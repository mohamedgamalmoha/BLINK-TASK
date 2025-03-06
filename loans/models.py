from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models import PersonnelUser, ProviderUser, CustomerUser
from loans.enums import LoanStatus
from loans.managers import LoanFundManager, LoanManager, AmortizationScheduleManager


class BaseLoanType(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Minimum Amount'))
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Maximum Amount'))
    interest_rate = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ],
        verbose_name=_('Interest Rate')
    )
    min_duration_months = models.PositiveSmallIntegerField(verbose_name=_('Min Duration Months'))
    max_duration_months = models.PositiveIntegerField(verbose_name=_('Max Duration Months'))
    create_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Create At"))
    update_at = models.DateTimeField(auto_now=True, verbose_name=_("Update At"))

    class Meta:
        abstract = True


class LoanFundType(BaseLoanType):
    personnel = models.ForeignKey(
        PersonnelUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='loan_fund_types',
        verbose_name=_('Personnel User')
    )

    class Meta:
        verbose_name = _('Loan Fund Type')
        verbose_name_plural = _('Loan Fund Types')
        ordering = ('-create_at', '-update_at')


class LoanFund(models.Model):
    provider = models.ForeignKey(
        ProviderUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='loan_funds',
        verbose_name=_('Provider User')
    )
    loan_type = models.ForeignKey(LoanFundType, on_delete=models.SET_NULL, null=True, verbose_name=_('Loan Type'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Amount'))
    duration_months = models.PositiveIntegerField(null=True, verbose_name=_('Term Months'))
    create_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Create At"))
    update_at = models.DateTimeField(auto_now=True, verbose_name=_("Update At"))

    objects = LoanFundManager()

    class Meta:
        verbose_name = _('Loan Fund')
        verbose_name_plural = _('Loan Funds')
        ordering = ('-create_at', '-update_at')


class LoanType(BaseLoanType):
    personnel = models.ForeignKey(
        PersonnelUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='loan_types',
        verbose_name=_('Personnel User')
    )

    class Meta:
        verbose_name = _('Loan Type')
        verbose_name_plural = _('Loan Types')
        ordering = ('-create_at', '-update_at')


class Loan(models.Model):
    customer = models.ForeignKey(
        CustomerUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='loans',
        verbose_name=_('Personnel User')
    )
    loan_type = models.ForeignKey(LoanType, on_delete=models.SET_NULL, null=True, verbose_name=_('Loan Type'))
    status = models.PositiveSmallIntegerField(
        choices=LoanStatus.choices,
        default=LoanStatus.PENDING,
        verbose_name=_('Status User')
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    duration_months = models.PositiveIntegerField(verbose_name=_('Term Months'))
    start_at = models.DateField(null=True, blank=True,  verbose_name=_('Start At'))
    create_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Create At"))
    update_at = models.DateTimeField(auto_now=True, verbose_name=_("Update At"))

    objects = LoanManager()

    class Meta:
        verbose_name = _('Loan')
        verbose_name_plural = _('Loan')
        ordering = ('-create_at', '-update_at')


class AmortizationSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True, related_name='loans', verbose_name=_("Loan"))

    principal_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Principal Amount"))
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Interest Amount"))
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total Payment"))
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Remaining Balance"))

    is_paid = models.BooleanField(default=False, verbose_name=_('Is Paid'))
    payment_number = models.CharField(max_length=20, verbose_name=_("Payment Number"))
    payment_date = models.DateField(verbose_name=_("Payment Date"))

    create_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Create At"))
    update_at = models.DateTimeField(auto_now=True, verbose_name=_("Update At"))

    objects = AmortizationScheduleManager()

    class Meta:
        verbose_name = _('Amortization Schedule')
        verbose_name_plural = _('Amortization Schedules')
        ordering = ('-create_at', '-update_at')
