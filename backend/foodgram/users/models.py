from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Email field is required and it used for authentication."""

    email = models.EmailField(
        _("email address"),
        blank=False,
        unique=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Кто подписался",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="На кого подписался",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="Unique subscription per user and author",
            )
        ]
