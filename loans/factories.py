import random
from decimal import Decimal

import factory.fuzzy
from faker import Faker

from accounts.factories import PersonnelUserFactory, ProviderUserFactory, CustomerUserFactory
from loans.enums import LoanStatus
from loans.models import LoanFundType, LoanFund, LoanType, Loan


fake = Faker()


class LoanFundTypeFactory(factory.django.DjangoModelFactory):
    name = factory.LazyFunction(lambda: f"Fund {fake.word().capitalize()}")
    min_amount = factory.LazyFunction(lambda: Decimal(str(random.randint(1000, 5000))))
    max_amount = factory.LazyFunction(lambda: Decimal(str(random.randint(10000, 100000))))
    interest_rate = factory.LazyFunction(lambda: round(random.uniform(1.0, 15.0), 2))
    min_duration_months = factory.LazyFunction(lambda: random.randint(3, 12))
    max_duration_months = factory.LazyFunction(lambda: random.randint(24, 60))
    personnel = factory.SubFactory(PersonnelUserFactory)

    class Meta:
        model = LoanFundType


class LoanFundFactory(factory.django.DjangoModelFactory):
    provider = factory.SubFactory(ProviderUserFactory)
    loan_type = factory.SubFactory(LoanFundTypeFactory)
    amount = factory.LazyFunction(lambda: Decimal(str(random.randint(5000, 50000))))
    duration_months = factory.LazyFunction(lambda: random.randint(12, 48))

    class Meta:
        model = LoanFund


class LoanTypeFactory(factory.django.DjangoModelFactory):
    name = factory.LazyFunction(lambda: f"Loan {fake.word().capitalize()}")
    min_amount = factory.LazyFunction(lambda: Decimal(str(random.randint(500, 2000))))
    max_amount = factory.LazyFunction(lambda: Decimal(str(random.randint(5000, 50000))))
    interest_rate = factory.LazyFunction(lambda: round(random.uniform(3.0, 20.0), 2))
    min_duration_months = factory.LazyFunction(lambda: random.randint(3, 12))
    max_duration_months = factory.LazyFunction(lambda: random.randint(24, 60))
    personnel = factory.SubFactory(PersonnelUserFactory)

    class Meta:
        model = LoanType


class LoanFactory(factory.django.DjangoModelFactory):
    customer = factory.SubFactory(CustomerUserFactory)
    loan_type = factory.SubFactory(LoanTypeFactory)
    status = LoanStatus.PENDING
    amount = factory.LazyFunction(lambda: Decimal(str(random.randint(1000, 30000))))
    duration_months = factory.LazyFunction(lambda: random.randint(6, 36))
    start_at = factory.LazyFunction(lambda: fake.date_between(start_date='-1y', end_date='today'))

    class Meta:
        model = Loan
