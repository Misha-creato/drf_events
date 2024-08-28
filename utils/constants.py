CONFIRM_EMAIL = 'confirm_email'
PASSWORD_RESTORE = 'password_restore'


EMAIL_TYPES = (
    (CONFIRM_EMAIL, 'Подтверждение адреса электронной почты'),
    (PASSWORD_RESTORE, 'Восстановление пароля'),
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
    ('Active', 'Активный'),
    ('Used', 'Использованный'),
    ('Expired', 'Просроченный'),
)

SEAT_TYPES = (
    ('Ordinary', 'Обычное'),
    ('VIP', 'ВИП'),
    ('Discounted', 'Уцененное'),
)
