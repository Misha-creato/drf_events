from typing import Any

from django.utils import timezone

from events.models import Event
from events.serializers import EventSerializer

from utils.logger import get_logger


logger = get_logger(__name__)


def get_all_events(request: Any, filter_backends: list, view: Any) -> (int, list):
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
