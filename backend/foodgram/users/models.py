from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import (FIRST_NAME_LENGTH, LAST_NAME_LENGTH,
                        MAX_LENGTH_USERNAME, UPLOAD_TO_AVATARS)


class User(AbstractUser):
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        verbose_name="Имя пользователя",
        help_text="Имя пользователя",
    )
    email = models.EmailField(
        unique=True,
    )
    first_name = models.CharField(max_length=FIRST_NAME_LENGTH,
                                  verbose_name="Имя")
    last_name = models.CharField(max_length=LAST_NAME_LENGTH,
                                 verbose_name="Фамилия")
    avatar = models.ImageField(
        null=True,
        blank=True, upload_to=UPLOAD_TO_AVATARS, verbose_name="Аватарка"
    )
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True,
        verbose_name="groups",
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this user.",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
