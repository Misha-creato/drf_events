from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils.text import slugify

from utils.constants import (
    CITIES,
    AGE_LIMITS,
    SEAT_TYPES,
)


User = get_user_model()


class Area(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
    )
    city = models.CharField(
        verbose_name='Город',
        choices=CITIES,
    )
    address = models.CharField(
        verbose_name='Адрес',
        max_length=256,
    )
    available = models.BooleanField(
        verbose_name='Доступна',
        default=True,
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.available:
            self.events.update(canceled=True)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'areas'
        verbose_name = 'Площадка'
        verbose_name_plural = 'Площадки'


class Category(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Event(models.Model):
    '''
        min_price обновляется через сигнал в events.signals
        при изменении связанной записи в таблице landing
    '''

    area = models.ForeignKey(
        verbose_name='Площадка',
        to=Area,
        on_delete=models.CASCADE,
        related_name='events',
    )
    category = models.ForeignKey(
        verbose_name='Категория',
        to=Category,
        on_delete=models.CASCADE,
        related_name='events',
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
    )
    start_at = models.DateTimeField(
        verbose_name='Дата и время начала',
    )
    end_at = models.DateTimeField(
        verbose_name='Дата и время окончания',
    )
    age_limit = models.IntegerField(
        verbose_name='Возрастное огранчиение',
        choices=AGE_LIMITS,
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True,
    )
    schema = models.ImageField(
        verbose_name='Схема площадки',
        upload_to='schemas',
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество доступных мест',
    )
    min_price = models.PositiveIntegerField(
        verbose_name='Минимальная цена',
        default=0,
    )
    canceled = models.BooleanField(
        verbose_name='Отменено',
        default=False,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique_for_date='start_at',
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время добавления',
        auto_now_add=True,
    )

    @property
    def available_tickets(self):
        return self.landings.aggregate(Sum('quantity'))['quantity__sum']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'events'
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'


class Landing(models.Model):
    event = models.ForeignKey(
        verbose_name='Мероприятие',
        to=Event,
        on_delete=models.CASCADE,
        related_name='landings',
    )
    section = models.CharField(
        verbose_name='Секция',
        max_length=64,
        null=True,
        blank=True,
    )
    row = models.CharField(
        verbose_name='Ряд',
        max_length=64,
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество мест',
    )
    price = models.DecimalField(
        verbose_name='Цена за место',
        max_digits=7,
        decimal_places=2,
    )

    def __str__(self):
        return f'{self.event.name} | секция {self.section} | ряд {self.row}'

    class Meta:
        db_table = 'landings'
        verbose_name = 'Посадка'
        verbose_name_plural = 'Посадки'

        unique_together = (
            'event',
            'section',
            'row',
        )


class SpecialSeat(models.Model):
    landing = models.ForeignKey(
        verbose_name='Посадка',
        to=Landing,
        on_delete=models.CASCADE,
        related_name='special_seats',
    )
    seat = models.CharField(
        verbose_name='Место',
        max_length=32,
    )
    price = models.DecimalField(
        verbose_name='Цена за место',
        max_digits=7,
        decimal_places=2,
    )
    seat_type = models.CharField(
        verbose_name='Тип места',
        choices=SEAT_TYPES,
    )

    def __str__(self):
        return f'{self.seat_type} {self.seat}'

    class Meta:
        db_table = 'special_seats'
        verbose_name = 'Особенное место'
        verbose_name_plural = 'Особенные места'

        unique_together = (
            'landing',
            'seat',
        )
