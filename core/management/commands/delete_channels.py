from django.core.management.base import BaseCommand
from core.models import Channel

class Command(BaseCommand):
    help = 'Deletes all channels from the database.'

    def handle(self, *args, **kwargs):
        # Fetch all channel records
        channels = Channel.objects.all()

        if channels.exists():
            channels_count = channels.count()
            # Delete all channels
            channels.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {channels_count} channels from the database.'))
        else:
            self.stdout.write(self.style.WARNING('No channels found in the database.'))
