import datetime

from django.utils import timezone

from tickets.services import Payment
from tickets.tasks import notify_users
from tickets.models import Ticket

from utils import redis_cache
from utils.logger import get_logger
from utils.constants import (
    TICKET_STATUSES,
    NOTIFY_DAY_IN_DAY,
    NOTIFY_3_DAYS,
    NOTIFY_EXPIRED
)


logger = get_logger(__name__)
payment = Payment()


def user_event_notification(notification_status: str) -> None:
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

    filters = {}
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
        case _:
            return

    try:
        tickets = Ticket.objects.filter(**filters).select_related('event', 'user')
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении билетов для оповещения '
                f'пользователей {notification_status}: {exc}',
        )
        return

    aggregated_events = {}
    for ticket in tickets:
        if not aggregated_events.get(ticket.event.id):
            aggregated_events[ticket.event.id] = {}
            event_data = {
                'name': ticket.event_name,
                'datetime': ticket.event.start_at,
                'slug': ticket.event.slug,
            }
            aggregated_events[ticket.event.id]['event_data'] = event_data
            aggregated_events[ticket.event.id]['recipients'] = []
        aggregated_events[ticket.event.id]['recipients'].append(ticket.user.email)

    for event, value in aggregated_events.items():
        status = notify_users.delay(
            event_data=value['event_data'],
            recipient_list=value['recipients'],
            email_type=email_type,
        )
        if status.get() != 200:
            return

        logger.info(
            msg=f'Отправлено {len(tickets)} писем-оповещений {email_type} '
                f'пользователям'
        )
        try:
            tickets.update(notification_status=notification_status)
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при обновлении статуса оповещения '
                    f'{notification_status} билетов: {exc}',
            )
            return

        logger.info(
            msg=f'Успешно обновлены статусы оповещения {notification_status}'
                f'билетов',
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


def check_bill_status() -> None:
    '''
    Проверка статусов счетов для оплаты из списка redis

    Returns:
    None
    '''

    logger.info(
        msg=f'Проверка статусов счетов для оплаты из списка redis',
    )

    status, bills = redis_cache.get_list(
        key='bills_to_check',
    )
    if status != 200:
        logger.error(
            msg=f'Возникла ошибка при проверку статусов счетов для оплаты',
        )
        return

    for bill in bills:
        status, data = payment.confirm_buying(
            bill_id=bill,
        )
        if status != 500:
            redis_cache.remove_from_list(
                key='bills_to_check',
                value=bill,
            )


def check_payment_status() -> None:
    '''
    Проверка статусов платежей в ожидании

    Returns:
    None
    '''

    logger.info(
        msg=f'Проверка статусов платежей в ожидании',
    )

    try:
        tickets = Ticket.objects.filter(
            status='waiting',
        )
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при проверке статусов платежей в ожидании'
        )
        return

    for ticket in tickets:
        status, response = payment.check_payment(
            payment_id=ticket.payment_id,
        )
        if status == 200:
            ticket.status = TICKET_STATUSES[1]
            try:
                ticket.save()
            except Exception as exc:
                logger.error(
                    msg=f'Возникла ошибка при смене статуса оплаченного билета '
                        f'{ticket}: {exc}',
                )
        elif status == 400:
            try:
                ticket.delete()
            except Exception as exc:
                logger.error(
                    msg=f'Возникла ошибка при удалении неоплаченного билета {exc}'
                )
