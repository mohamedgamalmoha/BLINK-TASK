from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import BasicAuthentication

from loans.api.permissions import IsPersonnel, IsProvider, IsCustomer
from loans.models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule
from loans.api.serializers import (LoanFundTypeSerializer, LoanFundSerializer, LoanTypeSerializer, LoanSerializer,
                                   AmortizationScheduleSerializer)


class LoanFundTypeViewSet(ModelViewSet):
    queryset = LoanFundType.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsPersonnel]
    serializer_class = LoanFundTypeSerializer


class LoanTypeViewSet(ModelViewSet):
    queryset = LoanType.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsPersonnel]
    serializer_class = LoanTypeSerializer


class LoanFundViewSet(ModelViewSet):
    queryset = LoanFund.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsProvider]
    serializer_class = LoanFundSerializer


class LoanViewSet(ModelViewSet):
    queryset = Loan.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsCustomer]
    serializer_class = LoanSerializer


class AmortizationScheduleViewSet(ModelViewSet):
    queryset = AmortizationSchedule.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsCustomer]
    serializer_class = AmortizationScheduleSerializer
