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


waiting_payment = 'waiting'
active = 'active'
used = 'used'
expired = 'expired'
canceled = 'canceled'
unknown = 'unknown'

# REFUND STATUSES
need_refund = 'need_refund'
waiting_refund = 'waiting_refund'
success_refund = 'success_refund'
fail_refund = 'fail_refund'


TICKET_STATUSES = (
    (unknown, 'Неизвестный'),
    (waiting_payment, 'Ожидание оплаты'),
    (active, 'Активный'),
    (used, 'Использованный'),
    (expired, 'Просроченный'),
    (canceled, 'Отмененный'),
    (need_refund, 'Нужен возврат'),
    (waiting_refund, 'Ожидание возврата'),
    (success_refund, 'Удачный возврат'),
    (fail_refund, 'Ошибка возврата'),
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
