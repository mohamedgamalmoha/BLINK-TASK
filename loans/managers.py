from django.db import models

from loans.enums import LoanStatus


class LoanFundManager(models.Manager):

    def get_total_fund_amount(self):
        return self.get_queryset().aggregate(
            total_fund=models.Sum('amount')
        )


class LoanManager(models.Manager):

    def get_total_loan_amount(self):
        return self.get_queryset().aggregate(
            total_loan=models.Sum('amount')
        )

    def get_user_active_loans(self, customer):
        return self.get_queryset().filter(
            customer=customer
        ).exclude(
            models.Q(status=LoanStatus.REJECTED) |
            models.Q(status=LoanStatus.COMPLETED)
        )


class AmortizationScheduleManager(models.Manager):

    def get_unpaid_schedules(self, customer):
        return self.get_queryset().filter(
            models.Q(loan__customer=customer) &
            models.Q(is_paid=False)
        ).exclude(
            models.Q(loan__status=self.model.LoanStatus.REJECTED) &
            models.Q(loan__status=self.model.LoanStatus.COMPLETED)
        )

    def get_previous_unpaid_schedules(self, loan_id, payment_number):
        return self.get_queryset().filter(
            models.Q(load__id=loan_id) &
            models.Q(payment_number__lt=payment_number) &
            models.Q(is_paid=False)
        )
