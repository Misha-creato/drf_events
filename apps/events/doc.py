from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from rest_framework import serializers

from utils.response_patterns import DefaultResponse


class EventList200Response(DefaultResponse):
    '''
    Получение списка всех активных мероприятий, поиск, фильтрация по параметрам

    '''

    data = serializers.JSONField(
        default=[
            [
                {
                    "name": "Testing test2 event",
                    "slug": "testing-test2-event",
                    "city": "Astana",
                    "place": "Test2",
                    "address": "test2 address",
                    "start_at": "2024-08-28T00:00:00+05:00",
                    "end_at": "2024-08-29T04:00:00+05:00",
                    "age_limit": 0,
                    "category": "Театр",
                    "min_price": 4000,
                    "quantity": 50,
                    "available_tickets": 50,
                    "description": ""
                }
            ]
        ]
    )


class Event200Response(DefaultResponse):
    '''
    Получение детальной информации о мероприятии по слагу

    '''

    data = serializers.JSONField(
        default=[
            {
                "name": "Testing test2 event",
                "slug": "testing-test2-event",
                "city": "Astana",
                "place": "Test2",
                "address": "test2 address",
                "start_at": "2024-08-28T00:00:00+05:00",
                "end_at": "2024-08-29T04:00:00+05:00",
                "age_limit": 0,
                "category": "Театр",
                "min_price": 4000,
                "quantity": 50,
                "available_tickets": 50,
                "description": ""
            }
        ]
    )


event_list_parameters = [
    OpenApiParameter(
        name='search',
        description='Название площадки/Название мероприятия',
        required=False,
        type=OpenApiTypes.STR
    ),
    OpenApiParameter(
        name='ordering',
        description='Название мероприятия/Дата и время начала/окончания/Минимальная цена',
        required=False,
        type=OpenApiTypes.STR
    ),
    OpenApiParameter(
        name='area',
        description='Название площадки',
        required=False,
        type=OpenApiTypes.STR
    ),
    OpenApiParameter(
        name='city',
        description='Город',
        required=False,
        type=OpenApiTypes.STR
    ),
    OpenApiParameter(
        name='category',
        description='Категория',
        required=False,
        type=OpenApiTypes.STR
    ),
    OpenApiParameter(
        name='start_at',
        description='Дата и время начала',
        required=False,
        type=OpenApiTypes.DATETIME
    ),
    OpenApiParameter(
        name='end_at',
        description='Дата и время окончания',
        required=False,
        type=OpenApiTypes.DATETIME
    ),
    OpenApiParameter(
        name='age_limit',
        description='Возрастное ограничение',
        required=False,
        type=OpenApiTypes.INT
    ),
]
