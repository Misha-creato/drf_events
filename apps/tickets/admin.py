from django.contrib import admin

from tickets.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'uuid',
        'bought_at',
        'status_updated',
        'check_count',
        'acquiring_status',
    ]
    list_filter = [
        'acquiring_status',
        'status',
    ]
    readonly_fields = [
        'user',
        'payment_id',
        'acquiring_status',
        'status_updated',
        'section',
        'row',
        'seat',
        'price',
        # 'status',
    ]
