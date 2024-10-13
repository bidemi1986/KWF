from django.core.management.base import BaseCommand
from core.models import Room, Channel
from django.utils import timezone
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a default "intro" channel for each room that has no channels and updates room channel_ids and members_uuids'

    def handle(self, *args, **kwargs):
        rooms = Room.objects.all()

        for room in rooms:
            # Check if the room already has channels
            if not room.channel_ids:  # If channel_ids list is empty or None
                self.stdout.write(f'Room "{room.name}" has no channels. Creating default "intro" channel.')

                # Fetch the room owner by joining with UserProfile to get the UUID
                try:
                    owner_profile = room.owner_uuid  # owner_uuid directly corresponds to the room's owner
                    owner = User.objects.get(userprofile__uuid=owner_profile)  # Join UserProfile to fetch user via UUID

                    owner_uuid = str(owner.userprofile.uuid)  # Access UUID via UserProfile
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Owner with UUID {room.owner_uuid} does not exist. Skipping room "{room.name}".'))
                    continue

                # Create a new channel with the room's UUID and the owner's UUID
                new_channel = Channel.objects.create(
                    name="Intro",  # Default channel name
                    room_uuid=room.id,  # Set the room's UUID as the channel's room_uuid
                    created_at=timezone.now(),  # Set creation time
                    color="rgb(216, 210, 123)",  # Example color
                    owner_uuid=room.owner_uuid  # Set the channel's owner to the room's owner's UUID
                )

                # Add the owner UUID to the channel's members_uuids list
                new_channel.members_uuids.append(owner_uuid)  # Add owner's UUID
                new_channel.save()

                # Update room's channel_ids field with the new channel's integer ID
                room.channel_ids.append(new_channel.id)  # Use the default integer ID for channels
                room.save()

                # Ensure the owner UUID is added to the room's members_uuids list if it's not already there
                if owner_uuid not in room.members_uuids:
                    room.members_uuids.append(owner_uuid)
                    room.save()

                self.stdout.write(self.style.SUCCESS(f'Channel "Intro" created for room "{room.name}".'))
            else:
                self.stdout.write(f'Room "{room.name}" already has channels. Skipping.')

        self.stdout.write(self.style.SUCCESS("Finished processing rooms."))
