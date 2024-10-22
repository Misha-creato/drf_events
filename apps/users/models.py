from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError('Требуется электронная почта')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(raw_password=password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str):
        return self.create_user(
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    is_superuser = models.BooleanField(
        verbose_name='Статус суперпользователя',
        default=False
    )
    is_staff = models.BooleanField(
        verbose_name='Статус персонала',
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name='Статус активности',
        default=True,
    )
    email_confirmed = models.BooleanField(
        verbose_name='Адрес электронной почты подтвержден',
        default=False,
    )
    url_hash = models.CharField(
        verbose_name='Хэш',
        max_length=128,
        null=True,
        blank=True,
    )
    date_joined = models.DateTimeField(
        verbose_name='Дата регистрации',
        auto_now_add=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
