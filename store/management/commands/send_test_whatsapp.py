from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from store.whatsapp import send_whatsapp


class Command(BaseCommand):
    help = "Send a real WhatsApp test message via Twilio to verify sandbox connectivity."

    def add_arguments(self, parser):
        parser.add_argument('to_number', help='Destination number, e.g. +15624409657')

    def handle(self, *args, **options):
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise CommandError('TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN are not set in the environment.')

        to_number = options['to_number']
        self.stdout.write(f"Account SID: {settings.TWILIO_ACCOUNT_SID[:6]}...")
        self.stdout.write(f"From: {settings.TWILIO_WHATSAPP_FROM}")
        self.stdout.write(f"To: whatsapp:{to_number}")

        send_whatsapp(to_number, "Frutería Elí: this is a test message to verify Twilio WhatsApp sandbox connectivity.")

        self.stdout.write(self.style.SUCCESS('Done — check logs above for sid/status or error details.'))
