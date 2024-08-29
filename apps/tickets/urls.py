from django.urls import path

from tickets.api import (
    TicketView,
    TicketQrView,
)


urlpatterns = [
    path(
        '',
        TicketView.as_view(),
        name='tickets',
    ),
    path(
        'qr/check/',
        TicketQrView.as_view(),
        name='ticket_qr_check',
    ),
]
