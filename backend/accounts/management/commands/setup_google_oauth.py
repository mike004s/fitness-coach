"""
Management command: setup_google_oauth

Seeds the Google OAuth SocialApp entry in the database using credentials
from the .env file. Run this once after migrations:

    python manage.py setup_google_oauth
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from decouple import config


class Command(BaseCommand):
    help = 'Create or update the Google OAuth SocialApp from .env credentials'

    def handle(self, *args, **options):
        from allauth.socialaccount.models import SocialApp

        client_id = config('GOOGLE_CLIENT_ID', default='')
        secret = config('GOOGLE_CLIENT_SECRET', default='')

        if not client_id or client_id.startswith('your-'):
            self.stdout.write(self.style.WARNING(
                'GOOGLE_CLIENT_ID is not set in .env — skipping Google OAuth setup.\n'
                'Update .env with real credentials, then re-run this command.'
            ))
            return

        site, _ = Site.objects.get_or_create(
            id=1, defaults={'domain': 'localhost:8000', 'name': 'KINETIC'}
        )

        app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': secret,
            },
        )
        app.sites.add(site)

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action} Google OAuth SocialApp successfully.'
        ))
