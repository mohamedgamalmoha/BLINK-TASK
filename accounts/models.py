from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .enums import UserRole
from .managers import CustomUserManager


class User(AbstractUser):
    base_role = UserRole.LOAN_CUSTOMER

    role = models.PositiveSmallIntegerField(choices=UserRole.choices)

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
