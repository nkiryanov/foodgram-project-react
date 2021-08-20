from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Count, Exists, OuterRef, Prefetch, Subquery
from django.utils.translation import gettext_lazy as _


class UserQuerySet(models.QuerySet):
    def with_subscriptions(self, user=None):
        """
        If user object provided annotates queryset with "is_subscribed" field.
        If user wasn't provided it still annotests with the field but it
        allways "False".
        """
        subquery = UserSubscription.objects.filter(
            follower=user,
            following_id=OuterRef("id"),
        )
        qs = self.annotate(is_subscribed=Exists(subquery))
        return qs

    def with_recipes_count(self):
        """Annotates queryset with amount of user's recipes."""
        qs = self.annotate(recipes_count=Count("recipes"))
        return qs

    def limit_recipes(self, count: int = None):
        """
        Prefetch user's list with their recipes.
        The number of user's recipes is limited with 'count'.
        If 'count' attribute is less than 0 then 0 recipes returns.
        """
        from ..recipes.models import Recipe

        count = 0 if count < 0 else count

        recipes = Recipe.objects.filter(author__id=OuterRef("author_id"))
        recipes_sliced_values_qs = recipes.values_list("id", flat=True)[:count]
        subquery_recipes_ids = Subquery(recipes_sliced_values_qs)
        recipes_sliced_qs = Recipe.objects.filter(id__in=subquery_recipes_ids)

        prefetch = Prefetch("recipes", queryset=recipes_sliced_qs)
        qs = self.prefetch_related(prefetch)
        return qs


class CustomUserManager(UserManager.from_queryset(UserQuerySet)):
    use_in_migrations = False


class User(AbstractUser):
    """Email field is required and it used for authentication."""

    email = models.EmailField(
        _("email address"),
        blank=False,
        unique=True,
    )

    objects = UserManager()
    ext_objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["id"]


class UserSubscription(models.Model):
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
        verbose_name = "Подписка на пользователя"
        verbose_name_plural = "Подписки на пользователя"

    def __str__(self):
        return (
            f"Подписка '{self.follower.username}' на пользователя "
            f"{self.following.username}"
        )
