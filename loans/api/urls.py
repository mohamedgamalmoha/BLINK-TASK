from django.urls import path, include

from rest_framework import routers

from loans.api.views import (LoanFundTypeViewSet, LoanFundViewSet, LoanTypeViewSet, LoanViewSet,
                             AmortizationScheduleViewSet)


app_name = 'loans'

router = routers.DefaultRouter()
router.register(r'fund-type', LoanFundTypeViewSet, basename='fund_type')
router.register(r'fund', LoanFundViewSet, basename='fund')
router.register(r'type', LoanTypeViewSet, basename='type')
router.register(r'/', LoanViewSet, basename='loan')
router.register(r'amortization-schedule', AmortizationScheduleViewSet, basename='amortization_schedule')

urlpatterns = [
    path('loans/', include(router.urls), name='loans_routes'),
]
