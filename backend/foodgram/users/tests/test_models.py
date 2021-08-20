from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from ..factories import UserFactory
from ..models import UserSubscription

User = get_user_model()


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory(email="user1@email.ru")

    def test_email_is_required_field(self):
        user_without_email = User(username="user1", password="Qwe1232343")

        with self.assertRaises(
            ValidationError,
            msg="Убедитесь, что 'email' обязательное поле.",
        ):
            user_without_email.full_clean()

    def test_email_is_unique_field(self):
        user_with_existed_email = User(
            username="unique_username",
            password="SomePassword23",
            email="user1@email.ru",
        )

        with self.assertRaises(
            ValidationError,
            msg=(
                "Убедитесь, что нельзя создать пользователей с одинаковым"
                "'email'."
            ),
        ):
            user_with_existed_email.full_clean()

    def test_user_no_self_follow(self):
        """User should can not follow himsels."""
        user = UserModelTest.user
        constraint_name = "Unique subscription - prevent user follow himself"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            UserSubscription.objects.create(follower=user, following=user)
