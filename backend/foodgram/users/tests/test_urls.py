from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..factories import UserFactory

URL_USERS_LIST = reverse("users-list")
URL_USERS_DETAIL = reverse("users-detail", args=[1])
URL_SUBSRIPRIONS_LIST = reverse("subscriptions-list")


class UserURLTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()

        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    def test_unauthorized_client_allowed_urls(self):
        """Unauthorized users should returns 200 for urls in 'URLS_TO_TEST'."""
        URLS_TO_TEST = [
            URL_USERS_DETAIL,
        ]
        client = UserURLTests.unauthorized_client

        for url in URLS_TO_TEST:
            with self.subTest(url):
                response = client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    msg=(
                        f"Проверьте что неавторизованный пользователь "
                        f"имеет доступ к '{url}'."
                    ),
                )

    def test_unauthorized_client_restricted_urls(self):
        """Unauthorized users should returns 401 for urls in 'URLS_TO_TEST'."""
        URLS_TO_TEST = [
            URL_USERS_LIST,
            URL_SUBSRIPRIONS_LIST,
        ]
        client = UserURLTests.unauthorized_client

        for url in URLS_TO_TEST:
            with self.subTest(url):
                response = client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                    msg=(
                        f"Проверьте что неавторизованный пользователь не "
                        f"имеет доступ к '{url}'."
                    ),
                )

    def test_urls_authorized_client(self):
        """Authorized users should returns 200 for urls in 'URLS_TO_TEST'."""
        URLS_TO_TEST = [
            URL_USERS_LIST,
            URL_USERS_DETAIL,
            URL_SUBSRIPRIONS_LIST,
        ]
        client = UserURLTests.authorized_client

        for url in URLS_TO_TEST:
            with self.subTest(url):
                response = client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    msg=(
                        f"Авторизованный пользователь получает имеет доступ к "
                        f"{url}"
                    ),
                )
