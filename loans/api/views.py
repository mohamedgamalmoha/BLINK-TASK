from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.authentication import BasicAuthentication
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_flex_fields.utils import is_expanded
from rest_flex_fields.filter_backends import FlexFieldsFilterBackend

from loans.models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule
from loans.api.permissions import IsPersonnel, IsProvider, IsCustomer
from loans.api.serializers import (LoanFundTypeSerializer, LoanFundSerializer, LoanTypeSerializer, LoanSerializer,
                                   AmortizationScheduleSerializer, AmortizationPayment)


class LoanFundTypeViewSet(ModelViewSet):
    queryset = LoanFundType.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsPersonnel]
    serializer_class = LoanFundTypeSerializer

    def perform_create(self, serializer):
        serializer.save(personnel=self.request.user)

    @action(["GET"], detail=False, url_name='me', url_path='me', serializer_class=LoanFundTypeSerializer)
    def me(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(personnel=self.request.user)
        return self.list(request,*args, **kwargs)


class LoanTypeViewSet(ModelViewSet):
    queryset = LoanType.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsPersonnel]
    serializer_class = LoanTypeSerializer

    def perform_create(self, serializer):
        serializer.save(personnel=self.request.user)

    @action(["GET"], detail=False, url_name='me', url_path='me', serializer_class=LoanTypeSerializer)
    def me(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(personnel=self.request.user)
        return self.list(request,*args, **kwargs)


class LoanFundViewSet(ModelViewSet):
    queryset = LoanFund.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsProvider]
    serializer_class = LoanFundSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(provider=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class LoanViewSet(ModelViewSet):
    queryset = Loan.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsCustomer]
    serializer_class = LoanSerializer
    filter_backends = [FlexFieldsFilterBackend] + api_settings.DEFAULT_FILTER_BACKENDS
    permit_list_expands = ['amortizations']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(customer=self.request.user)
        if is_expanded(self.request, 'amortizations'):
            queryset = queryset.select_related('amortizations')
        return queryset

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class AmortizationScheduleViewSet(ReadOnlyModelViewSet):
    queryset = AmortizationSchedule.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsCustomer]
    serializer_class = AmortizationScheduleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(loan__customer__id=self.request.user.id)
        return queryset

    @action(["POST"], detail=True, url_name='pay', url_path='pay',serializer_class=AmortizationPayment)
    def pay(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_paid=True)
        return Response(serializer.data)
