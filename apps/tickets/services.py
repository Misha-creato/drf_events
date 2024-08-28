from django.contrib.auth import get_user_model
from django.http import QueryDict

from tickets.serializer import (
    TicketSerializer,
    TicketQRSerializer,
)
from tickets.models import Ticket

from utils.constants import TICKET_STATUSES
from utils.logger import get_logger


logger = get_logger(__name__)
User = get_user_model()


def get_all_tickets(user: User) -> (int, list):
    '''

    Args:
        user: пользователь

    Returns:
        Код статуса и список данных
        200,
        [
            {
                "event_name": "Testing test2 event",
                "section": "1",
                "row": "2",
                "seat": "8",
                "status": "Active",
                "bought_at": "2024-08-08T12:15:32+05:00"
            }
        ]
    '''

    logger.info(
        msg=f'Получение списка билетов пользователя {user}',
    )

    try:
        tickets = Ticket.objects.filter(
            user=user,
        )
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении списка билетов '
                f'пользователя {user}: {exc}',
        )
        return 500, []

    response_data = TicketSerializer(
        instance=tickets,
        many=True,
    ).data
    logger.info(
        msg=f'Успешно получен список билетов пользователя {user}',
    )
    return 200, response_data


def check_ticket_qr(data: QueryDict) -> (int, dict):
    '''

    Args:
        data: данные qr

    Returns:
        Код статуса и словарь данных
        200, {}
    '''

    logger.info(
        msg=f'Проверка данных для qr билета {data}',
    )

    serializer = TicketQRSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для qr билета {data}: {serializer.errors}',
        )
        return 400, {}

    validated_data = serializer.validated_data
    print(validated_data)
    try:
        ticket = Ticket.objects.filter(
            pk=validated_data['uuid'],
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при проверке данных для qr билета {data}: {exc}',
        )
        return 500, {}

    if ticket is None:
        logger.error(
            msg=f'Билет с данными {data} для проверки qr не найден',
        )
        return 410, {}

    if ticket.status != 'Active':
        logger.error(
            msg=f'Билет с данными {data} уже недействителен',
        )
        return 400, {}

    ticket.status = TICKET_STATUSES[1]
    try:
        ticket.save()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при проверки данных для qr билета {data}: {exc}',
        )
        return 500, {}

    logger.info(
        msg=f'Успешно проверены qr данные билета {data}',
    )
    return 200, {}
