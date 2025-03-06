from django.db import models

import factory

from accounts.enums import UserRole
from accounts.models import User, PersonnelUser, ProviderUser, CustomerUser


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    role = factory.Iterator([role.value for role in UserRole if role != UserRole.ADMIN])
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')

    @factory.lazy_attribute_sequence
    def username(self, n):
        max_pk = User.objects.aggregate(max_pk=models.Max('pk'))['max_pk'] or 0
        return f'user_{max(max_pk, n) + 1}'

    class Meta:
        model = User


class PersonnelUserFactory(UserFactory):
    role = UserRole.LOAN_PERSONNEL

    class Meta:
        model = PersonnelUser


class ProviderUserFactory(UserFactory):
    role = UserRole.LOAN_PROVIDER

    class Meta:
        model = ProviderUser


class CustomerUserFactory(UserFactory):
    role = UserRole.LOAN_CUSTOMER

    class Meta:
        model = CustomerUser
