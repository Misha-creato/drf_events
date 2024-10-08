from django.urls import path

from events.api import (
    EventListView,
    EventView,
)


urlpatterns = [
    path(
        '',
        EventListView.as_view(),
        name='events',
    ),
    path(
        '<str:slug>/',
        EventView.as_view(),
        name='event',
    )
]
