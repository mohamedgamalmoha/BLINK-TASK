from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.enums import UserRole
from loans.models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule


class BaseUserRolePermission(BasePermission):
    allow_readonly: bool = True
    user_role: UserRole = None

    def is_safe_request(self, request) -> bool:
        return bool(
            self.allow_readonly and
            request.method in SAFE_METHODS
        )

    def has_permission(self, request, view) -> bool:
        return bool(
            self.is_safe_request(request=request) or
            (request.user.is_authenticated and request.user.role == self.user_role)
        )

    def has_object_permission(self, request, view, obj) -> bool:
        if self.is_safe_request(request=request):
            return True

        user = request.user

        # Personnel Permission
        if isinstance(obj, (LoanType, LoanFundType)):
            return obj.personnel == user

        # provider Permission
        if isinstance(obj, LoanFund):
            return obj.provider == user

        # customer Permission
        if isinstance(obj, Loan):
            return obj.customer == user
        if isinstance(obj, AmortizationSchedule):
            return obj.loan and obj.loan.customer == user

        return False


class IsPersonnel(BaseUserRolePermission):
    user_role = UserRole.LOAN_PERSONNEL


class IsProvider(BaseUserRolePermission):
    allow_readonly = False
    user_role = UserRole.LOAN_PROVIDER


class IsCustomer(BaseUserRolePermission):
    allow_readonly = False
    user_role = UserRole.LOAN_CUSTOMER
