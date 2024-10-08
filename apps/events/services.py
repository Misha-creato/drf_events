from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import Prefetch
from django.utils import timezone

from events.models import Event
from events.serializers import (
    EventSerializer,
    EventLandingSerializer,
)

from tickets.models import Ticket

from utils import (
    redis_cache,
    constants,
)
from utils.logger import get_logger


User = get_user_model()
logger = get_logger(__name__)


def get_all_events(request: Any, filter_backends: list, view: Any) -> (int, list):
    '''
    Получение списка всех мероприятий

    Args:
        request: запрос
        filter_backends: список фильтров для фильтрации, поиска и сортировки
        view: представление

    Returns:
        Код статуса и список данных
        200,
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
                "available_tickets": 45,
                "description": "Description"
            }
        ]
    '''

    logger.info(
        msg='Получение списка активных мероприятий',
    )

    try:
        events = Event.objects.filter(
            canceled=False,
            end_at__gte=timezone.now(),
        ).select_related('area', 'category')
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении списка активных мероприятий: {exc}',
        )
        return 500, []

    if request.query_params:
        for backend in filter_backends:
            try:
                events = backend().filter_queryset(
                    request=request,
                    queryset=events,
                    view=view,
                )
            except Exception as exc:
                logger.info(
                    msg=f'Не удалось получить список всех площадок по фильтрам: {exc}',
                )

    response_data = EventSerializer(
        instance=events,
        many=True,
    ).data
    logger.info(
        msg='Успешно получен список активных мероприятий',
    )
    return 200, response_data


def get_event(user: User | AnonymousUser, slug: str) -> (int, dict):
    '''
    Получение мероприятия по слагу

    Args:
        slug: слаг мероприятия

    Returns:
        Код статуса и словарь данных
        200,
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
            "available_tickets": 45,
            "description": "Description",
            "landings": [
            {
                "section": null,
                "row": null,
                "quantity": 25,
                "price": "4000.00",
                "special_seats": [
                {
                    "seat": "12",
                    "price": "8000.00",
                    "seat_type": "vip"
                }
                ]
            }
            ],
            "tickets": [
            {
                "section": null,
                "row": null,
                "seat": "8"
            }
            ],
            "temporary_booking": [
            {
                "event": 1,
                "user": 1,
                "seat_data":
                {
                    "section": null,
                    "row": null,
                    "seat": "18"
                }
                price: 1000.00
            }
            ]
            "user_temporary_booking": [
            ]
        }
    '''

    logger.info(
        msg=f'Получение мероприятия по слагу {slug}',
    )

    try:
        event = Event.objects.filter(
            canceled=False,
            end_at__gte=timezone.now(),
            slug=slug,
        ).prefetch_related(
            Prefetch('tickets',
                     queryset=Ticket.objects.exclude(
                         status=constants.canceled,
                     )),
            'landings',
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении мероприятия по слагу {slug}: {exc}',
        )
        return 500, {}

    if event is None:
        logger.info(
            msg=f'Мероприятие по слагу {slug} не найдено',
        )
        return 404, {}

    key_pattern = f'*event{event.id}*'
    status, matching_keys = redis_cache.get_matching_keys(
        key_pattern=key_pattern,
    )

    if status != 200:
        logger.error(
            msg=f'Не удалось получить временные брони мероприятия по слагу {slug}',
        )
        return status, {}

    temporary_booking = []
    user_temporary_booking = []
    for key in matching_keys:
        status, data = redis_cache.get(
            key=key,
        )
        if status != 200:
            return status, {}

        if data['user'] == user.id:
            user_temporary_booking.append(data)
        else:
            temporary_booking.append(data)

    response_data = EventLandingSerializer(
        instance=event,
    ).data
    response_data['temporary_booking'] = temporary_booking
    response_data['user_temporary_booking'] = user_temporary_booking
    logger.info(
        msg=f'Успешно найдено мероприятие по слагу {slug}',
    )
    return 200, response_data
