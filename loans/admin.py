from django.contrib import admin

from .models import LoanFundType, LoanFund, LoanType, Loan, AmortizationSchedule


class AmortizationScheduleInlineAdmin(admin.TabularInline):
    model = AmortizationSchedule
    min_num = 0
    extra = 1
    readonly_fields = ('create_at', 'update_at')


@admin.register(LoanFundType)
class LoanFundTypeModelAdmin(admin.ModelAdmin):
    list_display = ['personnel', 'name', 'create_at', 'update_at']
    readonly_fields = ('create_at', 'update_at')


@admin.register(LoanFund)
class LoanFundModelAdmin(admin.ModelAdmin):
    list_display = ['provider', 'loan_type', 'amount', 'create_at', 'update_at']
    readonly_fields = ('create_at', 'update_at')


@admin.register(LoanType)
class LoanTypeModelAdmin(admin.ModelAdmin):
    list_display = ['personnel', 'name', 'create_at', 'update_at']
    readonly_fields = ('create_at', 'update_at')


@admin.register(Loan)
class LoanModelAdmin(admin.ModelAdmin):
    list_display = ['customer', 'loan_type', 'status', 'amount', 'create_at', 'update_at']
    readonly_fields = ('create_at', 'update_at')
    inlines = [AmortizationScheduleInlineAdmin]
