from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Email field is required and it used for authentication."""

    email = models.EmailField(_("email address"), blank=False, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
