from django.urls import path

from users.api import (
    RegisterView,
    AuthView,
    RefreshTokenView,
    LogoutView,
    ConfirmEmailView,
    PasswordRestoreRequestView,
    PasswordRestoreView,
    CustomUserView,
    ConfirmEmailRequestView,
)

from utils.constants import (
    PASSWORD_RESTORE,
    CONFIRM_EMAIL,
)


urlpatterns = [
    path(
        'register/',
        RegisterView.as_view(),
        name='register',
    ),
    path(
        'auth/',
        AuthView.as_view(),
        name='auth',
    ),
    path(
        'auth/refresh/',
        RefreshTokenView.as_view(),
        name='refresh_token',
    ),
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout',
    ),
    path(
        'confirm_email/request/',
        ConfirmEmailRequestView.as_view(),
        name='confirm_email_request',
    ),
    path(
        'confirm_email/<str:url_hash>/',
        ConfirmEmailView.as_view(),
        name=CONFIRM_EMAIL,
    ),
    path(
        'password_restore/<str:url_hash>/',
        PasswordRestoreView.as_view(),
        name=PASSWORD_RESTORE,
    ),
    path(
        'password_restore/request/',
        PasswordRestoreRequestView.as_view(),
        name='password_restore_request',
    ),
    path(
        '',
        CustomUserView.as_view(),
        name='custom_user',
    )
]
