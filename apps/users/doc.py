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


class GoogleAuth200Response(DefaultResponse):
    '''
    Получение ссылки для авторизации пользователя через Google

    '''

    data = serializers.JSONField(
        default={
            "google_auth_url": "https://accounts.google.com/o/oauth2/v2/auth?"
                               "scope=https%3A//www.googleapis.com/auth/drive.metadata.readonly&"
                               "access_type=offline&"
                               "include_granted_scopes=true&"
                               "response_type=code&"
                               "state=state_parameter_passthrough_value&"
                               "redirect_uri=https%3A//oauth2.example.com/code&"
                               "client_id=client_id"
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
