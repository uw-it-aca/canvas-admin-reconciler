from django.core.management.base import BaseCommand
from django.utils.log import getLogger
from restclients.exceptions import DataFailureException
from astra.loader import Accounts


class Command(BaseCommand):
    help = "Load Canvas Accounts"

    def handle(self, *args, **options):
        try:
            Accounts().load_all_accounts()
        except DataFailureException, err:
            getLogger(__name__).error('REST ERROR: %s\nAborting.' % err)
