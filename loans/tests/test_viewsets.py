import random
from decimal import Decimal
from datetime import date

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from accounts.factories import PersonnelUserFactory, ProviderUserFactory, CustomerUserFactory
from loans.enums import LoanStatus
from loans.models import LoanFundType, LoanFund, LoanType, Loan
from loans.factories import LoanFundTypeFactory, LoanFundFactory, LoanTypeFactory, LoanFactory


class LoanFundTypeViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.personnel_user = PersonnelUserFactory()
        self.list_url = reverse('loans:fund_type-list')

        # Create a test fund type
        self.fund_type = LoanFundTypeFactory(personnel=self.personnel_user)
        self.detail_url = reverse('loans:fund_type-detail', kwargs={'pk': self.fund_type.pk})
        self.me_url = reverse('loans:fund_type-me')

        # Authentication
        self.client.force_authenticate(user=self.personnel_user)

    def test_fund_type_list(self):
        """Test retrieving a list of loan fund types"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_fund_type_create(self):
        """Test creating a new loan fund type"""
        data = {
            'name': 'New Fund Type',
            'min_amount': '1000.00',
            'max_amount': '50000.00',
            'interest_rate': 5.5,
            'min_duration_months': 6,
            'max_duration_months': 36
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoanFundType.objects.count(), 2)
        self.assertEqual(LoanFundType.objects.latest('id').personnel, self.personnel_user)

    def test_fund_type_detail(self):
        """Test retrieving a single loan fund type"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.fund_type.name)

    def test_fund_type_update(self):
        """Test updating a loan fund type"""
        data = {
            'name': 'Updated Fund Type',
            'min_amount': self.fund_type.min_amount,
            'max_amount': self.fund_type.max_amount,
            'interest_rate': 7.5,
            'min_duration_months': self.fund_type.min_duration_months,
            'max_duration_months': self.fund_type.max_duration_months
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.fund_type.refresh_from_db()
        self.assertEqual(self.fund_type.name, 'Updated Fund Type')
        self.assertEqual(self.fund_type.interest_rate, 7.5)

    def test_fund_type_delete(self):
        """Test deleting a loan fund type"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LoanFundType.objects.count(), 0)

    def test_fund_type_me_action(self):
        """Test retrieving only fund types associated with the authenticated personnel"""
        # Create another fund type with a different personnel
        other_personnel = PersonnelUserFactory()
        LoanFundTypeFactory(personnel=other_personnel)

        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.fund_type.id)

    def test_validation_min_max_amount(self):
        """Test validation for min amount being greater than max amount"""
        data = {
            'name': 'Invalid Fund Type',
            'min_amount': '10000.00',
            'max_amount': '5000.00',  # Lower than min_amount
            'interest_rate': 5.5,
            'min_duration_months': 6,
            'max_duration_months': 36
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Minimum amount cannot be greater than maximum amount', str(response.data))

    def test_validation_min_max_duration(self):
        """Test validation for min duration being greater than max duration"""
        data = {
            'name': 'Invalid Fund Type',
            'min_amount': '1000.00',
            'max_amount': '50000.00',
            'interest_rate': 5.5,
            'min_duration_months': 36,  # Greater than max_duration_months
            'max_duration_months': 12
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Minimum duration cannot be greater than maximum duration', str(response.data))


class LoanTypeViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.personnel_user = PersonnelUserFactory()
        self.list_url = reverse('loans:type-list')

        # Create a test loan type
        self.loan_type = LoanTypeFactory(personnel=self.personnel_user)
        self.detail_url = reverse('loans:type-detail', kwargs={'pk': self.loan_type.pk})
        self.me_url = reverse('loans:type-me')

        # Authentication
        self.client.force_authenticate(user=self.personnel_user)

    def test_loan_type_list(self):
        """Test retrieving a list of loan types"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_loan_type_create(self):
        """Test creating a new loan type"""
        data = {
            'name': 'New Loan Type',
            'min_amount': '500.00',
            'max_amount': '10000.00',
            'interest_rate': 8.5,
            'min_duration_months': 3,
            'max_duration_months': 24
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoanType.objects.count(), 2)
        self.assertEqual(LoanType.objects.latest('id').personnel, self.personnel_user)

    def test_loan_type_detail(self):
        """Test retrieving a single loan type"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.loan_type.name)

    def test_loan_type_update(self):
        """Test updating a loan type"""
        data = {
            'name': 'Updated Loan Type',
            'min_amount': self.loan_type.min_amount,
            'max_amount': self.loan_type.max_amount,
            'interest_rate': 9.5,
            'min_duration_months': self.loan_type.min_duration_months,
            'max_duration_months': self.loan_type.max_duration_months
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan_type.refresh_from_db()
        self.assertEqual(self.loan_type.name, 'Updated Loan Type')
        self.assertEqual(self.loan_type.interest_rate, 9.5)

    def test_loan_type_delete(self):
        """Test deleting a loan type"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LoanType.objects.count(), 0)

    def test_loan_type_me_action(self):
        """Test retrieving only loan types associated with the authenticated personnel"""
        # Create another loan type with a different personnel
        other_personnel = PersonnelUserFactory()
        LoanTypeFactory(personnel=other_personnel)

        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.loan_type.id)


class LoanFundViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider_user = ProviderUserFactory()
        self.personnel_user = PersonnelUserFactory()
        self.loan_fund_type = LoanFundTypeFactory(personnel=self.personnel_user)
        self.list_url = reverse('loans:fund-list')

        # Create a test loan fund
        self.loan_fund = LoanFundFactory(provider=self.provider_user, loan_type=self.loan_fund_type)
        self.detail_url = reverse('loans:fund-detail', kwargs={'pk': self.loan_fund.pk})

        # Authentication
        self.client.force_authenticate(user=self.provider_user)

    def test_loan_fund_list(self):
        """Test retrieving a list of loan funds"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_loan_fund_create(self):
        """Test creating a new loan fund"""
        data = {
            'loan_type': self.loan_fund_type.id,
            'amount': random.randint(
                int(self.loan_fund_type.min_amount) + 1,
                int(self.loan_fund_type.max_amount) - 1
            ),
            'duration_months': 24
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoanFund.objects.count(), 2)
        self.assertEqual(LoanFund.objects.latest('id').provider, self.provider_user)

    def test_loan_fund_detail(self):
        """Test retrieving a single loan fund"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['amount']), self.loan_fund.amount)

    def test_loan_fund_update(self):
        """Test updating a loan fund"""
        data = {
            'loan_type': self.loan_fund_type.id,
            'amount': '25000.00',
            'duration_months': self.loan_fund.duration_months
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan_fund.refresh_from_db()
        self.assertEqual(self.loan_fund.amount, Decimal('25000.00'))

    def test_loan_fund_delete(self):
        """Test deleting a loan fund"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LoanFund.objects.count(), 0)

    def test_loan_fund_validation(self):
        """Test validation for amount within min/max range of loan fund type"""
        # Set amount outside the range of the loan fund type
        data = {
            'loan_type': self.loan_fund_type.id,
            'amount': str(self.loan_fund_type.max_amount + Decimal('1000.00')),
            'duration_months': 24
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoanViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.customer_user = CustomerUserFactory()
        self.personnel_user = PersonnelUserFactory()

        # Create a loan type
        self.loan_type = LoanTypeFactory(
            personnel=self.personnel_user,
            min_amount=Decimal('1000.00'),
            max_amount=Decimal('50000.00'),
            min_duration_months=6,
            max_duration_months=60
        )

        # Create funds to ensure there's enough balance
        self.loan_fund_type = LoanFundTypeFactory(personnel=self.personnel_user)
        self.provider_user = ProviderUserFactory()
        LoanFundFactory(
            provider=self.provider_user,
            loan_type=self.loan_fund_type,
            amount=Decimal('100000.00')
        )

        # Set up URLs
        self.list_url = reverse('loans:loan-list')

        # Create a test loan
        self.loan = LoanFactory(
            customer=self.customer_user,
            loan_type=self.loan_type,
            amount=Decimal('10000.00'),
            duration_months=24,
            status=LoanStatus.PENDING
        )
        self.detail_url = reverse('loans:loan-detail', kwargs={'pk': self.loan.pk})

        # Authentication
        self.client.force_authenticate(user=self.customer_user)

    def test_loan_list(self):
        """Test retrieving a list of loans for the customer"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_loan_create(self):
        """Test creating a new loan application"""
        data = {
            'loan_type': self.loan_type.id,
            'amount': '5000.00',
            'duration_months': 12,
            'start_at': date.today().isoformat()
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 2)
        self.assertEqual(Loan.objects.latest('id').customer, self.customer_user)
        self.assertEqual(Loan.objects.latest('id').status, LoanStatus.PENDING)

    def test_loan_detail(self):
        """Test retrieving a single loan"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['amount']), self.loan.amount)

    def test_loan_update(self):
        """Test updating a loan in PENDING status"""
        data = {
            'loan_type': self.loan_type.id,
            'amount': '15000.00',
            'duration_months': self.loan.duration_months,
            'start_at': self.loan.start_at.isoformat() if self.loan.start_at else None
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.amount, Decimal('15000.00'))

    def test_loan_expand_amortization(self):
        """Test expanding amortizations in loan detail response"""
        # Change status to APPROVED and add amortization schedules
        self.loan.status = LoanStatus.APPROVED
        self.loan.save()

        # Manually trigger the signal (in test environment)
        from loans.signals import create_amortization_schedule
        create_amortization_schedule(sender=Loan, instance=self.loan, created=False)

        # Verify amortization schedules were created
        self.assertTrue(self.loan.amortizations.exists())

        # Test expand parameter
        url = f"{self.detail_url}?expand=amortizations"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('amortizations', response.data)
        self.assertTrue(len(response.data['amortizations']) > 0)

    def test_validation_amount_range(self):
        """Test validation for amount within min/max range of loan type"""
        # Test amount below min_amount
        data = {
            'loan_type': self.loan_type.id,
            'amount': str(self.loan_type.min_amount - Decimal('100.00')),
            'duration_months': 12,
            'start_at': date.today().isoformat()
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test amount above max_amount
        data['amount'] = str(self.loan_type.max_amount + Decimal('1000.00'))
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AmortizationScheduleViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.customer_user = CustomerUserFactory()
        self.personnel_user = PersonnelUserFactory()

        # Create a loan type
        self.loan_type = LoanTypeFactory(
            personnel=self.personnel_user,
            interest_rate=10.0
        )

        # Create a loan
        self.loan = LoanFactory(
            customer=self.customer_user,
            loan_type=self.loan_type,
            amount=Decimal('10000.00'),
            duration_months=12,
            status=LoanStatus.APPROVED,
            start_at=date.today()
        )

        # Manually create amortization schedules
        from loans.signals import create_amortization_schedule
        create_amortization_schedule(sender=Loan, instance=self.loan, created=False)

        # Get the first amortization schedule
        self.amortization = self.loan.amortizations.order_by('payment_number').first()
        self.list_url = reverse('loans:amortization-list')
        self.detail_url = reverse('loans:amortization-detail', kwargs={'pk': self.amortization.pk})
        self.pay_url = reverse('loans:amortization-pay', kwargs={'pk': self.amortization.pk})

        # Authentication
        self.client.force_authenticate(user=self.customer_user)

    def test_amortization_list(self):
        """Test retrieving a list of amortization schedules"""
        # TODO: resolve this
        # response = self.client.get(self.list_url)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_amortization_detail(self):
        """Test retrieving a single amortization schedule"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_number'], self.amortization.payment_number)

    def test_amortization_payment(self):
        """Test paying an amortization schedule"""
        data = {
            'transaction_id': 'TR123456789'
        }
        response = self.client.post(self.pay_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.amortization.refresh_from_db()
        self.assertTrue(self.amortization.is_paid)
        self.assertEqual(self.amortization.transaction_id, 'TR123456789')

    def test_amortization_already_paid(self):
        """Test attempting to pay an already paid amortization"""
        # First mark as paid
        self.amortization.is_paid = True
        self.amortization.transaction_id = 'TR123456789'
        self.amortization.save()

        # Try to pay again
        data = {
            'transaction_id': 'TR987654321'
        }
        response = self.client.post(self.pay_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_amortization_duplicate_transaction(self):
        """Test using duplicate transaction ID"""
        # Create a paid amortization with a transaction ID
        second_amortization = self.loan.amortizations.all()[1]
        second_amortization.is_paid = True
        second_amortization.transaction_id = 'TR123456789'
        second_amortization.save()

        # Try to use the same transaction ID for another payment
        data = {
            'transaction_id': 'TR123456789'
        }
        response = self.client.post(self.pay_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_loan_after_all_payments(self):
        """Test loan status changes to COMPLETED after all amortizations are paid"""
        # Pay all amortizations
        for i, amortization in enumerate(self.loan.amortizations.order_by('payment_number').all()):
            pay_url = reverse('loans:amortization-pay', kwargs={'pk': amortization.pk})
            data = {
                'transaction_id': f'TR{i + 1000}'
            }
            response = self.client.post(pay_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if loan status is updated to COMPLETED
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.status, LoanStatus.COMPLETED)
