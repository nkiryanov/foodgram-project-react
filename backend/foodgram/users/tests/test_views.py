from django.urls import reverse
from foodgram.users.models import UserSubscription
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..factories import UserFactory, UserSubscriptionFactory

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
        UserSubscriptionFactory(follower=user, following=user_who_follow)
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

    def test_user_can_subscribe_to_other_user(self):
        """
        Sends 'GET' request to 'subscribe' url and checks
            - status code
            - whether "UserSubscription" object was created
        """

        following = UserFactory()
        follower = UsersViewTests.user
        client = UsersViewTests.authorized_client
        url_subscribe_to_following_user = reverse(
            "users-subscribe",
            args=[following.id],
        )

        response = client.get(path=url_subscribe_to_following_user)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg="Удачная подписка на пользователя должна возвращать код 201.",
        )

        is_follower_follows_following = UserSubscription.objects.filter(
            follower=follower,
            following=following,
        ).exists()

        self.assertTrue(
            is_follower_follows_following,
            msg="Убедитесь, что удалось подписать и объект подписки создан.",
        )

    def test_user_can_unsubscribe_from_other_user(self):
        """
        Sends 'DELETE' request to 'subscribe' url and checks
            - status code
            - whether "UserSubscription" object was deleted
        """
        follower = UsersViewTests.user
        following = UserFactory()
        UserSubscriptionFactory(follower=follower, following=following)

        client = UsersViewTests.authorized_client
        url_subscribe_to_following_user = reverse(
            "users-subscribe",
            args=[following.id],
        )

        response = client.delete(path=url_subscribe_to_following_user)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            msg="Удачная отписка возвращает код 204.",
        )

        is_follower_follows_following = UserSubscription.objects.filter(
            follower=follower,
            following=following,
        ).exists()

        self.assertFalse(
            is_follower_follows_following,
            msg="Убедитесь, что объект подписки удален.",
        )

    def test_user_cant_subscribe_to_himself(self):
        """
        Sends 'GET' request to SELF 'subscribe' url and checks
            - status code
            - whether "UserSubscription" object was not created
        """

        follower = UsersViewTests.user
        following = follower
        client = UsersViewTests.authorized_client
        url_subscribe_to_following_user = reverse(
            "users-subscribe",
            args=[following.id],
        )

        response = client.get(path=url_subscribe_to_following_user)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg="Попытка подписаться на себя должна вернуть код 400.",
        )

        is_follower_follows_following = UserSubscription.objects.filter(
            follower=follower,
            following=following,
        ).exists()

        self.assertFalse(
            is_follower_follows_following,
            msg=(
                "Убедитесь, что при попытке подписать на себя не создается "
                "объект подписки."
            ),
        )

    def test_user_cant_subscribe_twice(self):
        """
        Sends 'GET' request to SELF 'subscribe' url and checks
            - status code
            - whether "UserSubscription" object was not created
        """

        follower = UsersViewTests.user
        following = UserFactory()
        UserSubscriptionFactory(follower=follower, following=following)

        client = UsersViewTests.authorized_client
        url_subscribe_to_following_user = reverse(
            "users-subscribe",
            args=[following.id],
        )

        response = client.get(path=url_subscribe_to_following_user)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg="При попытке подписаться дважды должен вернуться код 400.",
        )

        count_follower_follows_following = UserSubscription.objects.filter(
            follower=follower,
            following=following,
        ).count()

        self.assertEqual(
            count_follower_follows_following,
            1,
            msg="Убедитесь, что объект подписки есть, но только один.",
        )
