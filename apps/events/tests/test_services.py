import json
import os
from datetime import datetime

from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from events.api import EventListView
from events.services import (
    get_all_events,
    get_event
)


CUR_DIR = os.path.dirname(__file__)


class TestServices(TestCase):
    fixtures = [
        'areas.json', 'categories.json', 'events.json',
        'landings.json', 'special_seats.json',
        'users.json', 'tickets.json'
    ]

    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'

    @patch('django.utils.timezone.now')
    def test_get_all_events(self, mock_timezone):
        dt = datetime(2024, 8, 1, tzinfo=timezone.utc)
        mock_timezone.return_value = dt

        view = EventListView

        path = f'{self.path}/get_all_events'
        fixtures = (
            (200, 'valid_search'),
            (200, 'valid_ordering_end_at'),
            (200, 'valid_ordering_start_at'),
            (200, 'valid_ordering_min_price'),
            (200, 'valid_filters'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            factory = APIRequestFactory()
            request = factory.get('/', data)
            request = Request(request)
            status_code, response_data = get_all_events(
                request=request,
                filter_backends=view.filter_backends,
                view=view,
            )
            print(response_data)
            self.assertEqual(status_code, code, msg=fixture)

    @patch('django.utils.timezone.now')
    def test_get_event(self, mock_timezone):
        dt = datetime(2024, 8, 1, tzinfo=timezone.utc)
        mock_timezone.return_value = dt

        path = f'{self.path}/get_event'
        fixtures = (
            (200, 'valid'),
            (404, 'not_found'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = get_event(
                slug=data['slug'],
            )
            print(response_data)
            self.assertEqual(status_code, code, msg=fixture)
