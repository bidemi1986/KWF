from django.core.management.base import BaseCommand
from core.models import Room
from django.contrib.auth.models import User
from datetime import datetime

class Command(BaseCommand):
    help = 'Populates the database with predefined study rooms'

    study_rooms = [
        { 
            "name": "Physics 101",
            "category": "Science",
            "recentMessage": "Can someone explain quantum entanglement?",
            "lastActive": "2023-06-15T10:30:00Z"
        },
        { 
            "name": "World History",
            "category": "History",
            "recentMessage": "Discussing the impact of the Industrial Revolution",
            "lastActive": "2023-06-15T09:45:00Z"
        },
        { 
            "name": "Calculus Study Group",
            "category": "Math",
            "recentMessage": "Working on integration by parts problems",
            "lastActive": "2023-06-14T14:20:00Z"
        },
        { 
            "name": "Literature Circle",
            "category": "English",
            "recentMessage": "Analyzing themes in '1984' by George Orwell",
            "lastActive": "2023-06-15T08:15:00Z"
        },
        { 
            "name": "Computer Science Fundamentals",
            "category": "Science",
            "recentMessage": "Discussing Big O notation and algorithm efficiency",
            "lastActive": "2023-06-15T10:05:00Z"
        },
        { 
            "name": "Art History",
            "category": "History",
            "recentMessage": "Exploring the Renaissance period",
            "lastActive": "2023-06-13T16:40:00Z"
        },
        { 
            "name": "Biology Study Group",
            "category": "Science",
            "recentMessage": "Reviewing cellular respiration processes",
            "lastActive": "2023-06-15T09:30:00Z"
        },
        { 
            "name": "Statistics for Data Science",
            "category": "Math",
            "recentMessage": "Discussing hypothesis testing methods",
            "lastActive": "2023-06-15T10:29:00Z"
        }
    ]

    def handle(self, *args, **kwargs):
        # Try to fetch the user with the username 'admin'
        try:
            owner = User.objects.get(username='admin')
            owner_uuid = str(owner.userprofile.uuid)  # Convert UUID to string
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User with username "admin" does not exist'))
            return

        # Loop through the predefined study rooms and create each room
        for room in self.study_rooms:
            try:
                room_obj = Room.objects.create(
                    name=room['name'],
                    description=room['category'],
                    latest_message=room['recentMessage'],
                    last_active=datetime.fromisoformat(room['lastActive'].replace("Z", "+00:00")),
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    active=True,
                    visibility='public',
                    category=room['category'],
                    owner_uuid=owner_uuid,  # Use string representation of UUID
                    members_uuids=[owner_uuid],  # Use string representation of UUID for members
                )

                self.stdout.write(self.style.SUCCESS(f'Room "{room["name"]}" created successfully.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating room "{room["name"]}": {e}'))
