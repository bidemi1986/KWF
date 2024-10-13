from django.core.management.base import BaseCommand
from core.models import Room, Channel
from django.utils import timezone
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a default "intro" channel for each room that has no channels and updates room channel_ids with UUIDs and members_uuids'

    def handle(self, *args, **kwargs):
        rooms = Room.objects.all()

        for room in rooms:
            # Check if the room already has channels
            if room.channel_ids:  # If channel_ids list is not empty
                # Remove existing integer IDs (since they're no longer valid)
                room.channel_ids = []
                room.save()
                self.stdout.write(self.style.WARNING(f'Removed old integer channel IDs from room "{room.name}".'))

            # Fetch the room owner (User instance)
            try:
                owner = User.objects.get(userprofile__uuid=room.owner_uuid)  # Fetch the user via the UserProfile's UUID
                owner_uuid = str(owner.userprofile.uuid)  # Convert owner's UUID to string
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Owner with UUID {room.owner_uuid} does not exist. Skipping room "{room.name}".'))
                continue

            # Create a new channel with a UUID
            new_channel = Channel.objects.create(
                name="Intro",  # Default channel name
                room_uuid=room.id,  # Use the room's UUID (stored in the room's `id` field)
                created_at=timezone.now(),  # Set creation time
                color="rgb(216, 210, 123)",  # Example color
                owner_uuid=owner_uuid  # Set the channel's owner to the owner's UUID
            )

            # Add the owner UUID to the channel's members_uuids list
            new_channel.members_uuids.append(owner_uuid)  # Add owner's UUID to the members list
            new_channel.save()

            # Update room's channel_ids field with the new channel's UUID instead of integer ID
            room.channel_ids.append(str(new_channel.uuid))  # Use the new channel UUID
            room.save()

            # Ensure the owner UUID is added to the room's members_uuids list if it's not already there
            if owner_uuid not in room.members_uuids:
                room.members_uuids.append(owner_uuid)
                room.save()

            self.stdout.write(self.style.SUCCESS(f'Channel "Intro" created for room "{room.name}".'))

        self.stdout.write(self.style.SUCCESS("Finished processing rooms."))

