import json
import os
from unittest.mock import patch

from django.test import TestCase

from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from users.models import CustomUser
from users.services import (
    register,
    auth,
    refresh_token,
    logout,
    confirm_email,
    password_restore_request,
    password_restore,
    detail,
    remove,
    change_password,
    confirm_email_request,
)


CUR_DIR = os.path.dirname(__file__)


class ServicesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'
        cls.files = f'{CUR_DIR}/fixtures/files'
        cls.user = CustomUser.objects.create_user(
            email='test@cc.com',
            password='test123',
            url_hash='fc0ecf9c-4c37-4bb2-8c22-938a1dc65da4',
        )

    @patch('users.services.send_user_email')
    def test_register(self, mock_send_user_email):
        mock_send_user_email.return_value = 200
        path = f'{self.path}/register'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_email'),
            (400, 'invalid_structure'),
            (406, 'already_exists'),
            (400, 'password_mismatch'),
        )

        request = self.client.post('/').wsgi_request
        host = request.get_host()
        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = register(
                data=data,
                host=host,
            )
            self.assertEqual(status_code, code, msg=fixture)

    def test_auth(self):
        path = f'{self.path}/auth'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_email'),
            (400, 'invalid_structure'),
            (401, 'not_authenticated'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = auth(
                data=data,
            )
            self.assertEqual(status_code, code, msg=fixture)

    def test_refresh_token(self):
        token = RefreshToken.for_user(
            user=self.user,
        )

        path = f'{self.path}/refresh_token'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid'),
            (403, 'forbidden'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            if data.get('refresh') is None:
                data['refresh'] = str(token)

            status_code, response_data = refresh_token(
                data=data,
            )
            self.assertEqual(status_code, code, msg=fixture)

    def test_logout(self):
        token = RefreshToken.for_user(
            user=self.user,
        )
        path = f'{self.path}/logout'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid'),
            (500, 'blacklisted_token'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            refresh = data.get('refresh')

            if refresh is not None:
                data['refresh'] = str(token)

            status_code, response_data = logout(
                data=data,
                user=self.user,
            )
            self.assertEqual(status_code, code, msg=fixture)

    def test_confirm_email(self):
        path = f'{self.path}/confirm_email'
        fixtures = (
            (200, 'valid'),
            (404, 'invalid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                url_hash = json.load(file)

            status_code, response_data = confirm_email(
                url_hash=url_hash,
            )
            self.assertEqual(status_code, code, msg=fixture)

    @patch('users.services.send_user_email')
    def test_password_restore_request(self, mock_send_user_email):
        mock_send_user_email.return_value = 200
        path = f'{self.path}/password_restore_request'
        fixtures = (
            (200, 'valid'),
            (404, 'wrong_email'),
            (400, 'invalid_email'),
            (400, 'invalid'),
        )

        request = self.client.post('/').wsgi_request
        host = request.get_host()

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = password_restore_request(
                data=data,
                host=host,
            )
            self.assertEqual(status_code, code, msg=fixture)

    def test_password_restore(self):
        path = f'{self.path}/password_restore'
        fixtures = (
            (400, 'password_mismatch'),
            (404, 'invalid'),
            (200, 'valid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            url_hash = data.pop('url_hash')
            status_code, response_data = password_restore(
                url_hash=url_hash,
                data=data,
            )
            self.assertEqual(status_code, code, msg=fixture)

    def test_detail(self):
        status_code, response_data = detail(
            user=self.user,
        )
        self.assertEqual(status_code, 200)

    def test_remove(self):
        status_code, response_data = remove(
            user=self.user,
        )
        self.assertEqual(status_code, 200)

    def test_change_password(self):
        path = f'{self.path}/change_password'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_old_password'),
            (400, 'invalid_structure'),
            (400, 'password_mismatch'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = change_password(
                data=data,
                user=self.user,
            )
            self.assertEqual(status_code, code, msg=fixture)

    @patch('users.services.send_user_email')
    def test_confirm_email_request(self, mock_send_user_email):
        mock_send_user_email.return_value = 200

        request = self.client.post('/').wsgi_request
        host = request.get_host()
        status_code, response_data = confirm_email_request(
            user=self.user,
            host=host,
        )
        self.assertEqual(status_code, 200)
