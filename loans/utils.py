from decimal import Decimal

from loans.models import LoanFund, Loan


def get_current_balance() -> Decimal:
    funds = LoanFund.objects.get_total_fund_amount()
    loans = Loan.objects.get_total_loan_amount()
    total_fund = funds['total_fund'] or 0
    total_loan = loans['total_loan'] or 0
    return total_fund - total_loan


def calculate_loan_monthly_payment(loan_amount, monthly_interest_rate, total_periods) -> Decimal:
    numerator =  (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** total_periods)
    denominator = ((1 + monthly_interest_rate) ** total_periods - 1)
    return numerator / denominator
