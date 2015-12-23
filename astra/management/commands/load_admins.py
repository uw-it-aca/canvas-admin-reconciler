from sis_provisioner.management.commands import SISProvisionerCommand
from astra.loader import Loader


class Command(SISProvisionerCommand):
    help = "Loads admins for provisioning"

    def handle(self, *args, **options):
        loader = Loader()
        loader.load_all_admins()
        self.update_job()

