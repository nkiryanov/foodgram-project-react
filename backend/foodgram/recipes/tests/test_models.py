from django.core.exceptions import ValidationError
from django.test import TestCase

from ...users.factories import UserFactory
from ..factories import (
    IngredientFactory,
    MeasurementUnitFactory,
    RecipeCartFactory,
    RecipeFactory,
    RecipeFavoriteFactory,
    RecipeTagFactory,
)
from ..models import Recipe


class RecipeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user_1 = UserFactory(email="user_1@email.ru")
        cls.user_2 = UserFactory(email="user_2@email.ru")

        MeasurementUnitFactory.create_batch(5)
        RecipeTagFactory.create_batch(3)

        cls.ingredient_1 = IngredientFactory(name="колбаса")
        cls.ingredient_2 = IngredientFactory(name="землица")

        cls.user_1_recipes = RecipeFactory.create_batch(
            10, author=cls.user_1, ingredients=[cls.ingredient_1]
        )

    def test_is_favorited_attribute(self):
        """Queryset should have "is_favorited" attribute."""
        user = RecipeModelTest.user_1
        recipe = Recipe.ext_objects.with_favorites(user=user).first()

        self.assertTrue(
            hasattr(recipe, "is_favorited"),
            msg="Рецепт должен иметь атрибут 'is_favorited'.",
        )
        self.assertFalse(
            recipe.is_favorited,
            msg="Рецепт не добавляли в избранное. Проверьте значение.",
        )

    def test_is_in_shopping_cart_attribute(self):
        """Queryset should have "is_in_shopping_cart" attribute."""
        user = RecipeModelTest.user_1
        recipe = Recipe.ext_objects.with_shopping_cart(user=user).first()

        self.assertTrue(
            hasattr(recipe, "is_in_shopping_cart"),
            msg="Рецепт должен иметь атрибут 'is_in_shopping_cart'.",
        )
        self.assertFalse(
            recipe.is_in_shopping_cart,
            msg="Рецепт не добавляли в корзину покупок. Проверьте значение.",
        )

    def test_is_favorited_value(self):
        """Recipe in favorites should have attribute 'is_favorite' = True."""

        user = RecipeModelTest.user_1
        recipe_1 = RecipeFactory(name="Рецепт который в избранном")
        RecipeFavoriteFactory(recipe=recipe_1, user=user)
        recipe_2 = RecipeFactory(name="Рецепт НЕ в избранном")

        favorite_recipe = Recipe.ext_objects.with_favorites(user=user).get(
            name=recipe_1.name
        )

        self.assertTrue(
            favorite_recipe.is_favorited,
            msg="Рецепт в избранном должен иметь атрибут 'True'.",
        )

        not_favorite_recipe = Recipe.ext_objects.with_favorites(user=user).get(
            name=recipe_2.name
        )

        self.assertFalse(
            not_favorite_recipe.is_favorited,
            msg="Рецепт НЕ в избранном должен иметь атрибут 'False'.",
        )

    def test_is_in_shopping_cart_value(self):
        """
        Recipe in shopping cart should have attribute
        'is_in_shopping_cart' = True.
        """

        user = RecipeModelTest.user_1
        recipe_1 = RecipeFactory(name="Рецепт в корзине покупок.")
        RecipeCartFactory(recipe=recipe_1, user=user)
        recipe_2 = RecipeFactory(name="Рецепт НЕ в корзине покупок.")

        in_shopping_cart_recipe = Recipe.ext_objects.with_shopping_cart(
            user=user
        ).get(name=recipe_1.name)

        self.assertTrue(
            in_shopping_cart_recipe.is_in_shopping_cart,
            msg="Рецепт в корзине покупок должен иметь атрибут 'True'.",
        )

        not_in_shopping_cart_recipe = Recipe.ext_objects.with_shopping_cart(
            user=user
        ).get(name=recipe_2.name)

        self.assertFalse(
            not_in_shopping_cart_recipe.is_in_shopping_cart,
            msg="Рецепт НЕ в избранном должен иметь атрибут 'False'.",
        )

    def test_recipe_author_and_name_is_unique(self):
        """Tries to clean the recipe with existed author and name."""
        user = RecipeModelTest.user_1
        RecipeFactory(author=user, name="Рецепт с каким-то именем.")

        recipe_with_same_author_and_name = RecipeFactory.build(
            author=user, name="Рецепт с каким-то именем."
        )

        with self.assertRaises(
            ValidationError,
            msg=(
                "Убедитесь, что нельзя создать рецепт с одинаковым"
                "'author' и 'name'."
            ),
        ):
            recipe_with_same_author_and_name.full_clean()

    def test_recipe_favorite_user_and_recipe_is_unique(self):
        """Tries to clean the favorite with same user and recipe."""
        user = RecipeModelTest.user_1
        recipe = RecipeFactory()

        RecipeFavoriteFactory(
            user=user,
            recipe=recipe,
        )

        same_favorite_recipe_per_author = RecipeFavoriteFactory.build(
            user=user,
            recipe=recipe,
        )

        with self.assertRaises(
            ValidationError,
            msg=(
                "Убедитесь, что нельзя создать добавить рецепт в избранное"
                "для одного пользователя дважды."
            ),
        ):
            same_favorite_recipe_per_author.full_clean()

    def test_recipe_in_shopping_cart_user_and_recipe_is_unique(self):
        """
        Tries to clean the recipe in shopping cart with same user and recipe.
        """
        user = RecipeModelTest.user_1
        recipe = RecipeFactory()

        RecipeCartFactory(
            user=user,
            recipe=recipe,
        )

        same_in_shopping_cart_recipe_per_author = RecipeCartFactory.build(
            user=user,
            recipe=recipe,
        )

        with self.assertRaises(
            ValidationError,
            msg=(
                "Убедитесь, что нельзя создать добавить рецепт в корзину"
                "для одного пользователя дважды."
            ),
        ):
            same_in_shopping_cart_recipe_per_author.full_clean()
