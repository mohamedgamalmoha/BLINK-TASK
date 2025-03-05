from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.IntegerChoices):
    ADMIN = 0, _("Admin")
    LOAN_PERSONNEL = 1, _('Bank Personnel')
    LOAN_PROVIDER = 2, _('Loan Provider')
    LOAN_CUSTOMER = 3, _('Loan Customer')
