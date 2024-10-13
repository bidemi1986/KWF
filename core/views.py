# core/views.py
from django.http import HttpResponse
from rest_framework import viewsets, status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate  # Import authenticate for login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token  # Import Token for login
from .models import Room, Channel, UserProfile  # Import UserProfile
from .serializers import RoomSerializer, ChannelSerializer, UserSerializer, UserProfileSerializer, UserRegistrationSerializer  # Import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.conf import settings
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
# from jwt.exceptions import InvalidKeyError  # Ensure correct import


def home(request):
    return HttpResponse("Welcome to the Study Rooms API")


class RoomViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    # Custom action to fetch all public rooms
    @action(detail=False, methods=['get'], url_path='public')
    def public_rooms(self, request):
        public_rooms = Room.objects.filter(visibility='public')
        serializer = self.get_serializer(public_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Custom action to fetch rooms belonging to a specific user by user ID
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_rooms(self, request, user_id=None):
        try:
            user = User.objects.get(id=user_id)
            rooms = Room.objects.filter(owner_uuid=user.userprofile.uuid) | Room.objects.filter(members_uuids__contains=[str(user.userprofile.uuid)])
            serializer = self.get_serializer(rooms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

    # Custom action to fetch channels by room UUID
    @action(detail=False, methods=['get'], url_path='room/(?P<room_uuid>[^/.]+)')
    def room_channels(self, request, room_uuid=None):
        try:
            channels = Channel.objects.filter(room_uuid=room_uuid)
            serializer = self.get_serializer(channels, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

 

def send_mailerlite_email(subject, body, recipient_email):
    url = "https://api.mailerlite.com/api/v2/campaigns/send"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.MAILERLITE_API_KEY}'
    }
    data = {
        "subject": subject,
        "content": body,
        "recipients": [
            {
                "email": recipient_email
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        print(f"Failed to send email: {response.text}")
        return False
    
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)

        # Validate the request data
        if serializer.is_valid():
            try:
                # Save the user
                user = serializer.save()

                # Prepare the email content
                subject = "Welcome to Read Rocket!"
                body = f"Hello {user.username},\n\nThank you for registering with us!"
                recipient_email = user.email

                # Optionally send confirmation email via MailerLite (commented for now)
                # email_sent = send_mailerlite_email(subject, body, recipient_email)
                # if not email_sent:
                #     return Response({"message": "User created successfully but failed to send confirmation email."},
                #                     status=status.HTTP_201_CREATED)

                # Ensure this response is returned upon successful user creation
                return Response({"message": "User created successfully!","user":{"username": user.username, "email":user.email}}, status=status.HTTP_201_CREATED)

            except IntegrityError: 
                return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                # Handle unexpected exceptions
                return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Return errors if serializer validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username_or_email = request.data.get("username_or_email")
        password = request.data.get("password")

        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            username = username_or_email

        user = authenticate(username=username, password=password)
        
        if user:
            try:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'username': user.username
                }, status=status.HTTP_200_OK)
            # except InvalidKeyError as e:
            except :
                return Response({"error": f"Failed to generate token: "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # return Response({"error": f"Failed to generate token: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CheckUsernameView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access this endpoint

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)

        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"available": False, "message": "Username already taken"}, status=status.HTTP_200_OK)
        else:
            return Response({"available": True, "message": "Username is available"}, status=status.HTTP_200_OK)
        
 

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'register': reverse('register', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'profile': reverse('profile', request=request, format=format),
        'token': reverse('token_obtain_pair', request=request, format=format),
        'token-refresh': reverse('token_refresh', request=request, format=format),
        'token-verify': reverse('token_verify', request=request, format=format),
    })