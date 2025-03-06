from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_flex_fields import FlexFieldsModelSerializer

from loans.enums import LoanStatus
from loans.utils import get_current_balance
from loans.models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule


class LoanFundTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanFundType
        exclude = ()
        read_only_fields = ('personnel', 'create_at', 'update_at')

    def validate(self, data):
        # Ensure max amount is greater than min amount
        if data['min_amount'] > data['max_amount']:
            raise serializers.ValidationError(
                _("Minimum amount cannot be greater than maximum amount")
            )

        # Ensure max duration is greater than min duration
        if data['min_duration_months'] > data['max_duration_months']:
            raise serializers.ValidationError(
                _("Minimum duration cannot be greater than maximum duration")
            )
        return data


class LoanFundSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanFund
        exclude = ()
        read_only_fields = ('provider', 'create_at', 'update_at')

    def validate(self, data):
        # Validate loan amount against loan type min/max
        amount = data['amount']
        min_amount = data['loan_type'].min_amount
        max_amount = data['loan_type'].max_amount
        if not (max_amount >= amount >= min_amount):
            raise serializers.ValidationError(
                _("Amount should not exceed loan type max amount, or below loan type min amount")
            )
        return data


class LoanTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanType
        exclude = ()
        read_only_fields = ('personnel', 'create_at', 'update_at')

    def validate(self, data):
        # Ensure max amount is greater than min amount
        if data['min_amount'] > data['max_amount']:
            raise serializers.ValidationError(
                _("Minimum amount cannot be greater than maximum amount")
            )

        # Ensure max duration is greater than min duration
        if data['min_duration_months'] > data['max_duration_months']:
            raise serializers.ValidationError(
                _("Minimum duration cannot be greater than maximum duration")
            )
        return data


class LoanSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = Loan
        exclude = ()
        read_only_fields = ('customer', 'status',  'create_at', 'update_at')
        expandable_fields = {
            'amortizations': ('loans.api.AmortizationScheduleSerializer', {'many': True})
        }

    def validate(self, data):
        request = self.context['request']

        # For update operations (PUT/PATCH), only allow updates to loans with PENDING status
        if request.method in ('PUT', 'PATCH'):
            if data['status'] != LoanStatus.PENDING:
                raise PermissionDenied(
                    _("Updates are only allowed for loans with PENDING status.")
                )

        # Validate loan amount is within the range specified by the loan type
        amount = data['amount']
        min_amount = data['loan_type'].min_amount
        max_amount = data['loan_type'].max_amount
        if not (max_amount >= amount >= min_amount):
            raise serializers.ValidationError(
                _("Amount should not exceed loan type max amount, or below loan type min amount")
            )

        # Validate loan duration is within the range specified by the loan type
        duration = data['duration']
        min_duration = data['loan_type'].min_duration_months
        max_duration = data['loan_type'].max_duration_months
        if not (max_duration >= duration >= min_duration):
            raise serializers.ValidationError(
                _("Duration should not exceed loan type max duration, or below loan type min duration")
            )

        # Check if the customer has any unpaid loan schedules
        customer = request.user
        unpaid_schedules = AmortizationSchedule.objects.get_unpaid_schedules(customer=customer)
        if unpaid_schedules.count() > 0:
            raise serializers.ValidationError(
                _(f"Cannot create new loan. You have an existing loan that is not fully processed.")
            )

        # Verify that there's enough balance to cover the loan amount
        curr_balance = get_current_balance()
        if amount > curr_balance:
            raise serializers.ValidationError(
                _("Not enough balance, try again later or contact us")
            )
        return data


class AmortizationScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AmortizationSchedule
        exclude = ()
        read_only_fields = ('create_at', 'update_at')


class AmortizationPayment(serializers.ModelSerializer):

    class Meta:
        model = AmortizationSchedule
        fields = ('transaction_id', 'create_at', 'update_at')
        read_only_fields = ('create_at', 'update_at')

    def validate(self, data):
        # Check if there are any previous unpaid schedules
        instance = self.instance
        previous_unpaid_schedules = AmortizationSchedule.objects.get_previous_unpaid_schedules(
            loan_id=instance.loan.id,
            payment_number=instance.payment_number
        )
        if previous_unpaid_schedules.count() > 0:
            raise serializers.ValidationError(
                _(f"Cannot pay this amortization. You have an previous amortization that is not paid yet.")
            )

        # Check if the current instance is already marked as paid
        if instance.is_paid is True:
            raise PermissionDenied(
                _("You have already paid this")
            )
        return data
