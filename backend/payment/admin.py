from django.contrib import admin

from .models import PaymentProgress, Rate, FlatPayment


@admin.register(PaymentProgress)
class PaymentProgressAdmin(admin.ModelAdmin):
    list_display = (
        'home',
        'street',
        'month',
        'year',
        'result',
        'status',
        'task_id'
    )
    list_filter = ('status', 'year', 'month')


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('rate_type', 'rate')


@admin.register(FlatPayment)
class FlatPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'flat',
        'month',
        'year',
        'water_consumption',
        'water_cost',
        'maintenance_cost',
        'total_cost'
    )
    list_filter = ('flat', 'month', 'year')
