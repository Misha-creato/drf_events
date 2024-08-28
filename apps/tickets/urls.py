from django.urls import path

from tickets.api import TicketView


urlpatterns = [
    path(
        '',
        TicketView.as_view(),
        name='tickets',
    ),
]
