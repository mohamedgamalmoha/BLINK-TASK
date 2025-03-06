from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.authentication import BasicAuthentication

from loans.models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule
from loans.api.permissions import IsPersonnel, IsProvider, IsCustomer
from loans.api.serializers import (LoanFundTypeSerializer, LoanFundSerializer, LoanTypeSerializer, LoanSerializer,
                                   AmortizationScheduleSerializer)


class LoanFundTypeViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = LoanFundType.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsPersonnel]
    serializer_class = LoanFundTypeSerializer


class LoanTypeViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = LoanType.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsPersonnel]
    serializer_class = LoanTypeSerializer


class LoanFundViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = LoanFund.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsProvider]
    serializer_class = LoanFundSerializer


class LoanViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = Loan.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsCustomer]
    serializer_class = LoanSerializer


class AmortizationScheduleViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = AmortizationSchedule.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsCustomer]
    serializer_class = AmortizationScheduleSerializer
