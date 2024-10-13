from django.core.management.base import BaseCommand
from core.models import Channel, Room
from django.utils import timezone
import uuid

class Command(BaseCommand):
    help = 'Updates all existing channels with a unique UUID and a relative ID based on their room.'

    def handle(self, *args, **kwargs):
        # Fetch all the rooms
        rooms = Room.objects.all()

        for room in rooms:
            # Fetch all channels for this room and update each one
            channels = Channel.objects.filter(room_uuid=room.id).order_by('created_at')

            for idx, channel in enumerate(channels, start=1):
                # Update the channel with a unique UUID and a relative_id based on its order in the room
                if not channel.uuid:  # Ensure we only set uuid if it's missing
                    channel.uuid = uuid.uuid4()

                channel.relative_id = idx  # Set the relative ID based on its order in the room
                channel.save()

                self.stdout.write(self.style.SUCCESS(
                    f'Updated channel "{channel.name}" in room "{room.name}" with UUID: {channel.uuid} and relative ID: {channel.relative_id}'
                ))

        self.stdout.write(self.style.SUCCESS("Successfully updated all channels."))
