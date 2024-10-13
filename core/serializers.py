# core/serializers
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import  UserProfile
from django.db import IntegrityError
 

class UserProfileSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)  # Read-only since UUID is auto-generated

    class Meta:
        model = UserProfile
        fields = ['uuid']

        
class UserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(source='userprofile.uuid', read_only=True)  # Link to UserProfile UUID

    class Meta:
        model = User
        fields = ['id', 'uuid', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Remove nested userprofile data since we are only passing user fields
        profile_data = validated_data.pop('userprofile', None)
        
        # Create the user, then handle the password
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()

        # After saving the user, create a UserProfile instance linked to this user
        UserProfile.objects.create(user=user)

        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        
        # Only set password if it is present
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)  # Hash the password
        instance.save()

        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

     # Override the default validation to check if both passwords match
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def validate_email(self, value):
        # Check if the email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        try:
            validated_data.pop('confirm_password')
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email']
            )
            user.set_password(validated_data['password'])  # Hash the password
            user.save()

            # Create associated UserProfile only if it doesn't exist
            UserProfile.objects.get_or_create(user=user)

        except IntegrityError:
            raise serializers.ValidationError({"error": "User profile already exists."})
        
        return user
