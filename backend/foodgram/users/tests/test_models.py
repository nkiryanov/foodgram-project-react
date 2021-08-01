from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from foodgram.users.factories import UserFactory

User = get_user_model()


class UserModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        UserFactory(email="user1@email.ru")

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
