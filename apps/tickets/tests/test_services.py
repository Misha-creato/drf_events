import json
import os

from django.contrib.auth import get_user_model
from django.test import TestCase

from tickets.services import get_all_tickets, check_ticket_qr

CUR_DIR = os.path.dirname(__file__)
User = get_user_model()


class TestServices(TestCase):
    fixtures = [
        'areas.json', 'categories.json', 'events.json',
        'users.json', 'landings.json', 'tickets.json',
    ]

    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'

    def test_get_all_tickets(self):
        status_code, response_data = get_all_tickets(
            user=User.objects.get(pk=1),
        )
        print(response_data)
        self.assertEqual(status_code, 200)

    def test_check_ticket_qr(self):
        path = f'{self.path}/check_ticket_qr'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid'),
            (400, 'invalid_structure'),
            (410, 'not_found'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = check_ticket_qr(
                data=data,
            )
            self.assertEqual(status_code, code, msg=fixture)
