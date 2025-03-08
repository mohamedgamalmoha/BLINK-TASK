from django.utils.translation import gettext_lazy as _
from django.core import exceptions as django_exceptions
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from accounts.enums import UserRole
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('is_superuser', 'is_staff', 'groups', 'user_permissions')
        read_only_fields = ('is_active', 'last_login', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        request = self.context['request']

        if request.method in ('PUT', 'PATCH'):
            if data['role'] != self.instance.role:
                raise serializers.ValidationError(
                    _("Role cannot be changed after creation")
                )

        if data['role'] not in  (UserRole.LOAN_PROVIDER, UserRole.LOAN_CUSTOMER):
            raise serializers.ValidationError(
                _("Role should be Provider or Customer")
            )

        user = User(**data)
        password = data.get("password")
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"password": e}
            )

        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
