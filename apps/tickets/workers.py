import datetime

from django.utils import timezone

from events.models import Event

from tickets.tasks import notify_users
from tickets.models import Ticket

from utils.logger import get_logger
from utils.constants import (
    TICKET_STATUSES,
    NOTIFY_DAY_IN_DAY,
    NOTIFY_3_DAYS,
    NOTIFY_EXPIRED
)


logger = get_logger(__name__)


def check_notification(notification_status: str) -> None:
    '''
    Получение билетов по мероприятиям и оповещение пользователей

    Args:
        notification_status: статус оповещения

    Returns:
        None
    '''

    logger.info(
        msg=f'Получение билетов по мероприятиям для оповещения пользователей '
            f'{notification_status}',
    )

    event_filters = {}
    ticket_filters = {}
    email_type = ''
    match notification_status:
        case 'day_in_day':
            event_filters['start_at__date'] = timezone.now().date()
            ticket_filters['notification_status__in'] = ['no_notify', '3_days']
            email_type = NOTIFY_DAY_IN_DAY
        case '3_days':
            event_filters['start_at__date'] = (timezone.now().date() +
                                               datetime.timedelta(days=3))
            ticket_filters['notification_status'] = 'no_notify'
            email_type = NOTIFY_3_DAYS
        case 'expired':
            ticket_filters['notification_status__in'] = ['no_notify',
                                                         '3_days', 'day_in_day']
            ticket_filters['status'] = 'expired'
            email_type = NOTIFY_EXPIRED
        case _:
            return

    try:
        events = Event.objects.filter(**event_filters)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении билетов для оповещения '
                f'пользователей {notification_status}: {exc}',
        )
        return

    for event in events:
        tickets = event.tickets.filter(**ticket_filters)
        recipient_list = list(tickets.values_list('user__email', flat=True))
        event_name = event.name
        event_data = {
            'name': event_name,
            'datetime': event.start_at,
            'slug': event.slug,
        }
        if not recipient_list:
            return

        status = notify_users.delay(
            event_data=event_data,
            recipient_list=recipient_list,
            email_type=email_type,
        )
        if status.get() != 200:
            return

        logger.info(
            msg=f'Отправлено {len(tickets)} писем-оповещений {email_type} '
                f'по мероприятию {event_name} пользователям'
        )
        try:
            tickets.update(notification_status=notification_status)
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при обновлении статуса оповещения '
                    f'{notification_status} билетов по мероприятию '
                    f'{event_name}: {exc}',
            )
            return

        logger.info(
            msg=f'Успешно обновлены статусы оповещения {notification_status}'
                f'билетов по мероприятию {event_name}',
        )


def update_ticket_status() -> None:
    '''
    Обновление статуса просроченных билетов

    Returns:
        None
    '''

    logger.info(
        msg='Обновление статуса просроченных билетов'
    )

    try:
        tickets = Ticket.objects.filter(
            status='active',
            event__end_at__lte=timezone.now()
        )
        tickets.update(status=TICKET_STATUSES[2])
    except Exception as exc:
        logger.error(
            msg=f'Не удалось обновить статус просроченных билетов: {exc}',
        )
        return

    logger.info(
        msg=f'Обновлены статусы просроченных билетов',
    )
