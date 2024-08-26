from django.urls import path

from events.api import EventListView


urlpatterns = [
    path(
        '',
        EventListView.as_view(),
        name='events',
    )
]
