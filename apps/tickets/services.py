from datetime import (
    datetime,
    timedelta
)

import requests
import uuid

from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.utils import timezone

from config.settings import (
    PAYMENT_HOST,
    PAYMENT_AUTHORIZATION_TOKEN,
    PAYMENT_SITE_ID,
)

from events.models import Event

from tickets.serializer import (
    TicketSerializer,
    TicketQRSerializer,
    TicketBuySerializer,
)
from tickets.models import Ticket

from utils import redis_cache
from utils.constants import TICKET_STATUSES
from utils.logger import get_logger


logger = get_logger(__name__)
User = get_user_model()


class Payment:
    bill_success_statuses = [
        'CREATED',
        'PAID',
    ]
    payment_success_statuses = [
        'WAITING',
        'COMPLETED',
    ]
    url = f'{PAYMENT_HOST}/sites/{PAYMENT_SITE_ID}'
    headers = {
        "Authorization": f"Bearer {PAYMENT_AUTHORIZATION_TOKEN}",
    }

    def make_request(self, method: str, path: str, json_data: dict = None) -> (int, dict):
        logger.info(
            msg=f'Отправка {method} запроса в платежную систему по пути {path} '
                f'с данными {json_data}',
        )
        url = self.url + path
        if json_data is None:
            json_data = {}
        try:
            response = getattr(requests, method)(
                url=url,
                headers=self.headers,
                json=json_data,
            )
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при отправке {method} запроса в платежную '
                    f'систему по пути {path} с данными {json_data}: {exc}',
            )
            return 500, {}

        logger.info(
            msg=f'Успешно отпрвлен {method} запрос в платежную систему по пути '
                f'{path} с данными {json_data}',
        )
        return 200, response


payment = Payment()


