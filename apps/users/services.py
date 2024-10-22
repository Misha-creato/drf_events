import uuid

from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.http import QueryDict
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken

from config.settings import (
    CLIENT_ID,
    CLIENT_SECRET,
    SITE_PROTOCOL,
)

from google_custom_oauth2.google_oauth import GoogleOAuth

from notifications.services import Email

from users.models import CustomUser
from users.serializers import (
    RegisterSerializer,
    AuthSerializer,
    RefreshAndLogoutSerializer,
    PasswordRestoreRequestSerializer,
    PasswordRestoreSerializer,
    DetailSerializer,
    ChangePasswordSerializer,
)

from utils.constants import (
    CONFIRM_EMAIL,
    PASSWORD_RESTORE,
)
from utils.logger import (
    get_logger,
    get_log_user_data,
)


logger = get_logger(__name__)
oauth = GoogleOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri='http://127.0.0.1:8000/api/v1/users/auth/callback/',
    scope=['openid', 'email'],
)


def register(data: QueryDict, host: str) -> (int, dict):
    '''
    Регистрация пользователя

    Args:
        data: данные пользователя
            {
              "email": "test_new@cc.com",
              "password": "test123",
              "confirm_password": "test123"
            }
        host: хост для создания полного url пути
            используется в отправке писем

    Returns:
        Код статуса и словарь данных
        200,
        {
            "refresh": "refresh_token",
            "access": "access_token"
        }
    '''

    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Регистрация пользователя с данными {user_data}',
    )

    serializer = RegisterSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для регистрации пользователя '
                f'с данными {user_data}: {serializer.errors}',
        )
        return 400, {}

    validated_data = serializer.validated_data
    try:
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
    except IntegrityError as exc:
        logger.error(
            msg=f'Пользователь с данными {user_data} уже существует: {exc}',
        )
        return 406, {}
    except Exception as exc:
        logger.error(
            msg=f'Не удалось создать пользователя с данными {user_data}: {exc}',
        )
        return 500, {}

    logger.info(
        msg=f'Успешно зарегистрирован пользователь с данными: {user_data}',
    )

    send_user_email(
        user=user,
        host=host,
        email_type=CONFIRM_EMAIL,
    )

    try:
        token = RefreshToken.for_user(
            user=user,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить токен для аутентификации пользователя '
                f'с данными {user_data} после регистрации: {exc}',
        )
        return 201, {}

    token['email'] = user.email
    refresh = str(token)
    access = str(token.access_token)
    response_data = {
        'refresh': refresh,
        'access': access,
    }
    return 200, response_data


def auth(data: QueryDict) -> (int, dict):
    '''
    Аутентификация пользователя

    Args:
        data: данные пользователя
            {
              "email": "test@cc.com",
              "password": "test123"
            }

    Returns:
        Код статуса и словарь данных
        200,
        {
            "refresh": "refresh_token",
            "access": "access_token"
        }
    '''

    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Аутентификация пользователя с данными: {user_data}',
    )

    serializer = AuthSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для аутентификации пользователя '
                f'с данными {user_data}: {serializer.errors}',
        )
        return 400, {}

    validated_data = serializer.validated_data
    try:
        user = authenticate(
            email=validated_data['email'],
            password=validated_data['password'],
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось аутентифицировать пользователя с данными {user_data}: '
                f'{exc}',
        )
        return 500, {}

    if user is None:
        logger.error(
            msg=f'Не удалось аутентифицировать пользователя с данными {user_data}: '
                'неправильные email или пароль',
        )
        return 401, {}

    try:
        token = RefreshToken.for_user(
            user=user,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить токен для аутентификации пользователя '
                f'с данными {user_data}: {exc}',
        )
        return 500, {}

    token['email'] = user.email
    refresh = str(token)
    access = str(token.access_token)
    response_data = {
        'refresh': refresh,
        'access': access,
    }
    logger.info(
        msg=f'Успешная аутентификация пользователя с данными: {user_data}',
    )
    return 200, response_data


