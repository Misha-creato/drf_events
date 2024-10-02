from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.services import (
    get_user_tickets,
    check_ticket_qr,
    buy,
)

from utils.response_patterns import generate_response


class TicketView(APIView):

    permission_classes = [IsAuthenticated]

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

    def post(self, request):
        user = request.user
        data = request.data
        status_code, response_data = buy(
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