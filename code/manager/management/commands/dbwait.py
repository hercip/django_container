import time

from django.db import connection
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command that waits for database to be available"""

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write('Waiting for database...')
        for _ in range(10):
            try:
                connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 2 seconds...')
                time.sleep(2)
