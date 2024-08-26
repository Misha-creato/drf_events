from django.db import models
from django.forms import model_to_dict

from solo.models import SingletonModel

from utils import redis_cache
from utils.constants import EMAIL_TYPES


class EmailTemplate(models.Model):
    email_type = models.CharField(
        verbose_name='Тип письма',
        max_length=64,
        unique=True,
        choices=EMAIL_TYPES,
    )
    subject = models.CharField(
        verbose_name='Тема',
        max_length=256,
    )
    message = models.TextField(
        verbose_name='Сообщение',
    )

    def __str__(self):
        return self.email_type

    class Meta:
        db_table = 'email_templates'
        verbose_name = 'Шаблон письма'
        verbose_name_plural = 'Шаблоны писем'


class EmailSettings(SingletonModel):
    send_emails = models.BooleanField(
        verbose_name='Отправка писем включена',
        default=True,
    )

    def __str__(self):
        return ''

    def save(self, *args, **kwargs):
        redis_cache.set_key(
            key='email_settings',
            data=model_to_dict(self),
            time=60*60,
        )
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'email_settings'
        verbose_name = 'Настройки email'
