from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.log import getLogger
from django.utils.timezone import utc
from astra.loader import ASTRA, Accounts
from astra.loader import ASTRAException
from astra.models import Admin, Account
from restclients.canvas.admins import Admins as CanvasAdmins
from restclients.canvas.accounts import Accounts as CanvasAccounts
from restclients.pws import PWS
from restclients.exceptions import DataFailureException
from restclients.util import retry
from sis_provisioner.management.commands import SISProvisionerCommand
from optparse import make_option
import datetime
import time


class AncillaryException(Exception):
    pass


class Command(SISProvisionerCommand):
    help = "Reconcile ASTRA / Canvas Administrators"

    option_list = BaseCommand.option_list + (
        make_option('-r', '--root-account', action='store', dest='root_account', type="string",
                    default=settings.RESTCLIENTS_CANVAS_ACCOUNT_ID,
                    help='reconcile sections at and below root account (default: %s)'
                    % settings.RESTCLIENTS_CANVAS_ACCOUNT_ID),
        make_option('-c', '--commit', action='store_true', dest='commit',
                    default=False, help='update Canvas with ASTRA admins and roles'),
        make_option('-a', '--astra-is-authoritative', action='store_true', dest='remove_non_astra',
                    default=False, help='Remove Canvas admins not found in ASTRA'),
        make_option('-o', '--override', action='store', dest='override_id',
                    default=0, help='Override blocked Canvas admins import of given process id'),
        )

    max_retry = 8
    sleep_interval = 5
    retry_status_codes = [408, 500, 502, 503, 504]

    def handle(self, *args, **options):
        self._options = options
        self._verbosity = int(options.get('verbosity'))
        self._canvas_admins = CanvasAdmins()
        self._canvas_accounts = CanvasAccounts()
        self._pws = PWS()
        self._accounts = Accounts()
        self._log = getLogger('astra')

        self._canvas_role_mapping = {}
        for role in settings.ASTRA_ROLE_MAPPING:
            self._canvas_role_mapping[settings.ASTRA_ROLE_MAPPING[role]] = role
        if not self._options.get('commit'):
            self._log.info('NOT commiting ASTRA admins.  Only logging what would change.')

        # Compare table to Canvas reality
        try:
            if self._verbosity > 0:
                self._log.info('building admin table from ASTRA...')

            ASTRA({ 'verbosity': self._verbosity }).load_all_admins({ 'override': self._options.get('override_id') })

            if self._verbosity > 0:
                self._log.info('building sub account list...')

            accounts = []
            root = options.get('root_account')
            root_account_id = root if self._canvas_accounts.valid_canvas_id(root) else self._canvas_accounts.sis_account_id(root)

            if self._verbosity > 1:
                self._log.info('get account for id: %s...' % root_account_id)

            root_canvas_admins = []

            account = self.get_account(root_account_id)
            sub_accounts = self.get_all_sub_accounts(root_account_id)

            accounts.append(account)
            accounts.extend(sub_accounts)
            for account in accounts:
                canvas_id = account.account_id
                self._shown_canvas_id = canvas_id
                account_model = self._accounts.load_account(account)

                # reconcile admins against Admin table
                if account_model.is_sdb():
                    self._shown_id = account.sis_account_id
                else:
                    self._shown_id = 'canvas_%s' % canvas_id

                astra_admins = Admin.objects.filter(canvas_id=canvas_id)
                canvas_admins = self.get_admins(canvas_id)

                if account_model.is_root():
                    root_canvas_admins = canvas_admins

                if self._verbosity > 0 and (len(astra_admins) or len(canvas_admins)):
                    self._log.info('%d ASTRA and %s Canvas admins in account %s (%s)' %
                                   (len(astra_admins), len(canvas_admins),
                                    account.name, account.account_id))

                for astra_admin in astra_admins:
                    user_role = {
                        'canvas_account_id': account.account_id,
                        'role': settings.ASTRA_ROLE_MAPPING[astra_admin.role],
                        'net_id': astra_admin.net_id
                    }

                    canvas_admin = None

                    for admin in canvas_admins:
                        if (user_role['net_id'] == admin.user.login_id and
                            user_role['role'] == admin.role):
                            canvas_admin = admin
                            canvas_admin.in_astra = True
                            break

                    if astra_admin.is_deleted:
                        if canvas_admin:
                            user_role['user_id'] = canvas_admin.user.user_id
                            self._remove_admin(**user_role)
                            try:
                                ancillary = settings.ANCILLARY_CANVAS_ROLES[astra_admin.role]
                                user_role['role'] = ancillary['canvas_role']
                                if ancillary['account'] == 'common':
                                    self._remove_admin(**user_role)
                                elif len(Admin.objects.filter(net_id=canvas_admin.user.login_id,
                                                              role=astra_admin.role,
                                                              is_deleted__isnull=True)) == 0:
                                    user_role['canvas_account_id'] = settings.RESTCLIENTS_CANVAS_ACCOUNT_ID
                                    self._remove_admin(**user_role)
                            except Admin.DoesNotExist: pass
                            except KeyError: pass

                            astra_admin.deleted_date = datetime.datetime.utcnow().replace(tzinfo=utc)
                            astra_admin.save()
                    elif not canvas_admin:
                        user_role['user_id'] = self._canvas_admins.sis_user_id(astra_admin.reg_id)
                        self._add_admin(**user_role)

                        if astra_admin.role in settings.ANCILLARY_CANVAS_ROLES:
                            ancillary = settings.ANCILLARY_CANVAS_ROLES[astra_admin.role]
                            user_role['role'] = ancillary['canvas_role']
                            if ancillary['account'] == 'root':
                                user_role['canvas_account_id'] = settings.RESTCLIENTS_CANVAS_ACCOUNT_ID

                            self._add_admin(**user_role)

                        astra_admin.provisioned_date = datetime.datetime.utcnow().replace(tzinfo=utc)
                        astra_admin.save()
                    else:
                        if self._verbosity > 0:
                            self._log.info('  %s already in Canvas as %s' % (astra_admin.net_id, astra_admin.role))

                        if astra_admin.role in settings.ANCILLARY_CANVAS_ROLES:
                            ancillary = settings.ANCILLARY_CANVAS_ROLES[astra_admin.role]
                            user_role['role'] = ancillary['canvas_role']
                            add_ancillary = True
                            if ancillary['account'] == 'root':
                                user_role['canvas_account_id'] = settings.RESTCLIENTS_CANVAS_ACCOUNT_ID
                                for root_canvas_admin in root_canvas_admins:
                                    if (astra_admin.net_id == root_canvas_admin.user.login_id
                                        and root_canvas_admin.role == user_role['role']):
                                        add_ancillary = False
                                        break
                            elif  ancillary['account'] == 'common':
                                for canvas_admin in canvas_admins:
                                    if (astra_admin.net_id == canvas_admin.user.login_id
                                        and canvas_admin.role == user_role['role']):
                                        add_ancillary = False
                                        break

                            if add_ancillary:
                                user_role['user_id'] = self._canvas_admins.sis_user_id(astra_admin.reg_id)
                                self._add_admin(**user_role)
                            elif self._verbosity > 0:
                                self._log.info('  %s ancillary role %s already in %s'
                                               % (user_role['net_id'],
                                                  user_role['role'],
                                                  user_role['canvas_account_id']))

                # remove unrecognized admins
                for canvas_admin in canvas_admins:
                    if (self._options['remove_non_astra']
                        and not (hasattr(canvas_admin, 'in_astra')
                                 and canvas_admin.in_astra)):
                        if self._is_ancillary(account, canvas_admin.role,
                                              canvas_admin.user.login_id, account_model.is_root()):
                            self._log.info('preserving ancillary role: %s as %s'
                                           % (canvas_admin.user.login_id,
                                              canvas_admin.role))

                            continue

                        try:
                            self._remove_admin(canvas_account_id=canvas_id,
                                               net_id=canvas_admin.user.login_id,
                                               user_id=canvas_admin.user.user_id,
                                               role=canvas_admin.role)
                        except DataFailureException as err:
                            if err.args[1] == 404:
                                self._log.info('Ancillary role NOT in Canvas: %s as %s'
                                               % (canvas_admin.user.login_id,
                                                  canvas_admin.role))
                            else:
                                raise

            if self._verbosity > 0:
                self._log.info('Done.')

        except ASTRAException, err:
            self._log.error('ASTRA ERROR: %s\nAborting.' % err)

        except DataFailureException, err:
            self._log.error('REST ERROR: %s\nAborting.' % err)

        self.update_job()

    @retry(DataFailureException, status_codes=[408, 500, 502, 503, 504],
           tries=max_retry, delay=sleep_interval)
    def get_admins(canvas_id):
        return self._canvas_admins.get_admins(canvas_id)

    @retry(DataFailureException, status_codes=[408, 500, 502, 503, 504],
           tries=max_retry, delay=sleep_interval)
    def get_account(root_account_id):
        return self._canvas_accounts.get_account(root_account_id)

    @retry(DataFailureException, status_codes=[408, 500, 502, 503, 504],
           tries=max_retry, delay=sleep_interval)
    def get_all_sub_accounts(root_account_id):
        return self._canvas_accounts.get_all_sub_accounts(root_account_id)

    def _retry_with_backoff(self, f):
        n = 0
        while True:
            try:
                return f()
            except DataFailureException, err:
                self._log.error('REST ERROR (%s): %s' % (err.status, err))
                if n < self._max_retry and err.status in [408, 500, 502, 503, 504]:
                    n += 1
                    delay = n * self._sleep_interval
                    self._log.error('Retry after %s seconds.' % delay)
                    time.sleep(delay)
                else:
                    self._log.error('Aborting.')
                    raise

    def _is_ancillary(self, account, canvas_role, canvas_login_id, is_root):
        ancillary = settings.ANCILLARY_CANVAS_ROLES
        for astra_role in ancillary.keys():
            if ancillary[astra_role]['canvas_role'] == canvas_role:
                if ancillary[astra_role]['account'] == 'root' and is_root:
                    if len(Admin.objects.filter(net_id=canvas_login_id,
                                                role=astra_role,
                                                is_deleted__isnull=True)) > 0:
                        return True
                elif ancillary[astra_role]['account'] == 'common':
                    try:
                        Admin.objects.get(account_id=account.account_id,
                                          net_id=canvas_login_id,
                                          role=astra_role,
                                          is_deleted__isnull=True)
                        return True
                    except Admin.DoesNotExist:
                        pass

        return False

    def _add_admin(self, **kwargs):
        prefix = 'WOULD ADD'

        if self._options.get('commit'):
            prefix = 'ADDING'
            self._canvas_admins.create_admin(kwargs['canvas_account_id'],
                                             kwargs['user_id'],
                                             kwargs['role'])

        self._record('  %s: %s as %s' % (prefix, kwargs['net_id'], kwargs['role']))

    def _remove_admin(self, **kwargs):
        action = 'WOULD DELETE'

        if kwargs['net_id'] in getattr(settings, 'CANVAS_SERVICE_USER_ACCOUNTS', []):
            action = 'SERVICE USER'
        elif self._options.get('commit'):
            action = 'DELETING'
            try:
                self._canvas_admins.delete_admin(kwargs['canvas_account_id'],
                                                 kwargs['user_id'],
                                                 kwargs['role'])
            except DataFailureException, err:
                if err.status == 404:  # Non-personal regid?
                    action = "ALREADY DELETED"
                else:
                    raise

        self._record('  %s: %s (%s) as %s' % (action, kwargs['net_id'],
                                              kwargs['user_id'], kwargs['role']))

    def _record(self, msg):
        if self._shown_id:
            self._log.info('reconciling %s (%s)' % (self._shown_id, self._shown_canvas_id))
            self._shown_id = None

        self._log.info(msg)