def get_google_auth_link() -> (int, dict):
    '''
    Получение ссылки для авторизации через google

    Returns:
        Код статуса и словарь данных
        200,
        {
            "google_auth_url": "https://accounts.google.com/o/oauth2/v2/auth?
             scope=https%3A//www.googleapis.com/auth/drive.metadata.readonly&
             access_type=offline&
             include_granted_scopes=true&
             response_type=code&
             state=state_parameter_passthrough_value&
             redirect_uri=https%3A//oauth2.example.com/code&
             client_id=client_id"
        }
    '''

    logger.info(
        msg=f'Получение ссылки для авторизации через google',
    )

    state = str(uuid.uuid4())
    auth_url = oauth.get_auth_url(
        state=state,
    )

    response_data = {
        'google_auth_url': auth_url,
    }
    return 200, response_data


def google_callback(code: str) -> (int, dict):
    '''
    Авторизация через Google

    Args:
        code: авторизационный код от Google

    Returns:
        Код статуса и словарь данных
    '''

    logger.info(
        msg='Авторизация пользователя через google',
    )

    if not code:
        logger.error(
            msg='Не удалось авторизовать пользователя через google: '
                'отсутствие авторизационного кода',
        )
        return 400, {}#todo

    status, response = oauth.exchange_code_for_tokens(
        code=code,
    )
    if status != 200:
        logger.error(
            msg='Не удалось авторизовать пользователя через google: '
                'Ошибка получения токенов',
        )
        return 500, {}#todo

    id_token = response['id_token']

    status, response = oauth.verify_id_token(
        id_token=id_token,
    )
    if status != 200:
        logger.error(
            msg='Не удалось авторизовать пользователя через google: '
                'Ошибка получения данных пользователя',
        )
        return 500, {}#todo

    email = response['email']
    try:
        user, created = CustomUser.objects.get_or_create(
            email=email,
        )
        if created:
            random_password = CustomUser.objects.make_random_password()
            user.set_password(random_password)
            user.save()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при авторизации пользователя через google: '
                f'{exc}',
        )
        return 500, {}

    try:
        token = RefreshToken.for_user(
            user=user,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить токен для авторизации пользователя '
                f'через google: {exc}',
        )
        return 500, {}

    token['email'] = user.email
    refresh = str(token)
    access = str(token.access_token)
    response_data = {
        'refresh': refresh,
        'access': access,
    }
    logger.info(
        msg='Успешная авторизация пользователя через google',
    )
    return 200, response_data


def refresh_token(data: QueryDict) -> (int, dict):
    '''
    Обновление токена

    Args:
        data: данные для обновления
            {
              "refresh": "refresh_token"
            }

    Returns:
        Код статуса и словарь данных
        200,
        {
            "access": "access_token",
            "refresh": "new_refresh_token"
        }
    '''

    logger.info(
        msg='Обновление токена',
    )

    serializer = RefreshAndLogoutSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для обновления токена: {serializer.errors}',
        )
        return 400, {}

    validated_data = serializer.validated_data
    try:
        refresh = RefreshToken(validated_data['refresh'])
        user_id = refresh.payload['user_id']
        user = CustomUser.objects.get(id=user_id)
    except Exception as exc:
        logger.error(
            msg=f'Не удалось обновить токен: {exc}',
        )
        return 403, {}

    response_data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    logger.info(
        msg='Успешно обновлен токен'
    )
    return 200, response_data


def logout(data: QueryDict, user: CustomUser) -> (int, dict):
    '''
    Выход из системы

    Args:
        data: данные для выхода
            {
              "refresh": "refresh_token"
            }
        user: пользователь

    Returns:
        Код статуса и словарь данных
        200, {}
    '''

    logger.info(
        msg=f'Выход из системы пользователя {user}',
    )

    serializer = RefreshAndLogoutSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для выхода из системы пользователя {user}: '
                f'{serializer.errors}',
        )
        return 400, {}

    validated_data = serializer.validated_data
    try:
        refresh = RefreshToken(validated_data['refresh'])
    except Exception as exc:
        logger.error(
            msg=f'Невалидный токен для выхода пользователя {user}: {exc}',
        )
        return 500, {}

    try:
        refresh.blacklist()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось занести токен пользователя {user} '
                f'в черный список: {exc}',
        )
        return 500, {}

    logger.info(
        msg=f'Успешный выход из системы пользователя {user}',
    )
    return 200, {}


