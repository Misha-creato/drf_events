from rest_framework import serializers

from utils.response_patterns import DefaultResponse


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


class Detail200Response(DefaultResponse):
    '''
    Получение детальных данных пользователя

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
