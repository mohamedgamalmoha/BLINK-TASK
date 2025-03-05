from django.db import models


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
