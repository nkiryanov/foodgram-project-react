import factory
from django.contrib.auth import get_user_model
from faker import Faker

from .models import UserFollow

User = get_user_model()
fake = Faker(["ru-RU"])


class UserFollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserFollow
        django_get_or_create = ["follower", "following"]

    follower = factory.Iterator(User.objects.all())
    following = factory.Iterator(User.objects.all())


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
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call.

        The method has been taken from factory_boy manual. Without it
        password for users is being created without HASH and doesn't work
        right.
        """

        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)
