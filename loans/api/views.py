from rest_framework.authentication import BasicAuthentication
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from loans.models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule
from loans.api.permissions import IsPersonnel, IsProvider, IsCustomer
from loans.api.serializers import (LoanFundTypeSerializer, LoanFundSerializer, LoanTypeSerializer, LoanSerializer,
                                   AmortizationScheduleSerializer)


class LoanFundTypeViewSet(ModelViewSet):
    queryset = LoanFundType.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsPersonnel]
    serializer_class = LoanFundTypeSerializer

    def perform_create(self, serializer):
        serializer.save(personnel=self.request.user)


class LoanTypeViewSet(ModelViewSet):
    queryset = LoanType.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsPersonnel]
    serializer_class = LoanTypeSerializer

    def perform_create(self, serializer):
        serializer.save(personnel=self.request.user)


class LoanFundViewSet(ModelViewSet):
    queryset = LoanFund.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsProvider]
    serializer_class = LoanFundSerializer

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class LoanViewSet(ModelViewSet):
    queryset = Loan.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsCustomer]
    serializer_class = LoanSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class AmortizationScheduleViewSet(ReadOnlyModelViewSet):
    queryset = AmortizationSchedule.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsCustomer]
    serializer_class = AmortizationScheduleSerializer
