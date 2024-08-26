CONFIRM_EMAIL = 'confirm_email'
PASSWORD_RESTORE = 'password_restore'


EMAIL_TYPES = (
    (CONFIRM_EMAIL, 'Подтверждение адреса электронной почты'),
    (PASSWORD_RESTORE, 'Восстановление пароля'),
)

CITIES = (
    ('Almaty', 'Алматы'),
    ('Astana', 'Астана'),
    ('Karaganda', 'КАраганда'),
    ('Shymkent', 'Шымкент'),
)

AGE_LIMITS = (
    ('0_', 'Без ограничений'),
    ('6_', 'от 6 лет'),
    ('12_', 'от 12 лет'),
    ('16_', 'от 16 лет'),
    ('18_', 'от 18 лет'),
    ('21_', 'от 21 года'),
)

TICKET_STATUSES = (
    ('Active', 'Активный'),
    ('Used', 'Использованный'),
    ('Expired', 'Просроченный'),
)