def confirm_email(url_hash: str) -> (int, dict):
    '''
    Подтверждение email

    Args:
        url_hash: хэш

    Returns:
        Код статуса и словарь данных
        200, {}
    '''

    logger.info(
        msg=f'Подтверждение email пользователя с хэшем: {url_hash}',
    )

    try:
        user = CustomUser.objects.filter(
            url_hash=url_hash,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибки при поиске пользователя с хэшем {url_hash} '
                f'для потвреждения email: {exc}',
        )
        return 500, {}

    if user is None:
        logger.error(
            msg=f'Не удалось найти пользователя с хэшем {url_hash} '
                'для подтвреждения email',
        )
        return 404, {}

    user.email_confirmed = True
    user.url_hash = None
    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось подтвердить email пользователя {user} '
                f'с хэшем {url_hash}: {exc}',
        )
        return 500, {}

    logger.info(
        msg=f'Успешно подтвержден email пользователя {user}',
    )
    return 200, {}


def password_restore_request(data: QueryDict, host: str) -> (int, dict):
    '''
    Запрос на восстановление пароля пользователя

    Args:
        data: данные пользователя
            {
              "email": "test@cc.com"
            }
        host: хост для создания полного url пути
                    используется в отправке писем

    Returns:
        Код статуса и словарь данных
        200, {}
    '''

    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Запрос на восстановление пароля пользователя c данными {user_data}',
    )

    serializer = PasswordRestoreRequestSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg='Невалидные данные для запроса на восстановление пароля '
                f'пользователя c данными {user_data}: {serializer.errors}',
        )
        return 400, {}

    validated_data = serializer.validated_data
    try:
        user = CustomUser.objects.filter(
            email=validated_data['email'],
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при поиске пользователя с данными {user_data} '
                f'для запроса на восстановление пароля: {exc}',
        )
        return 500, {}

    if user is None:
        logger.error(
            msg='При запросе на восстановление пароля не найден '
                f'пользователь с данными {user_data} '
        )
        return 404, {}

    status_code = send_user_email(
        user=user,
        email_type=PASSWORD_RESTORE,
        host=host,
    )
    if status_code != 200:
        logger.error(
            msg='Запрос на восстановление пароля пользователя '
                f'с данными {user_data} не прошел',
        )
    else:
        logger.info(
            msg='Запрос на сброс пароля пользователя '
                f'с данными {user_data} прошел успешно',
        )
    return status_code, {}


def password_restore(data: QueryDict, url_hash: str) -> (int, dict):
    '''
    Восстановление пароля пользователя

    Args:
        url_hash: хэш
        data: данные пользователя
            {
              "new_password": "new_password123",
              "confirm_password": "new_password123"
            }

    Returns:
        Код статуса и словарь данных
        200, {}
    '''

    logger.info(
        msg=f'Восстановление пароля пользователя с хэшем: {url_hash}',
    )

    try:
        user = CustomUser.objects.filter(
            url_hash=url_hash,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при поиске пользователя с хэшем {url_hash} '
                f'для восстановления пароля: {url_hash}'
        )
        return 500, {}

    if user is None:
        logger.error(
            msg=f'При восстановлении пароля не найден пользователь с хэшем: {url_hash}',
        )
        return 404, {}

    serializer = PasswordRestoreSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для восстановления пароля '
                f'пользователя {user} c хэшем {url_hash}: {serializer.errors}',
        )
        return 400, {}

    validated_data = serializer.validated_data
    user.set_password(validated_data['new_password'])
    user.url_hash = None
    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось восстановить пароль пользователя {user}: {exc}'
        )
        return 500, {}

    logger.info(
        msg=f'Успешно восстановлен пароль пользователя {user}',
    )
    return 200, {}


