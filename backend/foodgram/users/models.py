from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Count, Exists, OuterRef
from django.utils.translation import gettext_lazy as _


class UserQuerySet(models.QuerySet):
    def with_follows(self, user=None):
        subquery = UserFollow.objects.filter(
            follower=user,
            following=OuterRef("id"),
        )
        qs = self.annotate(is_subscribed=Exists(subquery))
        return qs

    def with_recipes_count(self):
        qs = self.annotate(recipes_count=Count("recipes"))
        return qs


class User(AbstractUser):
    """Email field is required and it used for authentication."""

    email = models.EmailField(
        _("email address"),
        blank=False,
        unique=True,
    )

    extended_objects = UserManager.from_queryset(UserQuerySet)()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class UserFollow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Кто подписался",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="На кого подписался",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="Unique subscription per follower and author (following)",
            )
        ]
