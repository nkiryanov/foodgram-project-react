from tempfile import mkdtemp as tempfile_mkdtemp

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, override_settings

from ...users.factories import UserFactory
from ..factories import (
    IngredientFactory,
    MeasurementUnitFactory,
    RecipeCartFactory,
    RecipeFactory,
    RecipeTagFactory,
)
from ..models import Recipe, RecipeFavorite

TEMP_DIR = tempfile_mkdtemp()

URL_RECIPES_LIST = reverse("recipes-list")
URL_RECIPES_DETAIL = reverse("recipes-detail", args=[1])
URL_DOWNLOAD_SHOPPING_CART = reverse("recipes-download-shopping-cart")
URL_TAGS_LIST = reverse("tags-list")
URL_INGREDIENTS_LIST = reverse("ingredients-list")

SMALL_GIF = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVB"
    "MVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCB"
    "yxOyYQAAAABJRU5ErkJggg=="
)

User = get_user_model()


class RecipeViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()
        cls.other_user = UserFactory()

        MeasurementUnitFactory.create_batch(5)
        IngredientFactory.create_batch(5)

        RecipeFactory.create_batch(10, author=cls.user)

        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    def test_urls_to_test_is_paginated(self):
        """Just look for 'next', 'previous', 'result' keys in responses."""
        URLS_TO_TEST = [
            URL_RECIPES_LIST,
        ]
        client = RecipeViewTests.authorized_client

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
        client = RecipeViewTests.unauthorized_client

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
        recipe = RecipeFactory(author=RecipeViewTests.other_user)
        client = RecipeViewTests.authorized_client
        recipe_favorite_url = reverse("recipes-favorite", args=[recipe.id])

        response = client.get(path=recipe_favorite_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=(
                "После добавления рецепта в избранное должен возвращаться "
                "успешный код."
            ),
        )

        is_recipe_favorite = RecipeFavorite.objects.filter(
            user=RecipeViewTests.user,
            recipe=recipe,
        ).exists()

        self.assertTrue(
            is_recipe_favorite,
            msg="Убедитесь, что рецепт попадает в избранное.",
        )

    def test_user_can_delete_favorite_recipe(self):
        """
        Sends 'DELETE' request to 'favorite' url and checks
            - status code
            - whether "RecipeFavorite" object was deleted
        """
        user = RecipeViewTests.user
        recipe = RecipeFactory(author=RecipeViewTests.other_user)
        RecipeFavorite.objects.create(
            user=user,
            recipe=recipe,
        )
        client = RecipeViewTests.authorized_client
        recipe_favorite_url = reverse("recipes-favorite", args=[recipe.id])

        response = client.delete(path=recipe_favorite_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=(
                "После удалени рецепта из избранного возвращается "
                "успешный код."
            ),
        )

        is_recipe_favorite = RecipeFavorite.objects.filter(
            user=RecipeViewTests.user,
            recipe=recipe,
        ).exists()

        self.assertFalse(
            is_recipe_favorite,
            msg="Убедитесь, что рецепт удаляется из избранного.",
        )

    def test_authorized_user_download_shopping_cart(self):
        recipe = RecipeFactory()
        user = RecipeViewTests.user
        RecipeCartFactory(user=user, recipe=recipe)

        client = RecipeViewTests.authorized_client
        response = client.get(
            path=URL_DOWNLOAD_SHOPPING_CART,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="Удачная загрузка должна возвращать код 200.",
        )

        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/pdf",
            msg="Содержимое документа должен быть документ PDF.",
        )

    def test_cant_download_empty_shopping_cart(self):
        """Download shopping cart should return 404 if list is empty."""
        client = RecipeViewTests.authorized_client
        response = client.get(path=URL_DOWNLOAD_SHOPPING_CART)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            msg="Пустой список покупок должен возвращать 404.",
        )


