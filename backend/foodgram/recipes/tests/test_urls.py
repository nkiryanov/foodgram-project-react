from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ...users.factories import UserFactory
from ..factories import (
    IngredientFactory,
    MeasurementUnitFactory,
    RecipeFactory,
    RecipeTagFactory,
)

URL_RECIPES_LIST = reverse("recipes-list")
URL_RECIPES_DETAIL = reverse("recipes-detail", args=[1])
URL_TAGS_LIST = reverse("tags-list")
URL_INGREDIENTS_LIST = reverse("ingredients-list")


class RecipesURLTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        MeasurementUnitFactory.create_batch(5)
        IngredientFactory.create_batch(10)
        RecipeTagFactory.create_batch(3)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()

        RecipeFactory.create_batch(10, author=cls.user)

        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    def test_unauthorized_client_allowed_urls(self):
        """Unauthorized users should returns 200 for urls in 'URLS_TO_TEST'."""
        URLS_TO_TEST = [
            URL_RECIPES_LIST,
            URL_TAGS_LIST,
            URL_INGREDIENTS_LIST,
            URL_RECIPES_DETAIL,
        ]
        client = RecipesURLTests.unauthorized_client

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
        URL_RECIPES_FAVORITE = reverse("recipes-favorite", args=[1])

        URLS_TO_TEST = [
            URL_RECIPES_FAVORITE,
        ]
        client = RecipesURLTests.unauthorized_client

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
            URL_RECIPES_LIST,
            URL_TAGS_LIST,
            URL_INGREDIENTS_LIST,
            URL_RECIPES_DETAIL,
        ]
        client = RecipesURLTests.authorized_client

        for url in URLS_TO_TEST:
            with self.subTest(url):
                response = client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    msg=(
                        f"Авторизованный пользователь имеет доступ к '{url}'"
                    ),
                )
