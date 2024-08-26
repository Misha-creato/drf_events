from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)

from events.services import get_all_events
from utils.response_patterns import generate_response


class EventListView(APIView):
    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]
    ordering_fields = [
        'name',
        'min_price',
        'start_at',
        'end_at',
    ]

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
