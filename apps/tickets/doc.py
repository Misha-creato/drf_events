from rest_framework import serializers

from utils.response_patterns import DefaultResponse


class Ticket200Response(DefaultResponse):
    '''
    Получение всех билетов авторизованного пользователя

    '''

    data = serializers.JSONField(
        default=[
            {
                "uuid": "e7f5d696-a8fd-4d5d-9ea7-db7100903581",
                "event_name": "Test event",
                "section": "2",
                "row": "2",
                "seat": "2",
                "status": "active",
                "bought_at": "2024-10-17T17:00:39+05:00"
            },
        ]
    )


class TicketBuy200Response(DefaultResponse):
    '''
    Покупка билета по данным пользователем

    '''
    data = serializers.JSONField(
        default={
            "pay_url": "https://pay_url"
        },
    )
