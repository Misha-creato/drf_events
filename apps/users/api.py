from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.doc import (
    Auth200Response,
    DefaultResponse,
    Register200Response,
    RefreshToken200Response,
    Logout200Response,
    ConfirmEmail200Response,
    ConfirmEmailRequest200Response,
    PasswordRestoreRequest200Response,
    PasswordRestore200Response,
    Detail200Response,
    ChangePassword200Response,
    Remove200Response,
)
from users.serializers import (
    RegisterSerializer,
    AuthSerializer,
    RefreshAndLogoutSerializer,
    PasswordRestoreRequestSerializer,
    PasswordRestoreSerializer,
    ChangePasswordSerializer,
)
from utils.response_patterns import (
    generate_response,
)

from users.services import (
    register,
    auth,
    refresh_token,
    logout,
    confirm_email,
    password_restore_request,
    password_restore,
    detail,
    change_password,
    remove,
    confirm_email_request,
)


class RegisterView(APIView):

    @extend_schema(
        request=RegisterSerializer,
        responses={
            200: Register200Response,
            201: DefaultResponse,
            400: DefaultResponse,
            406: DefaultResponse,
            500: DefaultResponse,
        },
        description=Register200Response.__doc__,
        summary='Регистрация пользователя',
    )
    def post(self, request):
        data = request.data
        host = request.get_host()
        status_code, response_data = register(
            data=data,
            host=host,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class AuthView(APIView):

    @extend_schema(
        request=AuthSerializer,
        responses={
            200: Auth200Response,
            400: DefaultResponse,
            401: DefaultResponse,
            500: DefaultResponse,
        },
        description=Auth200Response.__doc__,
        summary='Аутентификация пользователя',
    )
    def post(self, request):
        data = request.data
        status_code, response_data = auth(
            data=data,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class RefreshTokenView(APIView):

    @extend_schema(
        request=RefreshAndLogoutSerializer,
        responses={
            200: RefreshToken200Response,
            400: DefaultResponse,
            403: DefaultResponse,
            500: DefaultResponse,
        },
        description=RefreshToken200Response.__doc__,
        summary='Обновление токена пользователя',
    )
    def post(self, request):
        data = request.data
        status_code, response_data = refresh_token(
            data=data,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RefreshAndLogoutSerializer,
        responses={
            200: Logout200Response,
            400: DefaultResponse,
            500: DefaultResponse,
        },
        description=Logout200Response.__doc__,
        summary='Выход из системы пользователя',
    )
    def post(self, request):
        data = request.data
        user = request.user
        status_code, response_data = logout(
            data=data,
            user=user,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class ConfirmEmailView(APIView):

    @extend_schema(
        responses={
            200: ConfirmEmail200Response,
            404: DefaultResponse,
            500: DefaultResponse,
        },
        description=ConfirmEmail200Response.__doc__,
        summary='Подтверждение email пользователя',
    )
    def get(self, request, url_hash):
        status_code, response_data = confirm_email(
            url_hash=url_hash,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class ConfirmEmailRequestView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: ConfirmEmailRequest200Response,
            403: DefaultResponse,
            500: DefaultResponse,
            501: DefaultResponse,
        },
        description=ConfirmEmailRequest200Response.__doc__,
        summary='Запрос на подтверждение email пользователя',
    )
    def post(self, request):
        user = request.user
        host = request.get_host()
        status_code, response_data = confirm_email_request(
            user=user,
            host=host,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class PasswordRestoreRequestView(APIView):

    @extend_schema(
        request=PasswordRestoreRequestSerializer,
        responses={
            200: PasswordRestoreRequest200Response,
            400: DefaultResponse,
            403: DefaultResponse,
            404: DefaultResponse,
            500: DefaultResponse,
            501: DefaultResponse,
        },
        description=PasswordRestoreRequest200Response.__doc__,
        summary='Запрос на восстановление пароля пользователя',
    )
    def post(self, request):
        data = request.data
        host = request.get_host()
        status_code, response_data = password_restore_request(
            data=data,
            host=host,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class PasswordRestoreView(APIView):

    @extend_schema(
        request=PasswordRestoreSerializer,
        responses={
            200: PasswordRestore200Response,
            400: DefaultResponse,
            404: DefaultResponse,
            500: DefaultResponse,
        },
        description=PasswordRestore200Response.__doc__,
        summary='Восстановление пароля пользователя',
    )
    def post(self, request, url_hash):
        data = request.data
        status_code, response_data = password_restore(
            data=data,
            url_hash=url_hash,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )


class CustomUserView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: Detail200Response,
        },
        description=Detail200Response.__doc__,
        summary='Данные пользователя',
    )
    def get(self, request):
        user = request.user
        status_code, response_data = detail(
            user=user,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: ChangePassword200Response,
            400: DefaultResponse,
            500: DefaultResponse,
        },
        description=ChangePassword200Response.__doc__,
        summary='Смена пароля пользователя',
    )
    def post(self, request):
        data = request.data
        user = request.user
        status_code, response_data = change_password(
            data=data,
            user=user,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )

    @extend_schema(
        responses={
            200: Remove200Response,
            500: DefaultResponse,
        },
        description=Remove200Response.__doc__,
        summary='Удаление пользователя',
    )
    def delete(self, request):
        user = request.user
        status_code, response_data = remove(
            user=user,
        )
        status, data = generate_response(
            status_code=status_code,
            data=response_data,
        )
        return Response(
            status=status,
            data=data,
        )
