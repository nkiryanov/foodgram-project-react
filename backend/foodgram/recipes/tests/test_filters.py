from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from ...users.factories import UserFactory
from ..factories import (
    IngredientFactory,
    MeasurementUnitFactory,
    RecipeCartFactory,
    RecipeFactory,
    RecipeFavoriteFactory,
    RecipeTagFactory,
)

URL_RECIPES_LIST = reverse("recipes-list")
URL_RECIPES_DETAIL = reverse("recipes-detail", args=[1])
URL_TAGS_LIST = reverse("tags-list")
URL_INGREDIENTS_LIST = reverse("ingredients-list")


class RecipesFilterTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        MeasurementUnitFactory.create_batch(5)
        IngredientFactory.create_batch(10)

        cls.user = UserFactory()
        cls.tag1 = RecipeTagFactory(slug="tag1")
        cls.tag2 = RecipeTagFactory(slug="tag2")
        cls.tag3 = RecipeTagFactory(slug="tag3")

        RecipeFactory.create_batch(
            3,
            author=cls.user,
            tags=[cls.tag1],
        )
        RecipeFactory.create_batch(
            5,
            author=cls.user,
            tags=[cls.tag2],
        )
        RecipeFactory.create_batch(
            10,
            author=cls.user,
            tags=[cls.tag3],
        )

        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    def test_authorized_user_recipes_tags_filter(self):
        """Result is filtered by tags."""
        client = RecipesFilterTests.authorized_client
        query_params = {"tags": "tag1"}

        response_data = client.get(URL_RECIPES_LIST, query_params).data
        count = response_data.get("count")
        self.assertEqual(
            count,
            3,
            msg=(
                "Авторизованный пользователь: проверьте фильтрацию по одному "
                "тэгу."
            ),
        )

        query_part_url = "?tags=tag1&tags=tag2"

        response_data = client.get(URL_RECIPES_LIST + query_part_url).data
        count = response_data.get("count")
        self.assertEqual(
            count,
            8,
            msg=(
                "Авторизованный пользователь: проверьте фильтрацию по 2 тэгам."
                "В выборку не должны попадать другие рецепты с 3-им тегом."
            ),
        )

    def test_authorized_user_recipes_is_in_shopping_cart_filter(self):
        """Count objects in response. Should match to cart objects."""
        user = RecipesFilterTests.user
        client = RecipesFilterTests.authorized_client
        query_params = {"is_in_shopping_cart": True}

        response_data = client.get(URL_RECIPES_LIST, query_params).data
        count = response_data.get("count")
        self.assertEqual(
            count,
            0,
            msg=(
                "Когда корзина пустая количество объектов должно быть "
                "равно 0."
            ),
        )

        RecipeCartFactory.create_batch(7, user=user)

        response_data = client.get(URL_RECIPES_LIST, query_params).data
        count = response_data.get("count")
        self.assertEqual(
            count, 7, msg="Создали 7 объектов в корзине. Должны их возвращать."
        )

    def test_authorized_user_recipes_is_favorited_filter(self):
        """Count objects in response. Should match favorites objects."""
        user = RecipesFilterTests.user
        client = RecipesFilterTests.authorized_client
        query_params = {"is_favorited": True}

        response_data = client.get(URL_RECIPES_LIST, query_params).data
        count = response_data.get("count")

        self.assertEqual(
            count,
            0,
            msg="Избранное пусто. Количество объектов должно быть равно 0.",
        )

        RecipeFavoriteFactory.create_batch(2, user=user)
        response_data = client.get(URL_RECIPES_LIST, query_params).data
        count = response_data.get("count")

        self.assertEqual(
            count,
            2,
            msg="Создали 2 объектов в избранном. Должны их возвращать.",
        )

    def test_unauthorized_user_recipes_author_filter(self):
        """Creates user in count objects in response while filtering."""
        other_user = UserFactory()
        client = RecipesFilterTests.unauthorized_client
        query_params = {"author": other_user.id}

        response_data = client.get(URL_RECIPES_LIST, query_params).data
        count = response_data.get("count")
        self.assertEqual(
            count,
            0,
            msg="Рецептов пользователя нет. Должны вернуть 0 объектов.",
        )

        RecipeFactory.create_batch(11, author=other_user)
        response_data = client.get(URL_RECIPES_LIST, query_params).data
        count = response_data.get("count")
        self.assertEqual(
            count, 11, msg="Создали 11 рецептов. Все они должны быть в ответе."
        )


class IngredientsFilterTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        MeasurementUnitFactory.create_batch(5)
        IngredientFactory(name="анаша")
        IngredientFactory(name="панаша")
        IngredientFactory(name="горох")

        cls.unauthorized_client = APIClient()

    def test_ingredients_name_filter_returns_filtered_objects(self):
        """
        Ingredient filterset should not return ingredients that don't match
        filtered criteria.
        """
        client = IngredientsFilterTests.unauthorized_client
        query_params = {"name": "ана"}

        response_data = client.get(URL_INGREDIENTS_LIST, query_params).data
        filtered_ingredients_count = len(response_data)
        self.assertEqual(
            filtered_ingredients_count,
            2,
            msg="Убедитесь, что фильтр по ингредиентам работает.",
        )

    def test_ingredients_name_filter_ordering(self):
        """
        Ingredient filterset should order ingredients that start with
        provided value first.
        """
        client = IngredientsFilterTests.unauthorized_client
        query_params = {"name": "ана"}

        response_data = client.get(URL_INGREDIENTS_LIST, query_params).data
        first_ingredient = response_data[0]
        self.assertEqual(
            first_ingredient["name"],
            "анаша",
            msg="Убедитесь, что фильтр по ингредиентам работает.",
        )
