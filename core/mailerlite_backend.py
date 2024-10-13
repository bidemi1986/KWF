# mailerlite_backend.py
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class MailerLiteEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for message in email_messages:
            self._send_mailerlite_message(message)

    def _send_mailerlite_message(self, message):
        url = 'https://connect.mailerlite.com/v2/campaigns/send'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.MAILERLITE_API_KEY}'
        }

        data = {
            "subject": message.subject,
            "content": message.body,
            "recipients": [
                {
                    "email": email
                } for email in message.to
            ]
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            print(f"Email sent to: {message.to}")
        else:
            print(f"Failed to send email to: {message.to}. Error: {response.text}")
