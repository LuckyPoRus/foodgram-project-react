from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.settings import (
    MAX_EMAIL_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_USER_NAME_LENGTH
)


class CustomUser(AbstractUser):
    email = models.EmailField(
        "Адрес электронной почты",
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        blank=False,
        null=False
    )

    first_name = models.CharField(
        "Имя",
        max_length=MAX_USER_NAME_LENGTH,
        blank=False
    )

    last_name = models.CharField(
        "Фамилия",
        max_length=MAX_USER_NAME_LENGTH,
        blank=False
    )

    password = models.CharField(
        "Пароль",
        max_length=MAX_PASSWORD_LENGTH,
        blank=False
    )

    REQUIRED_FIELDS = [
        "email",
        "first_name",
        "last_name",
        "password"
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscribing",
        verbose_name="Автор"
    )

    class Meta:
        constraints = [
            # Ограничение подписки на уже подписанного пользователя
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_subscription"
            ),
            # Проверка подписки на самого себя
            models.CheckConstraint(
                check=~models.Q(
                    user=models.F("author")
                ),
                name="user_author_not_equal",
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
