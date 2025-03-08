from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import date

from accounts.factories import CustomerUserFactory, PersonnelUserFactory
from loans.enums import LoanStatus
from loans.factories import LoanTypeFactory, LoanFundTypeFactory, LoanFundFactory, LoanFactory
from loans.models import Loan, AmortizationSchedule
from loans.utils import get_current_balance, calculate_loan_monthly_payment
from loans.signals import create_amortization_schedule, update_loan_status_on_payment


class LoanUtilsTest(TestCase):
    def setUp(self):
        # Create loan funds
        self.personnel = PersonnelUserFactory()
        self.loan_fund_type = LoanFundTypeFactory(personnel=self.personnel)

        self.fund1 = LoanFundFactory(
            loan_type=self.loan_fund_type,
            amount=Decimal('5000.00')
        )

        self.fund2 = LoanFundFactory(
            loan_type=self.loan_fund_type,
            amount=Decimal('10000.00')
        )

        # Create loan type and loans
        self.loan_type = LoanTypeFactory(personnel=self.personnel)
        self.customer = CustomerUserFactory()

        self.loan1 = LoanFactory(
            customer=self.customer,
            loan_type=self.loan_type,
            amount=Decimal('3000.00')
        )

        self.loan2 = LoanFactory(
            customer=self.customer,
            loan_type=self.loan_type,
            amount=Decimal('2000.00')
        )

    def test_get_current_balance(self):
        """Test get_current_balance utility function"""
        # Total funds: 15000, Total loans: 5000, Expected balance: 10000
        balance = get_current_balance()
        self.assertEqual(balance, Decimal('10000.00'))

        # Add another loan
        LoanFactory(
            customer=self.customer,
            loan_type=self.loan_type,
            amount=Decimal('1000.00')
        )

        # Total funds: 15000, Total loans: 6000, Expected balance: 9000
        balance = get_current_balance()
        self.assertEqual(balance, Decimal('9000.00'))

    def test_calculate_loan_monthly_payment(self):
        """Test calculate_loan_monthly_payment utility function"""
        # Test with known values
        # $10,000 loan at 12% annual interest for 60 months
        loan_amount = Decimal('10000.00')
        monthly_interest_rate = Decimal('0.01')  # 1% monthly (12% annually)
        total_periods = 60  # 5 years

        payment = calculate_loan_monthly_payment(
            loan_amount=loan_amount,
            monthly_interest_rate=monthly_interest_rate,
            total_periods=total_periods
        )

        # Expected payment around $222.44
        self.assertAlmostEqual(payment, Decimal('222.44'), delta=Decimal('0.01'))

        # Test with different values
        # $5,000 loan at 6% annual interest for 36 months
        loan_amount = Decimal('5000.00')
        monthly_interest_rate = Decimal('0.005')  # 0.5% monthly (6% annually)
        total_periods = 36  # 3 years

        payment = calculate_loan_monthly_payment(
            loan_amount=loan_amount,
            monthly_interest_rate=monthly_interest_rate,
            total_periods=total_periods
        )

        # Expected payment around $152.11
        self.assertAlmostEqual(payment, Decimal('152.11'), delta=Decimal('0.01'))


class LoanSignalsTest(TestCase):
    def setUp(self):
        self.personnel = PersonnelUserFactory()
        self.customer = CustomerUserFactory()

        self.loan_type = LoanTypeFactory(
            personnel=self.personnel,
            interest_rate=12.0  # 12% annual interest
        )

        # Create a loan with APPROVED status to trigger amortization creation
        self.loan = LoanFactory(
            customer=self.customer,
            loan_type=self.loan_type,
            amount=Decimal('10000.00'),
            duration_months=12,
            status=LoanStatus.PENDING,
            start_at=date.today()
        )

    def test_create_amortization_schedule_signal(self):
        """Test that amortization schedules are created when loan is approved"""
        # Initially no amortization schedules
        self.assertEqual(AmortizationSchedule.objects.filter(loan=self.loan).count(), 0)

        # Update loan status to APPROVED to trigger signal
        self.loan.status = LoanStatus.APPROVED
        self.loan.save()

        # Check if amortization schedules were created
        schedules = AmortizationSchedule.objects.filter(loan=self.loan)
        self.assertEqual(schedules.count(), self.loan.duration_months)

        # Check if the schedules have the correct values
        first_schedule = schedules.order_by('payment_number').first()
        self.assertEqual(first_schedule.payment_number, '1')
        self.assertFalse(first_schedule.is_paid)

        # Principal should equal loan amount
        total_principal = sum(schedule.principal_amount for schedule in schedules)
        self.assertAlmostEqual(total_principal, Decimal('10000.00'), delta=Decimal('0.01'))

    def test_update_loan_status_on_payment_signal(self):
        """Test that loan status is updated when all amortizations are paid"""
        # First approve the loan to create amortization schedules
        self.loan.status = LoanStatus.APPROVED
        self.loan.save()

        # Get all schedules
        schedules = AmortizationSchedule.objects.filter(loan=self.loan).order_by('payment_number')

        # Mark all but the last schedule as paid
        for schedule in schedules:
            schedule.is_paid = True
            schedule.transaction_id = f"TRX{schedule.payment_number}"
            schedule.save()

        # Loan status should still be APPROVED
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.status, LoanStatus.COMPLETED)
