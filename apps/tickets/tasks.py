from celery import shared_task

from django.urls import reverse

from config.settings import (
    SITE_PROTOCOL,
    HOST,
)

from notifications.services import Email
from tickets.api import payment

from utils.logger import get_logger


logger = get_logger(__name__)


@shared_task
def notify_users(event_data: dict, recipient_list: list, email_type: str) -> int:
    '''
    Асинхронная отправка писем-оповещений по мероприятию списку пользователей

    Args:
        event_data: данные мероприятия для формирования текста письма
            {
            "name": "Test event name",
            "datetime": datetime.datetime(2024, 9, 25, 13, 0,
            tzinfo=datetime.timezone.utc),
            "slug": "test-event-name"
            }
        recipient_list: список получателей письма
            ["test1@cc.com", "test2@cc.com"]
        email_type: тип письма
            "notify_day_in_day"

    Returns:
        Код статуса
    '''

    event_name = event_data['name']
    logger.info(
        msg=f'Отправка писeм-оповещений {email_type} по мероприятию '
            f' {event_name} списку пользователей {recipient_list}',
    )

    path = reverse('event', args=(event_data['slug'],))
    url = f'{SITE_PROTOCOL}://{HOST}/{path}'
    mail_data = {
        'datetime': event_data['datetime'],
        'event_name': event_name,
        'url': url,
    }

    email = Email(
        email_type=email_type,
        mail_data=mail_data,
        recipient=recipient_list,
    )
    status = email.send()
    return status


@shared_task
def check_bill(bill_id: str) -> int:
    '''
    Асинхронная проверка статуса счета

    Args:
        bill_id: id счета

    Returns:
        Код статуса
    '''

    status = payment.confirm_buying(
        bill_id=bill_id,
    )
    return status


@shared_task
def check_payment(payment_id: str) -> dict:
    '''
    Асинхронная проверка статуса платежа

    Args:
        payment_id: id платежа

    Returns:
        Код статуса и словарь данных
    '''

    status, data = payment.check_payment(
        payment_id=payment_id,
    )
    return data


@shared_task
def refund(payment_id: str, amount: str) -> dict:
    '''
    Асинхронный возврат средств по платежу

    Args:
        payment_id: id платежа
        amount: сумма возрата

    Returns:
        Словарь данных
    '''

    status, data = payment.refund(
        payment_id=payment_id,
        amount=amount,
    )
    return data


@shared_task
def check_refund(payment_id: str, refund_id: str) -> dict:
    '''
    Асинхронная проверка статуса возрата средств

    Args:
        payment_id: id платежа
        refund_id: id возврата

    Returns:
        Словарь данных
    '''

    status, data = payment.check_refund(
        payment_id=payment_id,
        refund_id=refund_id,
    )
    return data
