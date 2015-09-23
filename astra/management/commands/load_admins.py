from django.core.management.base import BaseCommand, CommandError
from astra.loader import Loader


class Command(BaseCommand):
    help = "Loads admins for provisioning"

    def handle(self, *args, **options):
        loader = Loader()
        loader.load_all_admins()

