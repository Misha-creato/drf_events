import datetime

from django.utils import timezone

from notifications.tasks import notify_user

from tickets.models import Ticket

from utils.logger import get_logger
from utils.constants import (
    TICKET_STATUSES,
    NOTIFY_DAY_IN_DAY,
    NOTIFY_3_DAYS,
    NOTIFY_EXPIRED)


logger = get_logger(__name__)


def check_notification(notification_status: str):
    logger.info(
        msg=f'Получение билетов для оповещения пользователя '
            f'{notification_status}',
    )

    filters = {}
    email_type = ''
    match notification_status:
        case 'day_in_day':
            filters['notification_status__in'] = ['no_notify', '3_days']
            filters['event__start_at__date'] = timezone.now().date()
            email_type = NOTIFY_DAY_IN_DAY
        case '3_days':
            filters['notification_status'] = 'no_notify'
            filters['event__start_at__date'] = (timezone.now().date() +
                                                datetime.timedelta(days=3))
            email_type = NOTIFY_3_DAYS
        case 'expired':
            filters['notification_status__in'] = ['no_notify',
                                                  '3_days', 'day_in_day']
            filters['status'] = 'expired'
            email_type = NOTIFY_EXPIRED

    try:
        tickets = Ticket.objects.filter(**filters)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении билетов для оповещения '
                f'пользователя {notification_status}: {exc}',
        )
    else:
        for ticket in tickets:
            ticket_data = {
                'user_email': ticket.user.email,
                'event_name': ticket.event_name,
                'datetime': ticket.event.start_at,
                'event_slug': ticket.event.slug,
            }
            notify_user.delay(
                ticket_uuid=ticket.uuid,
                ticket_data=ticket_data,
                email_type=email_type,
                notification_status=notification_status,
            )


def update_ticket_status():
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

