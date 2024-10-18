from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.doc import (
    Ticket200Response,
    DefaultTicketResponse,
    TicketBuy200Response,
)
from tickets.serializer import (
    TicketQRSerializer,
    TicketBuySerializer,
)
from tickets.services import (
    get_user_tickets,
    check_ticket_qr,
    Payment,
)

from utils.response_patterns import generate_response


payment = Payment()


class TicketView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: Ticket200Response,
            500: DefaultTicketResponse,
        },
        description=Ticket200Response.__doc__,
        summary='Получение билетов пользователя',
    )
    def get(self, request):
        user = request.user
        status_code, response_data = get_user_tickets(
            user=user,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class TicketQrView(APIView):

    @extend_schema(
        request=TicketQRSerializer,
        responses={
            200: DefaultTicketResponse,
            400: DefaultTicketResponse,
            410: DefaultTicketResponse,
            500: DefaultTicketResponse,
        },
        description='Проверка qr данных билета',
        summary='Проверка qr билета'
    )
    def post(self, request):
        data = request.data
        status_code, response_data = check_ticket_qr(
            data=data,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class TicketBuyView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TicketBuySerializer,
        responses={
            200: TicketBuy200Response,
            400: DefaultTicketResponse,
            404: DefaultTicketResponse,
            500: DefaultTicketResponse,
        },
        description=TicketBuy200Response.__doc__,
        summary='Покупка билета',
    )
    def post(self, request):
        user = request.user
        data = request.data
        status_code, response_data = payment.buy(
            user=user,
            data=data,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )
