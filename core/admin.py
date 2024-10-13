from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Room, Channel, UserProfile  # Import other models as needed
from django.contrib.admin import SimpleListFilter

# Check if User is registered before unregistering
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass  # User is not registered, so no need to unregister

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'owner_uuid', 'category', 'active')
    list_filter = ('owner_uuid', 'category', 'active')

# Register the User model again using UserAdmin
admin.site.register(User, UserAdmin)

class RoomFilter(SimpleListFilter):
    title = 'Room'
    parameter_name = 'room_uuid'

    def lookups(self, request, model_admin):
        rooms = Room.objects.all()
        return [(room.owner_uuid, room.name) for room in rooms]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room_uuid=self.value())
        return queryset

# Register the UserProfile model in the admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'uuid']  # Customize the columns shown in the admin
    search_fields = ['user__username', 'user__email']  # Enable searching by username or email

# Register the Room model
admin.site.register(Room, RoomAdmin)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['id',  'relative_id', 'get_room_name', 'name', 'get_owner_username', 'created_at']
    list_filter = [RoomFilter]

    # Custom method to display the room name based on its UUID
    def get_room_name(self, obj):
        try:
            room = Room.objects.get(id=obj.room_uuid)  # Fetch the room based on the UUID
            return room.name
        except Room.DoesNotExist:
            return "Room Not Found"
    get_room_name.short_description = 'Room'

    # Custom method to display the owner's username based on their UUID
    def get_owner_username(self, obj):
        try:
            user = User.objects.get(userprofile__uuid=obj.owner_uuid)  # Fetch user by UUID from UserProfile
            return user.username
        except User.DoesNotExist:
            return "User Not Found"
    get_owner_username.short_description = 'Owner'

# Register the Channel model
admin.site.register(Channel, ChannelAdmin)
