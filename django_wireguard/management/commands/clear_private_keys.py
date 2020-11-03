from django.core.management.base import BaseCommand

from django_wireguard.utils import purge_private_keys


class Command(BaseCommand):
    help = 'Purge Private Key information from all stored peers.'

    def handle(self, *args, **options):
        count = purge_private_keys()
        if count > 0:
            self.stderr.write(self.style.SUCCESS(f"Removed all {count} Private Keys from database."))
        else:
            self.stderr.write(self.style.NOTICE(f"No Private Key found in database."))
