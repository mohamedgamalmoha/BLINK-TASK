from datetime import date
from decimal import Decimal

from django.dispatch import receiver
from django.db.models.signals import post_save
from dateutil.relativedelta import relativedelta

from loans.enums import LoanStatus
from loans.models import Loan, AmortizationSchedule
from loans.utils import calculate_loan_monthly_payment


@receiver(post_save, sender=Loan)
def create_amortization_schedule(sender, instance, created, **kwargs):
    """
    Generate amortization schedule when loan is approved
    """
    # Exit if not approved or already has amortizations
    if instance.status != LoanStatus.APPROVED or instance.amortizations.exists():
        return

    # Exit if no loan type associated
    if not instance.loan_type:
        return

    # Calculate monthly payment components
    loan_amount = instance.amount
    annual_interest = Decimal(instance.loan_type.interest_rate) / 100
    monthly_interest_rate = annual_interest / 12
    total_periods = instance.duration_months

    # Monthly payment formula (annuity)
    monthly_payment = calculate_loan_monthly_payment(
        loan_amount=loan_amount,
        monthly_interest_rate=monthly_interest_rate,
        total_periods=total_periods
    )

    # Determine schedule start date
    start_date = instance.start_at or date.today()
    remaining_balance = loan_amount

    # Create amortization entries
    for period in range(1, total_periods + 1):
        interest = remaining_balance * monthly_interest_rate
        principal = monthly_payment - interest
        remaining_balance -= principal

        # Handle final payment rounding
        if period == total_periods:
            principal += remaining_balance
            remaining_balance = Decimal(0)

        AmortizationSchedule.objects.create(
            loan=instance,
            payment_number=str(period),
            payment_date=start_date + relativedelta(months=period-1),
            principal_amount=principal.quantize(Decimal('0.01')),
            interest_amount=interest.quantize(Decimal('0.01')),
            total_payment=monthly_payment.quantize(Decimal('0.01')),
            remaining_balance=remaining_balance.quantize(Decimal('0.01')),
            is_paid=False
        )


@receiver(post_save, sender=AmortizationSchedule)
def update_loan_status_on_payment(sender, instance, created, **kwargs):
    """
    Signal to automatically update loan status to CLOSED when all
    amortization schedules are marked as paid.
    """
    if created:
        return  # Only handle updates, not creations

    if instance.is_paid:
        loan = instance.loan

        # Check if all payments for this loan are completed
        unpaid_schedules = AmortizationSchedule.objects.filter(
            loan=loan,
            is_paid=False
        )

        # If no unpaid schedules remain, mark the loan as CLOSED
        if not unpaid_schedules.exists():
            loan.status = LoanStatus.COMPLETED
            loan.save()
