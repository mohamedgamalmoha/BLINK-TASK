from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from accounts.factories import PersonnelUserFactory, ProviderUserFactory, CustomerUserFactory
from loans.factories import LoanFundTypeFactory, LoanFundFactory, LoanTypeFactory, LoanFactory


class LoanPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users with different roles
        self.personnel_user = PersonnelUserFactory()
        self.provider_user = ProviderUserFactory()
        self.customer_user = CustomerUserFactory()

        # Create test data
        self.loan_fund_type = LoanFundTypeFactory(personnel=self.personnel_user)
        self.loan_fund = LoanFundFactory(
            provider=self.provider_user,
            loan_type=self.loan_fund_type
        )
        self.loan_type = LoanTypeFactory(personnel=self.personnel_user)
        self.loan = LoanFactory(
            customer=self.customer_user,
            loan_type=self.loan_type
        )

        # URLs
        self.fund_type_list_url = reverse('loans:fund_type-list')
        self.fund_type_detail_url = reverse('loans:fund_type-detail', kwargs={'pk': self.loan_fund_type.pk})

        self.fund_list_url = reverse('loans:fund-list')
        self.fund_detail_url = reverse('loans:fund-detail', kwargs={'pk': self.loan_fund.pk})

        self.type_list_url = reverse('loans:type-list')
        self.type_detail_url = reverse('loans:type-detail', kwargs={'pk': self.loan_type.pk})

        self.loan_list_url = reverse('loans:loan-list')
        self.loan_detail_url = reverse('loans:loan-detail', kwargs={'pk': self.loan.pk})

    def test_personnel_permissions(self):
        """Test that personnel users can access their resources but not others"""
        self.client.force_authenticate(user=self.personnel_user)

        # Should be able to access fund types and loan types
        response = self.client.get(self.fund_type_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.type_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should NOT be able to modify loan funds
        response = self.client.post(self.fund_list_url, {
            'loan_type': self.loan_fund_type.id,
            'amount': '10000.00',
            'duration_months': 24
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Should NOT be able to modify loans
        response = self.client.post(self.loan_list_url, {
            'loan_type': self.loan_type.id,
            'amount': '5000.00',
            'duration_months': 12
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_provider_permissions(self):
        """Test that provider users can access their resources but not others"""
        self.client.force_authenticate(user=self.provider_user)

        # Should be able to view loan fund types (read-only)
        response = self.client.get(self.fund_type_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should NOT be able to modify fund types
        response = self.client.post(self.fund_type_list_url, {
            'name': 'Test Fund Type',
            'min_amount': '1000.00',
            'max_amount': '50000.00',
            'interest_rate': 5.0,
            'min_duration_months': 6,
            'max_duration_months': 36
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Should be able to create and manage their own loan funds
        response = self.client.get(self.fund_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should NOT be able to access loans
        response = self.client.get(self.loan_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_permissions(self):
        """Test that customer users can access their resources but not others"""
        self.client.force_authenticate(user=self.customer_user)

        # Should be able to view loan types (read-only)
        response = self.client.get(self.type_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should NOT be able to modify loan types
        response = self.client.post(self.type_list_url, {
            'name': 'Test Loan Type',
            'min_amount': '500.00',
            'max_amount': '10000.00',
            'interest_rate': 8.0,
            'min_duration_months': 3,
            'max_duration_months': 24
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Should NOT be able to access loan funds
        response = self.client.post(self.fund_list_url, {
            'loan_type': self.loan_fund_type.id,
            'amount': '10000.00',
            'duration_months': 24
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Should be able to create and manage their own loans
        response = self.client.get(self.loan_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users can only access read-only endpoints"""
        self.client.force_authenticate(user=None)

        # Should be able to view loan fund types (read-only)
        response = self.client.get(self.fund_type_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should be able to view loan types (read-only)
        response = self.client.get(self.type_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should NOT be able to create loan fund types
        response = self.client.post(self.fund_type_list_url, {
            'name': 'Test Fund Type',
            'min_amount': '1000.00',
            'max_amount': '50000.00',
            'interest_rate': 5.0,
            'min_duration_months': 6,
            'max_duration_months': 36
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Should NOT be able to create loan funds
        response = self.client.post(self.fund_list_url, {
            'loan_type': self.loan_fund_type.id,
            'amount': '10000.00',
            'duration_months': 24
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Should NOT be able to create loans
        response = self.client.post(self.loan_list_url, {
            'loan_type': self.loan_type.id,
            'amount': '5000.00',
            'duration_months': 12
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