def detail(user: CustomUser) -> (int, dict):
    '''
    Данные пользователя

    Args:
        user: пользователь

    Returns:
        Код статуса и словарь данных
        200,
        {
            "email": "test@cc.com",
            "email_confirmed": True,
        }
    '''

    logger.info(
        msg=f'Получение данных пользователя {user}',
    )

    response_data = DetailSerializer(
        instance=user,
    ).data
    logger.info(
        msg=f'Данные пользователя {user} успешно получены: {response_data}',
    )
    return 200, response_data


def remove(user: CustomUser) -> (int, dict):
    '''
    Удаление пользователя

    Args:
        user: пользователь

    Returns:
        Код статуса и словарь данных
        200, {}
    '''

    email = user.email
    logger.info(
        msg=f'Удаление пользователя {email}',
    )

    try:
        user.delete()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось удалить пользователя {email}: {exc}',
        )
        return 500, {}

    logger.info(
        msg=f'Успешное удален пользователь {email}',
    )
    return 200, {}


def change_password(data: QueryDict, user: CustomUser) -> (int, dict):
    '''
    Смена пароля пользователя

    Args:
        data: данные пользователя
            {
              "old_password": "old_password123",
              "new_password": "new_password123",
              "confirm_password": "new_password123",
            }
        user: пользователь

    Returns:
        Код статуса и словарь данных
        200,
        {
            "email": "test@cc.com",
            "email_confirmed": True,
        }
    '''

    logger.info(
        msg=f'Смена пароля пользователя {user}',
    )

    serializer = ChangePasswordSerializer(
        instance=user,
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для смены пароля пользователя {user}: '
                f'{serializer.errors}',
        )
        return 400, {}

    validated_data = serializer.validated_data
    try:
        serializer.update(
            instance=user,
            validated_data=validated_data,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось сменить пароль пользователя {user}: {exc}',
        )
        return 500, {}

    logger.info(
        msg=f'Успешно изменен пароль пользователя {user}',
    )
    response_data = DetailSerializer(
        instance=user,
    ).data
    return 200, response_data


def send_user_email(user: CustomUser, email_type: str, host: str) -> int:
    '''
    Отправка письма по типу

    Args:
        user: пользователь
        email_type: тип письма
        host: хост для создания полного url пути
                    используется в отправке писем

    Returns:
        Код статуса
    '''

    logger.info(
        msg='Получение данных для формирования текста '
            f'письма {email_type} пользователю {user}',
    )

    url_hash = str(uuid.uuid4())
    user.url_hash = url_hash
    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить данные для формирования текста письма {email_type} '
                f'пользователю {user}: {exc}',
        )
        return 500

    path = reverse(email_type, args=(user.url_hash,))
    url = f'{SITE_PROTOCOL}://{host}{path}'
    mail_data = {
        'url': url,
    }

    logger.info(
        msg=f'Данные для формирования текста письма {email_type} '
            f'пользователю {user} получены: {mail_data}',
    )

    email = Email(
        email_type=email_type,
        mail_data=mail_data,
        recipient=user,
    )
    status = email.send()
    return status


def confirm_email_request(user: CustomUser, host: str) -> (int, dict):
    '''
    Запрос на отправку письма для подтверждения email

    Args:
        user: пользователь
        host: хост для создания полного url пути
                    используется в отправке писем

    Returns:
        Код статуса и словарь данных
        200, {}
    '''

    logger.info(
        msg=f'Запрос на отправку письма для подтверждения email '
            f'пользователя {user}',
    )

    status_code = send_user_email(
        user=user,
        email_type=CONFIRM_EMAIL,
        host=host,
    )
    if status_code != 200:
        logger.error(
            msg='Запрос на отправку письма для подтверждения email '
                f'пользователя {user} не прошел',
        )
    else:
        logger.info(
            msg='Запрос на отправку письма для подтверждения email '
                f'пользователя {user} прошел успешно',
        )
    return status_code, {}
