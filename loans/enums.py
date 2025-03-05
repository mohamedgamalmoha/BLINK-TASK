from django.db import models
from django.utils.translation import gettext_lazy as _


class LoanStatus(models.IntegerChoices):
    PENDING = 0, _("Pending")
    APPROVED = 1, _("Approved")
    REJECTED = 2, _("Rejected")
    ACTIVE = 3, _("Active")
    COMPLETED = 4, _("Completed")
