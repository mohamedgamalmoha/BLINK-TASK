from rest_framework import serializers

from loans.models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule


class LoanFundTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanFundType
        exclude = ()
        readonly_fields = ('create_at', 'update_at')


class LoanFundSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanFund
        exclude = ()
        readonly_fields = ('create_at', 'update_at')


class LoanTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanType
        exclude = ()
        readonly_fields = ('create_at', 'update_at')


class LoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        exclude = ()
        readonly_fields = ('create_at', 'update_at')


class AmortizationScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AmortizationSchedule
        exclude = ()
        readonly_fields = ('create_at', 'update_at')
