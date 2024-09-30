from django.urls import path

from tickets.api import (
    TicketView,
    TicketQrView,
    TicketBuyView,
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
    path(
        'buy/',
        TicketBuyView.as_view(),
        name='ticket_buy',
    )
]
