CONFIRM_EMAIL = 'confirm_email'
PASSWORD_RESTORE = 'password_restore'
NOTIFY_3_DAYS = 'notify_3_days'
NOTIFY_DAY_IN_DAY = 'notify_day_in_day'
NOTIFY_EXPIRED = 'notify_expired'

EMAIL_TYPES = (
    (CONFIRM_EMAIL, 'Подтверждение адреса электронной почты'),
    (PASSWORD_RESTORE, 'Восстановление пароля'),
    (NOTIFY_DAY_IN_DAY, 'Оповещение день в день'),
    (NOTIFY_3_DAYS, 'Оповещенеи за 3 дня'),
    (NOTIFY_EXPIRED, 'Оповещение о просроченном билете'),
)

CITIES = (
    ('Almaty', 'Алматы'),
    ('Astana', 'Астана'),
    ('Karaganda', 'Караганда'),
    ('Shymkent', 'Шымкент'),
)

AGE_LIMITS = (
    (0, 'Без ограничений'),
    (6, 'от 6 лет'),
    (12, 'от 12 лет'),
    (16, 'от 16 лет'),
    (18, 'от 18 лет'),
    (21, 'от 21 года'),
)

TICKET_STATUSES = (
    ('waiting_payment', 'Ожидание оплаты'),
    ('active', 'Активный'),
    ('used', 'Использованный'),
    ('expired', 'Просроченный'),
)


NOTIFICATION_STATUSES = (
    ('no_notify', 'Не оповещен'),
    ('3_days', 'За 3 дня'),
    ('day_in_day', 'День в день'),
    ('expired', 'Просроченный'),
)


SEAT_TYPES = (
    ('vip', 'ВИП'),
    ('discounted', 'Уцененное'),
)
