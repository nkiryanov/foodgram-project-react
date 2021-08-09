from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..factories import UserFactory

URL_USERS_LIST = reverse("users-list")
URL_SUBSRIPRIONS_LIST = reverse("subscriptions-list")
URL_USER_DETAIL = reverse("users-detail", args=[1])


class UserURLTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()

        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    def url_returns_405_not_allowed_test_utility(
        self, client, url, method_names
    ):
        """Helper. Tests "url" for not allowed methods.

        It translates "methods_names" to correspond methods on "client" and
        asserts when error different from 405 (not allowed) returns.
        """

        for method_name in method_names:
            with self.subTest(method_name):
                client_method = getattr(client, method_name)
                response = client_method(url)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                    msg=(
                        f"Убедитесь, что для '{url}' "
                        f"метод '{method_name}' запрещен и возвращает "
                        f"правильный номер ошибки."
                    ),
                )
    
    def test_urls_unauthorized_client(self):
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
            URL_SUBSRIPRIONS_LIST,
        ]
        client = UserURLTests.authorized_client

        response = client.get(URL_USERS_LIST)

        for url in URLS_TO_TEST:
            with self.subTest(url):
                response = client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    msg = (
                        f"Авторизованный пользователь получает имеет доступ к "
                        f"{url}"
                    )
                )