@override_settings(MEDIA_ROOT=TEMP_DIR)
class RecipeCreateViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        MeasurementUnitFactory.create_batch(5)

        cls.ingredient_1 = IngredientFactory()
        cls.ingredient_2 = IngredientFactory()
        cls.tag1 = RecipeTagFactory()
        cls.tag2 = RecipeTagFactory()

        cls.user = UserFactory()
        cls.name = "Простой рецепт"
        cls.text = "Описание рецепта длинное."

        cls.recipeingredient_1 = {"id": cls.ingredient_1.id, "amount": 10}
        cls.recipeingredient_2 = {"id": cls.ingredient_2.id, "amount": 10}

        cls.data = {
            "ingredients": [
                cls.recipeingredient_1,
                cls.recipeingredient_2,
            ],
            "tags": [cls.tag1.id],
            "image": SMALL_GIF,
            "name": "Простой рецепт",
            "text": "Описание рецепта длинное.",
            "cooking_time": "20",
        }

        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    def test_create_recipe(self):
        """
        Posts a recipe and checks response.status_code and recipes count in DB.
        """
        data = RecipeCreateViewTests.data
        client = RecipeCreateViewTests.authorized_client
        recipes_count_before_post = Recipe.objects.count()

        response = client.post(URL_RECIPES_LIST, data=data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=(
                f"Убедитесь, что при создании рецепта возвращается код 201."
                f"Ответ который получили {response.data}"
            ),
        )

        recipes_count_after_post = Recipe.objects.count()
        self.assertEqual(
            recipes_count_after_post,
            recipes_count_before_post + 1,
            msg="Всего должно стать +1 рецепт от первоначального значения.",
        )

    def test_recipe_without_tags_coudldn_be_created(self):
        """Posts recipe without tags. We should returns errors."""

        data = RecipeCreateViewTests.data
        data.pop("tags")
        recipes_count_before_post = Recipe.objects.count()
        client = RecipeCreateViewTests.authorized_client

        response = client.post(URL_RECIPES_LIST, data=data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=(
                f"Убедитесь, что при запросы без тега возвращают код 400."
                f"Ответ который получили {response.data}"
            ),
        )

        recipes_count_after_post = Recipe.objects.count()
        self.assertEqual(
            recipes_count_after_post,
            recipes_count_before_post,
            msg="Рецептов должно остаться прежнее количество.",
        )

    def test_recipe_without_ingredients_couldnt_be_created(self):
        """Posts recipe without ingredeints data. We should returns errors."""

        data = RecipeCreateViewTests.data
        data.pop("ingredients")
        recipes_count_before_post = Recipe.objects.count()
        client = RecipeCreateViewTests.authorized_client

        response = client.post(URL_RECIPES_LIST, data=data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=(
                f"Запросы без ингредиентов должны возвращать код 400."
                f"Ответ который получили {response.data}"
            ),
        )

        recipes_count_after_post = Recipe.objects.count()
        self.assertEqual(
            recipes_count_after_post,
            recipes_count_before_post,
            msg="Рецептов должно остаться прежнее количество.",
        )

    def test_recipe_with_same_name_and_author_couldnt_be_created(self):
        """
        1. Posts recipe with same name. We should return error.
        2. Posts recipe with different name and it should be ok.
        """
        author = RecipeCreateViewTests.user
        data = RecipeCreateViewTests.data
        name = data["name"]
        RecipeFactory(author=author, name=name)
        recipes_count_before_post = Recipe.objects.count()
        client = RecipeCreateViewTests.authorized_client

        response = client.post(URL_RECIPES_LIST, data=data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=(
                f"Запрос на создание рецепта с тем же именем должен вернуть "
                f"400. Ответ который получили {response.data}"
            ),
        )

        data["name"] = "Новое имя."
        response = client.post(URL_RECIPES_LIST, data=data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=(
                f"Запрос на создание рецепта с новым именем должен вернуть "
                f"ОК. Ответ который получили {response.data}"
            ),
        )

        recipes_count_after_post = Recipe.objects.count()
        self.assertEqual(
            recipes_count_after_post,
            recipes_count_before_post + 1,
            msg="Рецептов должно стать на 1 больше.",
        )

    def test_recipe_patch(self):
        """Patchs existed recipe with same new name."""
        author = RecipeCreateViewTests.user
        recipe = RecipeFactory(author=author, name="Старое имя")
        updated_data = {
            "ingredients": [
                RecipeCreateViewTests.recipeingredient_1,
            ],
            "tags": [RecipeCreateViewTests.tag2.id],
            "image": SMALL_GIF,
            "name": "Новое имя",
            "text": "НОВОЕ Описание рецепта длинное.",
            "cooking_time": "10",
        }
        client = RecipeCreateViewTests.authorized_client

        url_recipe_patch = reverse("recipes-detail", args=[recipe.id])

        response = client.patch(
            url_recipe_patch,
            data=updated_data,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="Запрос на изменение рецепта должен обработать успешно.",
        )

        recipe.refresh_from_db()
        self.assertEqual(
            recipe.name,
            "Новое имя",
            msg="Убедитесь, что данные обновляются в том же рецепте.",
        )

    def test_recipe_not_author_cant_patch_recipe(self):
        """Patchs existed recipe with same new name."""
        author = RecipeCreateViewTests.user
        other_user = UserFactory()
        recipe = RecipeFactory(author=author, name="Старое имя")
        updated_data = {
            "ingredients": [
                RecipeCreateViewTests.recipeingredient_1,
            ],
            "tags": [RecipeCreateViewTests.tag2.id],
            "image": SMALL_GIF,
            "name": "Новое имя",
            "text": "НОВОЕ Описание рецепта длинное.",
            "cooking_time": "10",
        }
        client = APIClient()
        client.force_authenticate(user=other_user)

        url_recipe_patch = reverse("recipes-detail", args=[recipe.id])

        response = client.patch(
            url_recipe_patch,
            data=updated_data,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg=(
                "Запрос на изменение рецепта пользователем отличным от "
                "должен возвращать ошибку 403."
            ),
        )

        recipe.refresh_from_db()
        self.assertEqual(
            recipe.name,
            "Старое имя",
            msg="Убедитесь, что данные в рецепте не изменены.",
        )
