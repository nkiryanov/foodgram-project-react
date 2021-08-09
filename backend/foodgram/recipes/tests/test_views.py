from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from ...users.factories import UserFactory
from ..factories import (
    IngredientFactory,
    MeasurementUnitFactory,
    RecipeFactory,
    RecipeTagFactory,
)
from ..models import RecipeFavorite

URL_RECIPES_LIST = reverse("recipes-list")
URL_RECIPES_DETAIL = reverse("recipes-detail", args=[1])
URL_TAGS_LIST = reverse("tags-list")
URL_INGREDIENTS_LIST = reverse("ingredients-list")


class RecipesViewTests(APITestCase):
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

    def test_urls_to_test_is_paginated(self):
        """Just look for 'next', 'previous', 'result' keys in responses."""
        URLS_TO_TEST = [
            URL_RECIPES_LIST,
        ]
        client = RecipesViewTests.authorized_client

        for url in URLS_TO_TEST:
            with self.subTest(url):
                response_data = client.get(path=url).data

                self.assertTrue("next" in response_data)
                self.assertTrue("previous" in response_data)
                self.assertTrue("results" in response_data)

    def test_custom_pagination_query_params(self):
        """
        Paginator has not default params. The tests verifies that the response
        is paginated. It checks 'previous' and 'next' links and the number
        of objects in response.
        """
        query_params = {
            "page": 1,
            "limit": 2,
        }
        client = RecipesViewTests.unauthorized_client

        response_data = client.get(
            path=URL_RECIPES_LIST,
            data=query_params,
        ).data
        results = response_data.get("results")
        previous = response_data.get("previous")
        next = response_data.get("next")

        self.assertEqual(
            len(results),
            2,
            msg="В паджинированном ответе должно быть 2 объекта.",
        )
        self.assertEqual(
            previous,
            None,
            msg=(
                "В паджинированном ответе ссылка на предыдущую страницу "
                "должны быть 'null' (то есть пустая)."
            ),
        )
        self.assertNotEqual(
            next,
            None,
            msg=(
                "В паджинированном ответе должна быть ссылка на следующую "
                "страницу отличная от 'null' (непустая)."
            ),
        )

    def test_user_can_mark_recipe_as_favorite(self):
        """
        Sends 'GET' request to 'favorite' url and checks
            - status code
            - whether "RecipeFavorite" object was created
        """
        recipe = RecipeFactory()
        client = RecipesViewTests.authorized_client
        recipe_favorite_url = reverse("recipes-favorite", args=[recipe.id])

        response = client.get(path=recipe_favorite_url)
        self.assertEqual(
            response.status_code,
            201,
            msg=(
                "После добавления рецепта в избранное должен возвращаться "
                "успешный код."
            ),
        )

        is_recipe_favorite = RecipeFavorite.objects.filter(
            user=RecipesViewTests.user,
            recipe=recipe,
        ).exists()

        self.assertTrue(
            is_recipe_favorite,
            msg="Убедитесь, что рецепт попадает в избранное.",
        )

    def test_user_can_delete_favorite_recipe(self):
        user = RecipesViewTests.user
        recipe = RecipeFactory()
        RecipeFavorite.objects.create(
            user=user,
            recipe=recipe,
        )
        client = RecipesViewTests.authorized_client
        recipe_favorite_url = reverse("recipes-favorite", args=[recipe.id])

        response = client.delete(path=recipe_favorite_url)
        self.assertEqual(
            response.status_code,
            201,
            msg=(
                "После удалени рецепта из избранного возвращается "
                "успешный код."
            ),
        )

        is_recipe_favorite = RecipeFavorite.objects.filter(
            user=RecipesViewTests.user,
            recipe=recipe,
        ).exists()

        self.assertFalse(
            is_recipe_favorite,
            msg="Убедитесь, что рецепт удаляется из избранного.",
        )
