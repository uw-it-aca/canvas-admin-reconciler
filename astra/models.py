from django.db import models


class Admin(models.Model):
    """ Represents the provisioned state of an administrative user.
    """
    net_id = models.CharField(max_length=20)
    reg_id = models.CharField(max_length=32)
    role = models.CharField(max_length=32)
    account_id = models.CharField(max_length=128)
    canvas_id = models.IntegerField()
    added_date = models.DateTimeField(auto_now_add=True)
    provisioned_date = models.DateTimeField(null=True)
    deleted_date = models.DateTimeField(null=True)
    is_deleted = models.NullBooleanField()
    queue_id = models.CharField(max_length=30, null=True)


class Account(models.Model):
    """ Represents Canvas Accounts
    """
    ROOT_TYPE = 'root'
    SDB_TYPE = 'sdb'
    ADHOC_TYPE = 'adhoc'
    TEST_TYPE = 'test'

    TYPE_CHOICES = (
        (SDB_TYPE, 'SDB'),
        (ADHOC_TYPE, 'Ad Hoc'),
        (ROOT_TYPE, 'Root'),
        (TEST_TYPE, 'Test')
    )

    canvas_id = models.IntegerField(unique=True)
    sis_id = models.CharField(max_length=128, unique=True, blank=True,
                              null=True)
    account_name = models.CharField(max_length=256)
    account_short_name = models.CharField(max_length=128)
    account_type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    added_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.NullBooleanField()
    is_blessed_for_course_request = models.NullBooleanField()
    queue_id = models.CharField(max_length=30, null=True)

    def is_root(self):
        return self.account_type == self.ROOT_TYPE

    def is_sdb(self):
        return self.account_type == self.SDB_TYPE

    def is_adhoc(self):
        return self.account_type == self.ADHOC_TYPE

    def is_test(self):
        return self.account_type == self.TEST_TYPE
