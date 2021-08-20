import factory
from django.contrib.auth import get_user_model

from .models import UserSubscription

User = get_user_model()


class UserSubscriptionFactory(factory.django.DjangoModelFactory):
    """
    Picks rundom user object and set it as follower.
    After that picks other random user object (except self) and set it as
    following.
    """

    class Meta:
        model = UserSubscription
        django_get_or_create = ["follower", "following"]

    @factory.lazy_attribute
    def follower(self):
        return User.objects.order_by("?").first()

    @factory.lazy_attribute
    def following(self):

        following = (
            User.objects.exclude(id=self.follower.id).order_by("?").first()
        )
        return following


class UserFactory(factory.django.DjangoModelFactory):
    """
    Simple User factory that generates users by template:
        - username: user_0
        - email: user_0@foodgram.ru
        - first_name: random first name
        - last_name: randon last name
    """

    class Meta:
        model = User
        django_get_or_create = ["username", "email"]

    username = factory.Sequence(lambda n: f"user_{User.objects.count()}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@foodgram.ru")
    password = "Food2021"
    first_name = factory.Faker("first_name", locale="ru_RU")
    last_name = factory.Faker("last_name", locale="ru_RU")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call.

        The method has been taken from factory_boy manual. Without it
        password for users is being created without HASH and doesn't work
        right.
        """

        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)
