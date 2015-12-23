from django.utils.log import getLogger
from sis_provisioner.management.commands import SISProvisionerCommand
from restclients.exceptions import DataFailureException
from astra.loader import Accounts


class Command(SISProvisionerCommand):
    help = "Load Canvas Accounts"

    def handle(self, *args, **options):
        try:
            Accounts().load_all_accounts()
            self.update_job()
        except DataFailureException as err:
            getLogger(__name__).error('REST ERROR: %s\nAborting.' % err)
