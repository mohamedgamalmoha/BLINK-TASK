from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.factories import PersonnelUserFactory, ProviderUserFactory, CustomerUserFactory
from loans.enums import LoanStatus
from loans.models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule
from loans.factories import LoanFundTypeFactory, LoanFundFactory, LoanTypeFactory, LoanFactory


class LoanFundTypeSerializerTest(APITestCase):
    def setUp(self):
        self.personnel = PersonnelUserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.personnel)
        self.url = reverse('loans:fund_type-list')

    def test_min_amount_greater_than_max_amount_validation(self):
        """Test validation when min_amount > max_amount"""
        data = {
            'name': 'Test Fund Type',
            'min_amount': 5000,
            'max_amount': 1000,  # Intentionally less than min
            'interest_rate': 5.5,
            'min_duration_months': 6,
            'max_duration_months': 24
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Minimum amount cannot be greater than maximum amount', str(response.data))

    def test_min_duration_greater_than_max_duration_validation(self):
        """Test validation when min_duration > max_duration"""
        data = {
            'name': 'Test Fund Type',
            'min_amount': 1000,
            'max_amount': 5000,
            'interest_rate': 5.5,
            'min_duration_months': 24,  # Intentionally more than max
            'max_duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Minimum duration cannot be greater than maximum duration', str(response.data))

    def test_automatic_personnel_assignment(self):
        """Test that personnel is automatically assigned to the current user"""
        data = {
            'name': 'Test Fund Type',
            'min_amount': 1000,
            'max_amount': 5000,
            'interest_rate': 5.5,
            'min_duration_months': 6,
            'max_duration_months': 24
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoanFundType.objects.count(), 1)

        created_fund_type = LoanFundType.objects.first()
        self.assertEqual(created_fund_type.personnel, self.personnel)


class LoanFundSerializerTest(APITestCase):
    def setUp(self):
        self.provider = ProviderUserFactory()
        self.loan_fund_type = LoanFundTypeFactory(
            min_amount=1000,
            max_amount=10000
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.provider)
        self.url = reverse('loans:fund-list')

    def test_amount_validation_within_range(self):
        """Test validation when amount is within loan type range"""
        data = {
            'loan_type': self.loan_fund_type.id,
            'amount': 5000,
            'duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_amount_validation_below_min(self):
        """Test validation when amount is below loan type minimum"""
        data = {
            'loan_type': self.loan_fund_type.id,
            'amount': 500,  # Below min of 1000
            'duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Amount should not exceed loan type max amount, or below loan type min amount',
                      str(response.data))

    def test_amount_validation_above_max(self):
        """Test validation when amount is above loan type maximum"""
        data = {
            'loan_type': self.loan_fund_type.id,
            'amount': 15000,  # Above max of 10000
            'duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Amount should not exceed loan type max amount, or below loan type min amount',
                      str(response.data))

    def test_automatic_provider_assignment(self):
        """Test that provider is automatically assigned to the current user"""
        data = {
            'loan_type': self.loan_fund_type.id,
            'amount': 5000,
            'duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoanFund.objects.count(), 1)

        created_fund = LoanFund.objects.first()
        self.assertEqual(created_fund.provider, self.provider)


class LoanTypeSerializerTest(APITestCase):
    def setUp(self):
        self.personnel = PersonnelUserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.personnel)
        self.url = reverse('loans:type-list')

    def test_min_amount_greater_than_max_amount_validation(self):
        """Test validation when min_amount > max_amount"""
        data = {
            'name': 'Test Loan Type',
            'min_amount': 5000,
            'max_amount': 1000,  # Intentionally less than min
            'interest_rate': 5.5,
            'min_duration_months': 6,
            'max_duration_months': 24
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Minimum amount cannot be greater than maximum amount', str(response.data))

    def test_min_duration_greater_than_max_duration_validation(self):
        """Test validation when min_duration > max_duration"""
        data = {
            'name': 'Test Loan Type',
            'min_amount': 1000,
            'max_amount': 5000,
            'interest_rate': 5.5,
            'min_duration_months': 24,  # Intentionally more than max
            'max_duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Minimum duration cannot be greater than maximum duration', str(response.data))

    def test_automatic_personnel_assignment(self):
        """Test that personnel is automatically assigned to the current user"""
        data = {
            'name': 'Test Loan Type',
            'min_amount': 1000,
            'max_amount': 5000,
            'interest_rate': 5.5,
            'min_duration_months': 6,
            'max_duration_months': 24
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoanType.objects.count(), 1)

        created_loan_type = LoanType.objects.first()
        self.assertEqual(created_loan_type.personnel, self.personnel)


class LoanSerializerTest(APITestCase):
    def setUp(self):
        self.customer = CustomerUserFactory()
        self.loan_type = LoanTypeFactory(
            min_amount=1000,
            max_amount=10000,
            min_duration_months=6,
            max_duration_months=36
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.customer)
        self.url = reverse('loans:loan-list')

    @patch('loans.api.serializers.get_current_balance')
    def test_create_loan_success(self, mock_get_current_balance):
        """Test successful loan creation"""
        # Mock the balance to be sufficient
        mock_get_current_balance.return_value = Decimal('20000.00')

        data = {
            'loan_type': self.loan_type.id,
            'amount': 5000,
            'duration_months': 12,
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)

        created_loan = Loan.objects.first()
        self.assertEqual(created_loan.customer, self.customer)
        self.assertEqual(created_loan.status, LoanStatus.PENDING)

    def test_amount_validation_below_min(self):
        """Test validation when amount is below loan type minimum"""
        data = {
            'loan_type': self.loan_type.id,
            'amount': 500,  # Below min of 1000
            'duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Amount should not exceed loan type max amount, or below loan type min amount',
                      str(response.data))

    def test_amount_validation_above_max(self):
        """Test validation when amount is above loan type maximum"""
        data = {
            'loan_type': self.loan_type.id,
            'amount': 15000,  # Above max of 10000
            'duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Amount should not exceed loan type max amount, or below loan type min amount',
                      str(response.data))

    def test_duration_validation_below_min(self):
        """Test validation when duration is below loan type minimum"""
        data = {
            'loan_type': self.loan_type.id,
            'amount': 5000,
            'duration_months': 3  # Below min of 6
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Duration should not exceed loan type max duration, or below loan type min duration',
                      str(response.data))

    def test_duration_validation_above_max(self):
        """Test validation when duration is above loan type maximum"""
        data = {
            'loan_type': self.loan_type.id,
            'amount': 5000,
            'duration_months': 48  # Above max of 36
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Duration should not exceed loan type max duration, or below loan type min duration',
                      str(response.data))

    @patch('loans.api.serializers.AmortizationSchedule.objects.get_unpaid_schedules')
    @patch('loans.api.serializers.get_current_balance')
    def test_existing_unpaid_loan(self, mock_get_current_balance, mock_get_unpaid_schedules):
        """Test validation when customer has unpaid loans"""
        # Mock the balance to be sufficient
        mock_get_current_balance.return_value = Decimal('20000.00')

        # Mock unpaid schedules
        mock_unpaid = MagicMock()
        mock_unpaid.count.return_value = 1
        mock_get_unpaid_schedules.return_value = mock_unpaid

        data = {
            'loan_type': self.loan_type.id,
            'amount': 5000,
            'duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("existing loan that is not fully processed", str(response.data))

    @patch('loans.api.serializers.get_current_balance')
    def test_insufficient_balance(self, mock_get_current_balance):
        """Test validation when there's insufficient balance"""
        # Mock the balance to be insufficient
        mock_get_current_balance.return_value = Decimal('1000.00')

        data = {
            'loan_type': self.loan_type.id,
            'amount': 5000,  # More than available balance
            'duration_months': 12
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not enough balance", str(response.data))

    def test_update_non_pending_loan(self):
        """Test that only PENDING loans can be updated"""
        # Create a loan with status APPROVED
        loan = LoanFactory(
            customer=self.customer,
            loan_type=self.loan_type,
            amount=5000,
            duration_months=12,
            status=LoanStatus.APPROVED
        )

        url = reverse('loans:loan-detail', kwargs={'pk': loan.id})
        data = {
            'loan_type': self.loan_type.id,
            'amount': 6000,
            'duration_months': 18,
            'status': LoanStatus.APPROVED  # This should trigger validation error
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Updates are only allowed for loans with PENDING status", str(response.data))


class AmortizationScheduleViewSetTest(APITestCase):
    def setUp(self):
        self.customer = CustomerUserFactory()
        self.loan_type = LoanTypeFactory()

        # Create a loan and related amortization schedules
        self.loan = LoanFactory(
            customer=self.customer,
            loan_type=self.loan_type,
            status=LoanStatus.APPROVED
        )

        # Create three amortization schedules
        self.schedule1 = AmortizationSchedule.objects.create(
            loan=self.loan,
            payment_number='1',
            payment_date='2023-01-01',
            principal_amount=Decimal('100.00'),
            interest_amount=Decimal('10.00'),
            total_payment=Decimal('110.00'),
            remaining_balance=Decimal('900.00'),
            is_paid=False
        )

        self.schedule2 = AmortizationSchedule.objects.create(
            loan=self.loan,
            payment_number='2',
            payment_date='2023-02-01',
            principal_amount=Decimal('100.00'),
            interest_amount=Decimal('9.00'),
            total_payment=Decimal('109.00'),
            remaining_balance=Decimal('800.00'),
            is_paid=False
        )

        self.schedule3 = AmortizationSchedule.objects.create(
            loan=self.loan,
            payment_number='3',
            payment_date='2023-03-01',
            principal_amount=Decimal('100.00'),
            interest_amount=Decimal('8.00'),
            total_payment=Decimal('108.00'),
            remaining_balance=Decimal('700.00'),
            is_paid=False
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.customer)

    def test_pay_amortization(self):
        """Test successful payment of an amortization schedule"""
        url = reverse('loans:amortization-pay', kwargs={'pk': self.schedule1.id})
        data = {'transaction_id': 'TRX12345'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify amortization is marked as paid
        self.schedule1.refresh_from_db()
        self.assertTrue(self.schedule1.is_paid)

    def test_pay_already_paid_amortization(self):
        """Test attempt to pay an already paid amortization"""
        # First mark as paid
        self.schedule1.is_paid = True
        self.schedule1.transaction_id = 'TRX12345'
        self.schedule1.save()

        url = reverse('loans:amortization-pay', kwargs={'pk': self.schedule1.id})
        data = {'transaction_id': 'TRX67890'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You have already paid this", str(response.data))

    def test_duplicate_transaction_id(self):
        """Test validation of duplicate transaction IDs"""
        # First payment with transaction ID
        self.schedule1.is_paid = True
        self.schedule1.transaction_id = 'TRX12345'
        self.schedule1.save()

        # Try to use same transaction ID for second payment
        url = reverse('loans:amortization-pay', kwargs={'pk': self.schedule2.id})
        data = {'transaction_id': 'TRX12345'}

        with patch('loans.api.serializers.AmortizationSchedule.objects.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.count.return_value = 1
            mock_filter.return_value = mock_query

            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Transaction id is already exist", str(response.data))

    def test_pay_out_of_order(self):
        """Test validation when trying to pay schedules out of order"""
        # Try to pay schedule 2 before schedule 1
        url = reverse('loans:amortization-pay', kwargs={'pk': self.schedule2.id})
        data = {'transaction_id': 'TRX67890'}

        with patch('loans.api.serializers.AmortizationSchedule.objects.get_previous_unpaid_schedules') as mock_get:
            mock_query = MagicMock()
            mock_query.count.return_value = 1
            mock_get.return_value = mock_query

            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("You have an previous amortization that is not paid yet", str(response.data))


class PermissionsTest(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.personnel = PersonnelUserFactory()
        self.provider = ProviderUserFactory()
        self.customer = CustomerUserFactory()

        # Create test objects
        self.loan_fund_type = LoanFundTypeFactory(personnel=self.personnel)
        self.loan_type = LoanTypeFactory(personnel=self.personnel)
        self.loan_fund = LoanFundFactory(provider=self.provider, loan_type=self.loan_fund_type)
        self.loan = LoanFactory(customer=self.customer, loan_type=self.loan_type)

    def test_personnel_permissions(self):
        """Test that personnel can only access their allowed resources"""
        self.client.force_authenticate(user=self.personnel)

        # Should be able to access loan fund types
        response = self.client.get(reverse('loans:fund_type-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should be able to access loan types
        response = self.client.get(reverse('loans:type-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should not be able to access loans (customer resource)
        response = self.client.get(reverse('loans:loan-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_provider_permissions(self):
        """Test that providers can only access their allowed resources"""
        self.client.force_authenticate(user=self.provider)

        # Should be able to access loan funds
        response = self.client.get(reverse('loans:fund-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should be able to read loan fund types (read-only)
        response = self.client.get(reverse('loans:fund_type-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should not be able to create loan fund types
        data = {
            'name': 'Test Fund Type',
            'min_amount': 1000,
            'max_amount': 5000,
            'interest_rate': 5.5,
            'min_duration_months': 6,
            'max_duration_months': 24
        }
        response = self.client.post(reverse('loans:fund_type-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_permissions(self):
        """Test that customers can only access their allowed resources"""
        self.client.force_authenticate(user=self.customer)

        # Should be able to access own loans
        response = self.client.get(reverse('loans:loan-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should be able to access own amortization schedules
        # TODO: resolve this issue
        # response = self.client.get(reverse('loans:amortization-list'))
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should not be able to access loan funds (provider resource)
        response = self.client.get(reverse('loans:fund-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_object_level_permissions(self):
        """Test object-level permissions"""
        # Create another personnel user
        other_personnel = PersonnelUserFactory()
        self.client.force_authenticate(user=other_personnel)

        # Try to update loan fund type created by first personnel
        url = reverse('loans:fund_type-detail', kwargs={'pk': self.loan_fund_type.id})
        data = {'name': 'Updated Fund Type'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Create another customer
        other_customer = CustomerUserFactory()
        self.client.force_authenticate(user=other_customer)

        # Try to access loan created by first customer
        url = reverse('loans:loan-detail', kwargs={'pk': self.loan.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
