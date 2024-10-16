from datetime import (
    timedelta,
    datetime
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

from events.models import Event, Landing

from tickets.serializer import (
    TicketSerializer,
    TicketQRSerializer,
    TicketBuySerializer,
)
from tickets.models import Ticket

from utils import (
    redis_cache,
    constants,
)
from utils.logger import get_logger


logger = get_logger(__name__)
User = get_user_model()


class Payment:
    bill_success_statuses = [
        'CREATED',
        'PAID',
    ]
    bill_fail_statuses = [
        'EXPIRED',
        'DECLINED',
    ]

    payment_done_status = 'COMPLETED'
    payment_success_statuses = [
        'WAITING',
        payment_done_status,
    ]
    payment_fail_statuses = [
        'DECLINED',
    ]

    refund_done_status = 'COMPLETED'
    refund_success_statuses = [
        'WAITING',
        refund_done_status,
    ]
    refund_fail_statuses = [
        'DECLINED',
    ]
    url = f'{PAYMENT_HOST}/sites/{PAYMENT_SITE_ID}'
    headers = {
        "Authorization": f"Bearer {PAYMENT_AUTHORIZATION_TOKEN}",
    }
    allowed_methods = [
        'get',
        'post',
        'put',
    ]

    def make_request(self, method: str, path: str, json_data: dict = None) -> (int, dict):
        '''
        Отправка запроса с помощью библиотеки requests

        Args:
            method: метод запроса
            "get"
            path: путь запроса
            "/path/"
            json_data: данные запроса
            {
                "data": "example"
            }

        Returns:
        Код статуса и словарь данных
        '''

        logger.info(
            msg=f'Отправка {method} запроса в платежную систему по пути {path} '
                f'с данными {json_data}',
        )
        if method not in self.allowed_methods:
            logger.error(
                msg=f'Не удалось отправить {method} запрос в платежную систему '
                    f'по пути {path} c данными {json_data}: неправильный метод',
            )
            return 400, {}

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
            msg=f'Отправлен {method} запрос в платежную систему по пути '
                f'{path} с данными {json_data}',
        )
        status = response.status_code

        if status == 200:
            data = response.json()
        else:
            data = response.content

        if status == 500 and 'not found' in response.json()['message'].lower():
            status = 404
        return status, data

    def buy(self, user: User, data: QueryDict) -> (int, dict):
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
                },
                "price": 1000.00
            }

        Returns:
            Код статуса и словарь данных
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
                id=int(event_id),
                canceled=False,
                end_at__gt=timezone.now(),
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

        try:
            landings = list(event.landings.filter(
                quantity__gt=0,
            ).values('section', 'row'))
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при получении доступных посадок по мероприятию '
                    f'{event_id}: {exc}',
            )
            return 500, {}

        seat_data = data['seat_data']
        landing_data = seat_data.copy()
        landing_data.pop('seat')

        if landing_data not in landings:
            logger.error(
                msg=f'Некорректные данные для покупки билета {data} пользователем '
                    f'{user}: Посадка по данным {seat_data} не доступна или не существует',
            )
            return 400, {}

        key_pattern = f'*event{event_id}*'
        status, matching_keys = redis_cache.get_matching_keys(
            key_pattern=key_pattern,
        )

        if status != 200:
            logger.error(
                msg=f'Не удалось получить временные брони мероприятия по id {event_id}',
            )
            return status, {}

        for key in matching_keys:
            status, key_data = redis_cache.get(
                key=key,
            )
            if status != 200:
                return status, {}

            if seat_data == key_data['seat_data']:
                if user.id != key_data['user']:
                    logger.error(
                        msg=f'Некорретные данные для покупки билета {data} пользователем '
                            f'{user}',
                    )
                    return 400, {}
                redis_cache.delete(key=key)

        try:
            tickets = list(event.tickets.exclude(
                status=constants.canceled,
            ).values('section', 'row', 'seat'))
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
            msg=f'Создание счета для оплаты билета {data} пользователю {user}',
        )
        price = str(data['price'])
        # у qiwi время идет с опозданием на 11 минут
        expiration_datetime = datetime.now().isoformat(timespec='seconds') + '+05:00'
        bill_data = {
            "amount": {
                "currency": "KZT",
                "value": price
            },
            "expirationDateTime": expiration_datetime,
            "comment": f"Оплата билета на мероприятие {event.name}",
            "customer": {
                "email": user.email,
            }
        }
        bill_id = str(uuid.uuid4())
        path = f'/bills/{bill_id}/'
        status, response_data = self.make_request(
            method='put',
            path=path,
            json_data=bill_data,
        )
        if status != 200:
            logger.error(
                msg=f'Возникла ошибка при создании счета для оплаты билета {data} '
                    f' пользователю {user}: {response_data}',
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
            time=600,
        )
        if status != 200:
            logger.error(
                msg=f'Не удалось создать временную бронь билета {data}',
            )
            return 500, {}

        status = redis_cache.push_to_list(
            key='bills_to_check',
            value=bill_id,
        )
        if status != 200:
            logger.error(
                msg=f'Не удалось добавить {bill_id} в список для проверки',
            )
            return 500, {}

        logger.info(
            msg=f'Временно забронированн билет {data}. Cоздан счет для оплаты '
                f'билета пользователю {user}',
        )
        pay_url = response_data['payUrl']
        response_data = {
            'pay_url': pay_url,
        }
        return 200, response_data

    def confirm_buying(self, bill_id: str) -> int:
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
        status, response_data = self.make_request(
            method='get',
            path=path,
        )
        if status == 404:
            return status

        if status != 200:
            logger.error(
                msg=f'Возникла ошибка при подтверждении покупки по счету {bill_id}:'
                    f'{response_data}',
            )
            return 500

        bill_status = response_data['status']['value']
        if bill_status in self.bill_fail_statuses:
            logger.error(
                msg=f'Не удалось подтвердить покупку по счету {bill_id}. '
                    f'Статус счета {bill_status}',
            )
            return 400  # Todo

        if bill_status not in self.bill_success_statuses:
            logger.error(
                msg=f'Не удалось подтвердить покупку по счету {bill_id}. '
                    f'Получен неизвестный статус счета {bill_status}',
            )
            return 500

        payments = response_data.get('payments')
        if not payments:
            logger.info(
                msg=f'Ожидание оплаты счета {bill_id} со стороны пользователя',
            )
            return 500

        payment_data = payments[0]
        payment_id = payment_data['paymentId']
        payment_status = payment_data['status']['value']

        ticket_status = constants.waiting_payment
        if payment_status in self.payment_fail_statuses:
            logger.error(
                msg=f'Не удалось подтвердить покупку по счету {bill_id}. '
                    f'Статус платежа {payment_status}',
            )
            return 400  # Todo

        if payment_status not in self.payment_success_statuses:
            logger.error(
                msg=f'При подтверждении покупки по счету {bill_id} получен '
                    f'неизвестный статус платежа {payment_status}',
            )
            ticket_status = constants.unknown

        key_pattern = f'*bill{bill_id}*'
        status, keys = redis_cache.get_matching_keys(
            key_pattern=key_pattern,
        )
        if status != 200 or not keys:
            logger.error(
                msg=f'Не удалось подтвердить покупку по счету {bill_id}. '
                    f'Ошибка redis или временная недоступна',
            )
            return status

        key = keys[0]
        status, key_data = redis_cache.get(
            key=key,
        )
        if status != 200:
            logger.error(
                msg=f'Не удалось подтвердить покупку по счету {bill_id}. '
                    f'Ошибка redis или временная недоступна',
            )
            return status

        if payment_status == self.payment_done_status:
            ticket_status = constants.active

        seat_data = key_data['seat_data']
        section = seat_data['section']
        row = seat_data['row']
        try:
            ticket = Ticket.objects.create(
                event_id=key_data['event'],
                user_id=key_data['user'],
                section=section,
                row=row,
                seat=seat_data['seat'],
                price=key_data['price'],
                status=ticket_status,
                payment_id=payment_id,
                acquiring_status=payment_status,
                status_updated=timezone.now(),
            )
            landing = Landing.objects.filter(
                event=ticket.event,
                section=section,
                row=row,
            ).first()
            landing.quantity -= 1
            landing.save()
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при подтверждении покупки по счету {bill_id}: '
                    f'{exc}',
            )
            return 500

        redis_cache.delete(
            key=key,
        )

        logger.info(
            msg=f'Успешно подтверждена покупка по счету {bill_id} и создан билет',
        )
        return 200

    def check_payment(self, payment_id: str) -> (int, dict):
        '''
        Проверка статуса платежа по id

        Args:
            payment_id: id платежа

        Returns:
            Код статуса и словарь данных
        '''

        logger.info(
            msg=f'Проверка статуса платежа {payment_id}',
        )

        path = f'/payments/{payment_id}/'
        status, response_data = self.make_request(
            method='get',
            path=path,
        )

        data = {
            'acquiring_status': None
        }
        if status == 404:
            logger.error(
                msg=f'Возникла ошибка при проверке статуса платежа {payment_id}. '
                    f'Платеж не найден',
            )
            data['ticket_status'] = constants.canceled
            return status, data

        if status != 200:
            logger.error(
                msg=f'Возникла ошибка при проверке статуса платежа {payment_id}',
            )
            data['ticket_status'] = constants.waiting_payment
            return 500, data

        payment_status = response_data['status']['value']
        data['acquiring_status'] = payment_status

        if payment_status in self.payment_fail_statuses:
            logger.error(
                msg=f'Платеж {payment_id} не прошел',
            )
            data['ticket_status'] = constants.canceled
            return 400, data

        if payment_status not in self.payment_success_statuses:
            logger.error(
                msg=f'При проверке платежа {payment_id} получен неизвестный '
                    f'статус {payment_status}',
            )
            data['ticket_status'] = constants.unknown
            return 500, data

        if payment_status == self.payment_done_status:
            logger.info(
                msg=f'Платеж {payment_id} прошел успешно'
            )
            data['ticket_status'] = constants.active
            return 200, data

        logger.info(
            msg=f'Платеж {payment_id} в обработке',
        )
        data['ticket_status'] = constants.waiting_payment
        return 200, data

    def refund(self, payment_id: str, amount: str) -> (int, dict):
        '''
        Возврат средств по id завершенного платежа

        Args:
            payment_id: id платежа
            amount: сумма возврата

        Returns:
            Код статуса и словарь данных
        '''

        logger.info(
            msg=f'Возврат средств по платежу {payment_id}',
        )

        refund_data = {
            "amount": {
                "currency": "KZT",
                "value": amount,
            }
        }
        refund_id = str(uuid.uuid4())
        path = f'/payments/{payment_id}/refunds/{refund_id}/'
        status, response_data = self.make_request(
            method='put',
            path=path,
            json_data=refund_data,
        )
        data = {
            'refund_id': refund_id,
            'refund_status': constants.need_refund
        }
        if status != 200:
            logger.error(
                msg=f'Возникла ошибка при возврате средств по платежу {payment_id}:'
                    f'{response_data}',
            )
            return 500, data

        refund_status = response_data['status']['value']
        if status in self.refund_fail_statuses:
            logger.error(
                msg=f'Не удалось осуществить возврат средств по платежу: {payment_id}.'
                    f'Статус возврата {refund_status}',
            )
            data['refund_status'] = constants.fail_refund
            return 400, data #TODO

        if status not in self.payment_success_statuses:
            logger.error(
                msg=f'Не удалось осуществить возврат средств по платежу: {payment_id} '
                    f'Неизвестный статус возврата {refund_status}',
            )
            data['refund_status'] = constants.unknown
            return 400, data

        data['refund_status'] = constants.waiting_refund
        if refund_status == self.refund_done_status:
            data['refund_status'] = constants.success_refund

        logger.info(
            msg=f'Осуществлен возврат средств по платежу {payment_id}. '
                f'Статус возврата {refund_status}',
        )
        return 200, data

    def check_refund(self, payment_id: str, refund_id: str) -> (int, dict):
        '''
        Проверка статуса возврата средств

        Args:
            payment_id: id платежа
            refund_id: id возврата

        Returns:
            Код статуса и словарь данных
        '''

        logger.info(
            msg=f'Проверка статуса возврата средств {refund_id} по '
                f'платежy {payment_id}',
        )
        path = f'/payments/{payment_id}/refunds/{refund_id}/'
        status, response_data = self.make_request(
            method='get',
            path=path,
        )
        data = {
            'acquiring_status': None,
            'refund_status': constants.waiting_refund
        }
        if status != 200:
            logger.error(
                msg=f'Не удалось проверить статус возврата средств {refund_id} '
                    f'по платежу {payment_id}: {response_data}',
            )
            return status, data

        refund_status = response_data['status']['value']
        data['acquiring_status'] = refund_status

        if refund_status in self.refund_fail_statuses:
            logger.error(
                msg=f'Ошибка возврата средств {refund_id} по платежу {payment_id}.'
                    f'Статус возврата {refund_status}',
            )
            data['refund_status'] = constants.fail_refund
            return 400, data #todo

        if refund_status not in self.payment_success_statuses:
            logger.error(
                msg=f'При проверка статуса возврата средств {refund_id} по платежу '
                    f'{payment_id} получен неизвестный статус: {refund_status}',
            )
            data['refund_status'] = constants.unknown
            return 400, data #todo

        data['refund_status'] = constants.waiting_refund
        if refund_status == self.refund_done_status:
            logger.info(
                msg=f'Успешный возврат средств {refund_id} по платежу {payment_id}',
            )
            data['refund_status'] = constants.success_refund

        return 200, data


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
            msg=f'Билет с данными {data} недействителен',
        )
        return 400, {}

    ticket.status = constants.used
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
