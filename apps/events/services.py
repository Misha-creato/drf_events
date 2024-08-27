from typing import Any

from django.utils import timezone

from events.models import Event
from events.serializers import EventSerializer

from utils.logger import get_logger


logger = get_logger(__name__)


def get_all_events(request: Any, filter_backends: list, view: Any) -> (int, list):
    '''
    Получение списка всех мероприятий

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
            },
            ....
        ]
    '''
    logger.info(
        msg='Получение списка активных мероприятий',
    )

    try:
        events = Event.objects.filter(
            canceled=False,
            start_at__gte=timezone.now(),
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


def get_event(slug: str) -> (int, dict):
    '''
    Получение списка мероприятия по слагу

    Returns:
        Код статуса и словарь данных
        200,
        {
            "name": "Testing test2 event",
            ....
        },
    '''
    logger.info(
        msg=f'Получение мероприятия по слагу {slug}',
    )

    try:
        event = Event.objects.filter(
            canceled=False,
            start_at__gte=timezone.now(),
            slug=slug,
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

    response_data = EventSerializer(
        instance=event,
    ).data
    logger.info(
        msg=f'Успешно найдено мероприятие по слагу {slug}',
    )
    return 200, response_data
