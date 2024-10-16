import uuid

from django.contrib.auth import get_user_model
from django.db import models

from events.models import Event

from utils.constants import (
    TICKET_STATUSES,
    NOTIFICATION_STATUSES,
    active,
)


User = get_user_model()


class Ticket(models.Model):
    uuid = models.UUIDField(
        verbose_name='Идентификатор',
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    event = models.ForeignKey(
        verbose_name='Мероприятие',
        to=Event,
        on_delete=models.SET_NULL,
        related_name='tickets',
        null=True,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    event_name = models.CharField(
        verbose_name='Наименование мероприятия',
        blank=True,
    )
    section = models.CharField(
        verbose_name='Секция',
        max_length=64,
        null=True,
    )
    row = models.CharField(
        verbose_name='Ряд',
        max_length=64,
        null=True,
    )
    price = models.DecimalField(
        verbose_name='Цена за место',
        max_digits=7,
        decimal_places=2,
    )
    seat = models.CharField(
        verbose_name='Место',
        max_length=32,
    )
    status = models.CharField(
        verbose_name='Статус',
        choices=TICKET_STATUSES,
        default=active,
        blank=True,
    )
    acquiring_status = models.CharField(
        verbose_name='Статус эквайринга',
    )
    refund_id = models.CharField(
        verbose_name='Id возрата',
        null=True,
        blank=True,
    )
    payment_id = models.CharField(
        verbose_name='Id платежа',
    )
    bought_at = models.DateTimeField(
        verbose_name='Дата и время покупки',
        auto_now_add=True,
    )
    notification_status = models.CharField(
        verbose_name='Статус оповещения',
        choices=NOTIFICATION_STATUSES,
        default=NOTIFICATION_STATUSES[0][0],
        blank=True,
    )
    check_count = models.PositiveIntegerField(
        verbose_name='Количество попыток проверки',
        default=0,
        blank=True,
    )
    status_updated = models.DateTimeField(
        verbose_name='Время последнего обновления статуса',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.uuid}'

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.event_name = self.event.name
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'tickets'
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'
