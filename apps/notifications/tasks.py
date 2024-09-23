import datetime

from django.utils import timezone

from events.models import Event

from tickets.models import Ticket

from utils.logger import get_logger


logger = get_logger(__name__)


def get_events_day_in_day():
    logger.info(
        msg=f'Получение списка мероприятий для оповещения пользователей'
    )

    try:
        events = Event.objects.filter(
            notification_status__in=['no notify', '3 days'],
            start_at__date=timezone.now().date()
        )
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении списка мероприятий '
                f'для оповещения пользователей: {exc}',
        )
    else:
        for event in events:
            pass # TODO


def get_events_by_3_days():
    logger.info(
        msg=f'Получение списка мероприятий для оповещения пользователей'
    )

    try:
        events = Event.objects.filter(
            notification_status='no notify',
            start_at__date=timezone.now().date() + datetime.timedelta(days=3),
        )
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении списка мероприятий '
                f'для оповещения пользователей: {exc}',
        )
    else:
        for event in events:
            pass # TODO


def get_expired_events():
    logger.info(
        msg=f'Получение списка мероприятий для оповещения пользователей'
    )

    try:
        events = Event.objects.filter(
            notification_status__in=['no notify', '3 days', 'day in day'],
            end_at__lte=timezone.now()
        )
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении списка мероприятий '
                f'для оповещения пользователей: {exc}',
        )
    else:
        for event in events:
            pass # TODO


def get_expired_tickets():
    logger.info(
        msg=f'Получение списка билетов для обновления статуса и оповещения пользователей'
    )

    try:
        tickets = Ticket.objects.filter(
            status='active',
            event__end_at__lte=timezone.now()
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить список билетов для обновления статуса и'
                f'оповещения пользователей: {exc}',
        )
    else:
        for ticket in tickets:
            pass #todo
