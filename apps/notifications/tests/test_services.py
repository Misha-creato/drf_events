import json
import os

from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch

from notifications.models import EmailSettings
from notifications.services import Email


CUR_DIR = os.path.dirname(__file__)


User = get_user_model()


class ServicesTest(TestCase):
    fixtures = ['email_template.json']

    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'
        cls.user = User.objects.create_user(
            email='test@cc.com',
            password='test123',
        )
        cls.settings = EmailSettings.get_solo()

    def test_formate_email_text(self):
        path = f'{self.path}/formate_email_text'
        fixtures = (
            (200, 'valid_confirm_email'),
            (200, 'valid_password_reset'),
            (501, 'invalid_email_type'),
            (500, 'invalid_mail_data'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            email = Email(
                email_type=data.get('email_type'),
                mail_data=data.get('mail_data'),
                recipient=self.user,
            )

            status_code, response = email.formate_email_text()
            self.assertEqual(status_code, code, msg=fixture)

    @patch('django.core.mail.send_mail')
    def test_send(self, mock_send_mail):
        mock_send_mail.return_value = 200
        path = f'{self.path}/send'
        fixtures = (
            (200, 'valid_confirm_email'),
            (200, 'valid_password_reset'),
            (403, 'enable_send_emails'),
            (501, 'invalid_email_type'),
            (500, 'invalid_mail_data'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            self.settings.send_emails = data.get('send_emails')
            self.settings.save()

            email = Email(
                email_type=data.get('email_type'),
                mail_data=data.get('mail_data'),
                recipient=self.user,
            )

            status_code = email.send()
            self.assertEqual(status_code, code, msg=fixture)