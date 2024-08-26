from rest_framework import serializers


class DefaultResponse(serializers.Serializer):
    message = serializers.CharField(
        default='Сообщение',
    )
    data = serializers.JSONField(
        default={},
    )


class Register200Response(DefaultResponse):
    '''
    Регистрация пользователя

    '''

    data = serializers.JSONField(
        default={
            'refresh': 'refresh_token',
            'access': 'access_token',
        }
    )


class Auth200Response(DefaultResponse):
    '''
    Аутентификация пользователя

    '''

    data = serializers.JSONField(
        default={
            'refresh': 'refresh_token',
            'access': 'access_token',
        }
    )


class RefreshToken200Response(DefaultResponse):
    '''
    Обновление токена пользователя

    '''

    data = serializers.JSONField(
        default={
            'refresh': 'refresh_token',
            'access': 'access_token',
        }
    )


class Logout200Response(DefaultResponse):
    '''
    Выход из системы пользователя

    '''


class ConfirmEmail200Response(DefaultResponse):
    '''
    Подтверждение email пользователя

    '''


class ConfirmEmailRequest200Response(DefaultResponse):
    '''
    Запрос на отправку письма для подтверждения email пользователя

    '''


class PasswordRestoreRequest200Response(DefaultResponse):
    '''
    Запрос на восстановление пароля пользователя

    '''


class PasswordRestore200Response(DefaultResponse):
    '''
    Восстановление пароля пользователя

    '''


class Detail200Response(DefaultResponse):
    '''
    Данные пользователя

    '''

    data = serializers.JSONField(
        default={
            "email": "test@cc.com",
            "email_confirmed": True,
        }
    )


class ChangePassword200Response(DefaultResponse):
    '''
    Изменение пароля пользователя

    '''

    data = serializers.JSONField(
        default={
            "email": "test@cc.com",
            "email_confirmed": True,
        }
    )


class Remove200Response(DefaultResponse):
    '''
    Удаление пользователя

    '''
