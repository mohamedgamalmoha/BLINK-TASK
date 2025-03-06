from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from accounts.enums import UserRole
from accounts.managers import CustomUserManager, PersonnelUserManager, ProviderUserManager, CustomerUserManager


class User(AbstractUser):
    base_role = UserRole.LOAN_CUSTOMER

    role = models.PositiveSmallIntegerField(choices=UserRole.choices, verbose_name=_('Role'))

    REQUIRED_FIELDS = ['email', 'role']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('date_joined', )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


class PersonnelUser(User):
    base_role = UserRole.LOAN_PERSONNEL

    objects = PersonnelUserManager()

    class Meta:
        proxy = True


class ProviderUser(User):
    base_role = UserRole.LOAN_PROVIDER

    objects = ProviderUserManager()

    class Meta:
        proxy = True


class CustomerUser(User):
    base_role = UserRole.LOAN_CUSTOMER

    objects = CustomerUserManager()

    class Meta:
        proxy = True
