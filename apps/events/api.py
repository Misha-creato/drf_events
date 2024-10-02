from drf_spectacular.utils import extend_schema

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)


from events.filters import EventFilter
from events.services import (
    get_all_events,
    get_event,
)
from events.doc import (
    event_list_parameters,
    DefaultEventResponse,
    EventList200Response,
    Event200Response,
)

from utils.response_patterns import generate_response


class EventListView(APIView):
    filter_backends = [
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'name',
        'area__name',
    ]
    ordering_fields = [
        'name',
        'min_price',
        'start_at',
        'end_at',
    ]
    filter_fields = [
        'area__name',
        'start_at',
        'end_at',
        'age_limit',
        'category__name',
        'area__city',
    ]
    filterset_class = EventFilter

    @extend_schema(
        parameters=event_list_parameters,
        responses={
            200: EventList200Response,
            500: DefaultEventResponse,
        },
        description=EventList200Response.__doc__,
        summary='Получение списка всех мероприятий',
    )
    def get(self, request):
        status_code, response_data = get_all_events(
            request=request,
            filter_backends=self.filter_backends,
            view=self,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class EventView(APIView):

    @extend_schema(
        responses={
            200: Event200Response,
            404: DefaultEventResponse,
            500: DefaultEventResponse,
        },
        description=Event200Response.__doc__,
        summary='Получение мероприятия по слагу',
    )
    def get(self, request, slug):
        user = request.user
        status_code, response_data = get_event(
            user=user,
            slug=slug,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )
