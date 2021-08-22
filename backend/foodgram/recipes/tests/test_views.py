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
from ..models import Recipe, RecipeCart, RecipeFavorite

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

    def test_user_can_add_recipe_as_favorite(self):
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
            status.HTTP_204_NO_CONTENT,
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

    def test_non_existend_favorite_recipe_couldnt_be_deleted(self):
        """
        Tries to delete form favorites the recipe that actually not in
        favorites. 404 exception have to be raised.
        """
        recipe = RecipeFactory(author=RecipeViewTests.other_user)
        client = RecipeViewTests.authorized_client
        recipe_favorite_url = reverse("recipes-favorite", args=[recipe.id])

        response = client.delete(path=recipe_favorite_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            msg=(
                "Попытка удалить из избранного рецепт, которого там нет "
                "должна возвращать 404."
            ),
        )

    def test_user_can_add_recipe_in_shopping_cart(self):
        """
        Sends 'GET' request to 'shopping_cart' url and checks
            - status code
            - whether "RecipeCart" object was created
        """
        recipe = RecipeFactory(author=RecipeViewTests.other_user)
        client = RecipeViewTests.authorized_client
        recipe_shopping_cart_url = reverse(
            "recipes-shopping-cart",
            args=[recipe.id],
        )

        response = client.get(path=recipe_shopping_cart_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=(
                "После добавления рецепта в корзину должен возвращаться "
                "успешный код."
            ),
        )

        is_recipe_in_shopping_cart = RecipeCart.objects.filter(
            user=RecipeViewTests.user,
            recipe=recipe,
        ).exists()

        self.assertTrue(
            is_recipe_in_shopping_cart,
            msg="Убедитесь, что рецепт попадает в корзину покупок.",
        )

    def test_user_can_delete_recipe_from_shopping_cart(self):
        """
        Sends 'DELETE' request to 'shopping_cart' url and checks
            - status code
            - whether "RecipeCart" object was deleted
        """
        user = RecipeViewTests.user
        recipe = RecipeFactory(author=RecipeViewTests.other_user)
        RecipeCartFactory(
            user=user,
            recipe=recipe,
        )
        client = RecipeViewTests.authorized_client
        recipe_shopping_cart_url = reverse(
            "recipes-shopping-cart",
            args=[recipe.id],
        )

        response = client.delete(path=recipe_shopping_cart_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            msg=(
                "После удалени рецепта из корзины возвращается "
                "успешный код."
            ),
        )

        is_recipe_favorite = RecipeCart.objects.filter(
            user=RecipeViewTests.user,
            recipe=recipe,
        ).exists()

        self.assertFalse(
            is_recipe_favorite,
            msg="Убедитесь, что рецепт удаляется из корзины.",
        )

    def test_non_existend_in_shopping_cart_recipe_couldnt_be_deleted(self):
        """
        Tries to delete form shopping cart the recipe that actually not in
        shopping cart. 404 exception have to be raised.
        """
        recipe = RecipeFactory(author=RecipeViewTests.other_user)
        client = RecipeViewTests.authorized_client
        recipe_shopping_cart_url = reverse(
            "recipes-shopping-cart",
            args=[recipe.id],
        )

        response = client.delete(path=recipe_shopping_cart_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            msg=(
                "При попытке удалить из корзины покупок рецепт, которого "
                "там нет, должен возвращаться код 404."
            ),
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

    def test_recipes_has_right_fields(self):
        """Result has all expected fields.

        Be aware that nested objects fields will be tested in its own test.
        They are:
            - tags
            - author
            - ingredients
        """

        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]
        client = RecipeViewTests.authorized_client

        response = client.get(path=URL_RECIPES_LIST).data
        result = response.get("results")[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in result, msg=f"Нет поля {field}")

    def test_recipe_author_has_right_fields(self):
        """Nested author has to have all expected fields."""

        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        client = RecipeViewTests.authorized_client

        response = client.get(path=URL_RECIPES_LIST).data
        result = response.get("results")[0]
        author = result.get("author")
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in author, msg=f"Нет поля {field}")

    def test_recipe_ingredient_has_right_fields(self):
        """Nested ingredient has to have all expected fields."""

        fields = [
            "id",
            "name",
            "measurement_unit",
            "amount",
        ]
        client = RecipeViewTests.authorized_client

        response = client.get(path=URL_RECIPES_LIST).data
        result = response.get("results")[0]
        ingredient = result.get("ingredients")[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in ingredient, msg=f"Нет поля {field}")


@override_settings(MEDIA_ROOT=TEMP_DIR)
class RecipeCreateViewTests(APITestCase):
    def setUp(self) -> None:
        MeasurementUnitFactory.create_batch(5)

        self.ingredient_1 = IngredientFactory()
        self.ingredient_2 = IngredientFactory()
        self.tag1 = RecipeTagFactory()
        self.tag2 = RecipeTagFactory()

        self.user = UserFactory()
        self.name = "Простой рецепт"
        self.text = "Описание рецепта длинное."

        self.recipeingredient_1 = {"id": self.ingredient_1.id, "amount": 10}
        self.recipeingredient_2 = {"id": self.ingredient_2.id, "amount": 10}

        self.data = {
            "ingredients": [
                self.recipeingredient_1,
                self.recipeingredient_2,
            ],
            "tags": [self.tag1.id],
            "image": SMALL_GIF,
            "name": "Простой рецепт",
            "text": "Описание рецепта длинное.",
            "cooking_time": "20",
        }

        self.unauthorized_client = APIClient()
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(user=self.user)

    def test_create_recipe(self):
        """
        Posts a recipe and checks response.status_code and recipes count in DB.
        """
        data = self.data
        client = self.authorized_client
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

    def test_recipe_without_tags_couldnt_be_created(self):
        """Posts recipe without tags. We should returns errors."""

        data = self.data
        data["tags"] = []
        recipes_count_before_post = Recipe.objects.count()
        client = self.authorized_client

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

        data = self.data
        data["ingredients"] = []
        recipes_count_before_post = Recipe.objects.count()
        client = self.authorized_client

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
        author = self.user
        data = self.data
        name = data["name"]
        RecipeFactory(author=author, name=name)
        recipes_count_before_post = Recipe.objects.count()
        client = self.authorized_client

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

    def test_recipe_with_duplicated_ingredients_couldnt_be_created(self):
        """
        Posts a recipe and duplicated ingredient (but with different amount).
        The recipe should not be created.
        """
        duplicate = {
            "id": self.ingredient_1.id,
            "amount": 20,
        }
        data = self.data
        data["ingredients"] = [
            self.recipeingredient_1,
            duplicate,
        ]
        client = self.authorized_client
        recipes_count_before_post = Recipe.objects.count()

        response = client.post(URL_RECIPES_LIST, data=data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=(
                f"Убедитесь, что не удается создать рецепт с дубликатами "
                f"ингредиентов. Ответ который получили {response.data}"
            ),
        )

        recipes_count_after_post = Recipe.objects.count()
        self.assertEqual(
            recipes_count_after_post,
            recipes_count_before_post,
            msg="Количество рецептов не должно измениться.",
        )

    def test_recipe_with_duplicated_tags_couldnt_be_created(self):
        """
        Posts a recipe and duplicated tags. The recipe should not be created.
        """
        data = self.data
        data["tags"] = [self.tag1.id, self.tag1.id]
        client = self.authorized_client
        recipes_count_before_post = Recipe.objects.count()

        response = client.post(URL_RECIPES_LIST, data=data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=(
                f"Убедитесь, что не удается создать рецепт с дубликатами "
                f"тэгов. Ответ который получили {response.data}"
            ),
        )

        recipes_count_after_post = Recipe.objects.count()
        self.assertEqual(
            recipes_count_after_post,
            recipes_count_before_post,
            msg="Количество рецептов не должно измениться.",
        )

    def test_recipe_patch(self):
        """Patchs existed recipe with same new name."""
        author = self.user
        recipe = RecipeFactory(author=author, name="Старое имя")
        updated_data = {
            "ingredients": [
                self.recipeingredient_1,
            ],
            "tags": [self.tag2.id],
            "image": SMALL_GIF,
            "name": "Новое имя",
            "text": "НОВОЕ Описание рецепта длинное.",
            "cooking_time": "10",
        }
        client = self.authorized_client

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
        author = self.user
        other_user = UserFactory()
        recipe = RecipeFactory(author=author, name="Старое имя")
        updated_data = {
            "ingredients": [
                self.recipeingredient_1,
            ],
            "tags": [self.tag2.id],
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
