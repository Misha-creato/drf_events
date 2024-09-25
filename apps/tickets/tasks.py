from celery import shared_task

from django.urls import reverse

from config.settings import (
    SITE_PROTOCOL,
    HOST,
)

from notifications.services import Email

from tickets.models import Ticket

from utils.logger import get_logger


logger = get_logger(__name__)


@shared_task
def notify_user(ticket_uuid: str, ticket_data: dict, email_type: str, notification_status: str):
    user_email = ticket_data['user_email']
    logger.info(
        msg=f'Отправка письма-оповещения пользователю {user_email}'
    )

    path = reverse('event', args=(ticket_data['event_slug'],))
    url = f'{SITE_PROTOCOL}://{HOST}/{path}'
    mail_data = {
        'datetime': ticket_data['datetime'],
        'event_name': ticket_data['event_name'],
        'url': url,
    }

    email = Email(
        email_type=email_type,
        mail_data=mail_data,
        recipient=user_email,
    )
    status = email.send()
    if status == 200:
        try:
            ticket = Ticket.objects.filter(
                uuid=ticket_uuid,
            )
            ticket.notification_status = notification_status
            ticket.save()
        except Exception as exc:
            logger.error(
                f'Не удалось обновить статус оповещения билета {ticket_uuid}: {exc}',
            )
