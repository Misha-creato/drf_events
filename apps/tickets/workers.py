import datetime

from celery import group

from django.db.models import (
    Q,
)
from django.utils import timezone

from events.models import Landing

from tickets.services import Payment
from tickets.tasks import (
    notify_users,
    check_bill,
    check_payment,
    refund,
    check_refund,
)
from tickets.models import Ticket

from utils import redis_cache, constants
from utils.logger import get_logger
from utils.constants import (
    NOTIFY_DAY_IN_DAY,
    NOTIFY_3_DAYS,
    NOTIFY_EXPIRED
)


logger = get_logger(__name__)
payment = Payment()


def user_event_notification(notification_status: str) -> None:
    '''
    Оповещение пользователей по билетам

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
                                                  '3_days',
                                                  'day_in_day', ]
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
        tickets.update(status=constants.expired)
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
        msg='Проверка статусов счетов для оплаты из списка redis',
    )

    status, bills = redis_cache.get_list(
        key='bills_to_check',
    )
    if status != 200:
        logger.error(
            msg='Возникла ошибка при проверку статусов счетов для оплаты',
        )
        return

    task_group = group(check_bill.s(bill_id=bill) for bill in bills)
    result_group = task_group.apply_async()
    results = result_group.join()

    bills_data = {}
    for result in results:
        bills_data.update(result)

    for bill in bills:
        status = bills_data[bill]
        key_pattern = f'*bill{bill}*'
        redis_status, keys = redis_cache.get_matching_keys(
            key_pattern=key_pattern,
        )
        if status != 500 or (redis_status == 200 and not keys):
            redis_cache.remove_from_list(
                key='bills_to_check',
                value=bill,
            )

    logger.info(
        msg=f'Проверены статусы {len(bills)} счетов',
    )


def check_payment_status() -> bool:
    '''
    Проверка статусов платежей в ожидании

    Returns:
        True/False
    '''

    logger.info(
        msg='Проверка статусов платежей билетов в ожидании',
    )

    try:
        tickets = Ticket.objects.filter(
            status=constants.waiting_payment,
        ).exclude( #лучше бы убрать
            event=None,
        ).select_related('event')
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при проверке статусов платежей в ожидании: {exc}',
        )
        return False

    landing_filters = []
    tickets_data = {}

    task_group = group(check_payment.s(
        payment_id=ticket.payment_id,
        ticket_uuid=str(ticket.uuid),
    ) for ticket in tickets)
    result_group = task_group.apply_async()
    results = result_group.join()

    for result in results:
        tickets_data.update(result)

    for ticket in tickets:
        data = tickets_data[str(ticket.uuid)]
        acquiring_status = data['acquiring_status']
        ticket_status = data['ticket_status']

        ticket.status = ticket_status
        ticket.acquiring_status = acquiring_status if acquiring_status else ticket.acquiring_status
        ticket.check_count += 1
        ticket.status_updated = timezone.now()

        if ticket_status == constants.canceled:
            filter_dict = {
                'event': ticket.event,
                'section': ticket.section,
                'row': ticket.row,
            }
            landing_filters.append(filter_dict)

        if ticket_status == constants.active:
            if ticket.event.canceled:
                ticket.status = constants.need_refund

    if tickets:
        try:
            Ticket.objects.bulk_update(tickets, [
                'status', 'acquiring_status', 'check_count', 'status_updated',
            ])
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при проверке статусов билетов в ожидании. '
                    f'Обновление билетов: {exc}',
            )
            return False

    if landing_filters:
        query_filter = Q()
        for filter_dict in landing_filters:
            filter_object = Q(event=filter_dict['event'])
            filter_object &= Q(section=filter_dict['section'])
            filter_object &= Q(row=filter_dict['row'])

            query_filter |= filter_object

        try:
            landings = (Landing.objects.filter(query_filter).
                        select_related('event'))
            for landing in landings:
                landing.quantity += 1

            Landing.objects.bulk_update(landings, ['quantity'])
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при проверке статусов билетов в ожидании. '
                    f'Обновление посадок: {exc}',
            )
            return False

    logger.info(
        msg=f'Проверены статусы платежей {len(tickets)} билетов в ожидании',
    )
    return True


def need_refund() -> bool:
    '''
    закрывается площадка -> выборка активных билетов -≥
    установка статуса "нужно вернуть" -≥ отправка запроса на возврат средств -≥
    если вернулся успешный статус -≥ установка refund_status "refunded"/"waiting"
    -≥ воркер на опрос билетов с статусом возврата waiting

    Осуществление возврата средств для всех билетов со
    статусом необходимости возврата

    Returns:
        True/False
    '''

    logger.info(
        msg='Возврат средств для всех билетов со статусом need_refund',
    )

    try:
        tickets = Ticket.objects.filter(
            status=constants.need_refund,
        ).select_related('events')
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении билетов для возврата средств: {exc}',
        )
        return False

    tickets_data = {}

    task_group = group(refund.s(
        payment_id=ticket.payment_id,
        amount=str(ticket.price),
        ticket_uuid=str(ticket.uuid),
    ) for ticket in tickets)

    result_group = task_group.apply_async()
    results = result_group.join()

    for result in results:
        tickets_data.update(result)

    for ticket in tickets:
        data = tickets_data[ticket.uuid]

        refund_status = data['refund_status']
        refund_id = data['refund_if']
        ticket.status = refund_status
        ticket.refund_id = refund_id
        ticket.status_updated = timezone.now()

    if tickets:
        try:
            Ticket.objects.bulk_update(tickets, [
                'status', 'refund_id', 'status_updated',
            ])
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при возврате средств у билетов со статусом '
                    f'необходимости возврата. Обновление билетов: {exc}',
            )
            return False

    logger.info(
        msg=f'Осуществлен возврат средств у {len(tickets)} билетов',
    )
    return True


def check_refund_status() -> bool:
    '''
    Проверка статуса возврата средств у билетов с возвратом в ожидании

    Returns:
        True/False
    '''

    logger.info(
        msg='Проверка статуса возврата средств у билетов с возвратом в ожидании',
    )

    try:
        tickets = Ticket.objects.filter(
            status=constants.waiting_refund,
        ).select_related('event')
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении билетов с возвратом в ожидании: {exc}',
        )
        return False

    tickets_data = {}
    task_group = group(check_refund.s(
        payment_id=ticket.payment_id,
        refund_id=ticket.refund_id,
        ticket_uuid=str(ticket.uuid),
    ) for ticket in tickets)

    result_group = task_group.apply_async()
    results = result_group.join()

    for result in results:
        tickets_data.update(result)

    for ticket in tickets:
        data = tickets_data[ticket.uuid]
        refund_status = data['refund_status']
        acquiring_status = data['acquiring_status']

        ticket.status = refund_status
        ticket.acquiring_status = acquiring_status if acquiring_status else ticket.acquiring_status
        ticket.status_updated = timezone.now()
        ticket.check_count += 1

    if tickets:
        try:
            Ticket.objects.bulk_update(tickets, [
                'status', 'acquiring_status', 'status_updated', 'check_count',
            ])
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при проверке возврата средств у билетов. '
                    f'Обновление билетов: {exc}',
            )
            return False

    logger.info(
        msg=f'Проверен статус возврата средств у {len(tickets)} билетов',
    )
    return True