def get_user_tickets(user: User) -> (int, list):
    '''

    Args:
        user: авторизованный пользователь

    Returns:
        Код статуса и список данных
        200,
        [
            {
                "event_name": "Testing test2 event",
                "section": "1",
                "row": "2",
                "seat": "8",
                "status": "аctive",
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
        {
            "uuid": "d868d304-f37a-46f2-ad68-a03f7492f62c"
        }

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

    if ticket.status != 'active':
        logger.error(
            msg=f'Билет с данными {data} уже недействителен',
        )
        return 400, {}

    ticket.status = TICKET_STATUSES[1]
    try:
        ticket.save()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при проверке данных для qr билета {data}: {exc}',
        )
        return 500, {}

    logger.info(
        msg=f'Успешно проверены qr данные билета {data}',
    )
    return 200, {}


def buy(user: User, data: QueryDict) -> (int, dict):
    '''
    Покупка билета пользователем

    Args:
        user: пользователь
        data: данные билета
        {
            "event_id": 1,
            "seat_data":
            {
                "section": "1",
                "row": "1",
                "seat": "1"
            }
            "price": 1000.00
        }

    Returns:

    '''

    logger.info(
        msg=f'Покупка билета {data} пользователем {user}',
    )

    serializer = TicketBuySerializer(
        data=data
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Некорректные данные для покупки билета {data} пользователем {user}:'
                f'{serializer.errors}',
        )
        return 400, {}

    data = serializer.validated_data
    event_id = data['event_id']
    try:
        event = Event.objects.filter(
            id=event_id,
            canceled=False,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении мероприятия по id {event_id}: {exc}',
        )
        return 500, {}

    if event is None:
        logger.info(
            msg=f'Мероприятие по id {event_id} не найдено',
        )
        return 404, {}

    key_pattern = f'*event{event_id}*'
    status, matching_keys = redis_cache.get_matching_keys(
        key_pattern=key_pattern,
    )

    if status != 200:
        logger.error(
            msg=f'Не удалось получить временные брони мероприятия по id {event_id}',
        )
        return status, {}

    seat_data = data['seat_data']
    for key in matching_keys:
        status, key_data = redis_cache.get(
            key=key,
        )
        if status != 200:
            return status, {}

        if seat_data == key_data['seat_data'] and user.id != key_data['user']:
            logger.error(
                msg=f'Некорретные данные для покупки билета {data} пользователем'
                    f'{user}',
            )
            return 400, {}

    try:
        tickets = list(event.tickets.all().values('section', 'row', 'seat'))
        print(tickets)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении билетов мероприятия по id '
                f'{event_id}: {exc}',
        )
        return 500, {}

    if seat_data in tickets:
        logger.error(
            msg=f'Некорретные данные для покупки билета {data} пользователем '
                f'{user}. Билет уже куплен',
        )
        return 400, {}

    logger.info(
        msg=f'Создание счета для оплаты билета {seat_data} '
            f'на мероприятие {event_id} пользователю {user}',
    )
    price = str(data['price'])
    bill_data = {
        "amount": {
            "currency": "KZT",
            "value": price
        },
        "expirationDateTime": (timezone.now() + timedelta(minutes=10)).
        isoformat(timespec='seconds'),
        "comment": f"Оплата билета на мероприятие {event.name}",
        # "successUrl": "https://test.com/", #TODO
        # "failedUrl": "https://test.com", #TODO
        "customer": {
            "email": user.email,
        }
    }
    bill_id = str(uuid.uuid4())
    path = f'/bills/{bill_id}/'
    status, response = payment.make_request(
        method='put',
        path=path,
        json_data=bill_data,
    )
    response_data = response.json()
    if status != 200 or response.status_code != 200:
        logger.error(
            msg=f'Возникла ошибка при создании счета для оплаты билета {seat_data} '
                f'на мероприятие {event_id} пользователю {user}: {response_data}',
        )
        return 500, {}

    key = f'event{event_id}_bill{bill_id}'
    ticket_data = {
        'seat_data': seat_data,
        'user': user.id,
        'price': price,
        'event': event_id,
    }
    status = redis_cache.set_key(
        key=key,
        data=ticket_data,
        time=600
    )
    if status != 200:
        logger.error(
            msg=f'Не удалось создать временную бронь билета {seat_data} на '
                f'мероприятие {event_id}',
        )
        return 500, {}

    logger.info(
        msg=f'Временно забронированн билет {seat_data} на мероприятие {event_id}. '
            f'Создан счет для оплаты билета пользователю {user}',
    )
    pay_url = response_data['payUrl']
    response_data = {
        'pay_url': pay_url,
    }
    return 200, response_data


def confirm_buying(bill_id: str) -> (int, dict):
    '''
    Подтверждение покупки и создание билета по id счета

    Args:
        bill_id: id счета

    Returns:
        Код статуса и словарь данных
    '''

    logger.info(
        msg=f'Подтверждение покупки по счету {bill_id}'
    )

    path = f'/bills/{bill_id}/details/'
    status, response = payment.make_request(
        method='get',
        path=path,
    )
    response_data = response.json()
    if status != 200 or response.status_code != 200:
        logger.error(
            msg=f'Возникла ошибка при подтверждении покупки по счету {bill_id}:'
                f'{response_data}',
        )
        return 500, {}

    bill_status = response_data['status']['value']
    if bill_status not in payment.bill_success_statuses:
        logger.error(
            msg=f'Не удалось подтвердить покупку по счету {bill_id}',
        )
        return 500, {} #Todo

    payment_data = response_data['payments'][0]
    payment_id = payment_data['paymentId']
    payment_status = payment_data['status']['value']

    if payment_status not in payment.payment_success_statuses:
        logger.error(
            msg=f'Не удалось подтвердить покупку по счету {bill_id}',
        )
        return 500, {}  # Todo

    key_pattern = f'*bill{bill_id}*'
    status, keys = redis_cache.get_matching_keys(
        key_pattern=key_pattern,
    )
    if status != 200 or not keys:
        logger.error(
            msg=f'Не удалось подтвердить покупку по счету {bill_id}',
        )
        return status, {}

    key = keys[0]
    status, key_data = redis_cache.get(
        key=key,
    )
    if status != 200:
        logger.error(
            msg=f'Не удалось подтвердить покупку по счету {bill_id}',
        )
        return status, {}

    ticket_status = TICKET_STATUSES[1]
    if payment_status == 'WAITING':
        ticket_status = TICKET_STATUSES[0]

    seat_data = key_data['seat_data']
    try:
        Ticket.objects.create(
            event=key_data['event'],
            user=key_data['user'],
            section=seat_data['section'],
            row=seat_data['row'],
            seat=seat_data['seat'],
            price=key_data['price'],
            status=ticket_status,
            payment_id=payment_id,
        )
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при подтверждении покупки по счету {bill_id}',
        )
        return 500, {}

    redis_cache.delete(
        key=key,
    )

    logger.info(
        msg=f'Успешно подтверждена покупка по счету {bill_id} и создан билет',
    )
    return 200, {}

