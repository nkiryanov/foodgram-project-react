from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from ..factories import UserFactory, UserFollowFactory

URL_USERS_LIST = reverse("users-list")
URL_SUBSRIPRIONS_LIST = reverse("subscriptions-list")
URL_USER_DETAIL = reverse("users-detail", args=[1])


class UsersViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()

        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    def test_urls_to_test_is_paginated(self):
        """Just look for 'next', 'previous', 'result' keys in responses."""
        URLS_TO_TEST = [
            URL_USERS_LIST,
            URL_SUBSRIPRIONS_LIST,
        ]
        client = UsersViewTests.authorized_client

        for url in URLS_TO_TEST:
            with self.subTest(url):
                response_data = client.get(path=url).data

                self.assertTrue("next" in response_data)
                self.assertTrue("previous" in response_data)
                self.assertTrue("results" in response_data)

    def test_users_has_right_fields(self):
        """Result has all expected fields."""
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        client = UsersViewTests.authorized_client

        response = client.get(URL_USERS_LIST).data
        result = response.get("results")[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in result, msg=f"Нет поля {field}")

    def test_following_user_has_is_subscribed_true_flag(self):
        """Users who user is follow has 'is_subscribed=true' value."""

        user = UsersViewTests.user
        user_who_follow = UserFactory()
        UserFollowFactory(follower=user, following=user_who_follow)
        client = UsersViewTests.authorized_client

        USER_DETAIL_URL = reverse("users-detail", args=[user_who_follow.id])
        response_data = client.get(USER_DETAIL_URL).data

        self.assertEqual(
            "True",
            str(response_data.get("is_subscribed")),
            msg=(
                "Проверьте, что у пользователей на которых "
                "пользователь подписан возвращается флаг "
                "'is_subscribed': true."
            ),
        )

    def test_not_followed_user_has_is_subscribed_false_flag(self):
        """Users who user is follow has 'is_subscribed=false' value."""

        not_followed_user = UserFactory()
        client = UsersViewTests.authorized_client

        USER_DETAIL_URL = reverse("users-detail", args=[not_followed_user.id])
        response_data = client.get(USER_DETAIL_URL).data

        self.assertEqual(
            "False",
            str(response_data.get("is_subscribed")),
            msg=(
                "Пользователь, на кого не подписан должен иметь флаг "
                "'is_subscribed': false ."
            ),
        )
