from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.db.models.expressions import Exists, OuterRef
from foodgram.core.utils import cyrillic_slugify

User = get_user_model()


class MeasurementUnit(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Единица измерения",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Единицы измерения"

    def __str__(self):
        return f"{self.name}"


class IngredientQuerySet(models.QuerySet):
    def user_cart(self, user=None):
        assert user is not None, "'user' is required attribute."

        qs = (
            self.filter(recipe__cart__user=user)
            .annotate(amount=Sum("recipeingredients__amount"))
            .select_related("measurement_unit")
            .order_by("name")
        )
        return qs


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название",
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.RESTRICT,
        related_name="ingredients",
        verbose_name="Единицы измерения",
    )

    objects = models.Manager()
    ext_objects = IngredientQuerySet.as_manager()

    class Meta:
        ordering = [
            "name",
        ]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, ({self.measurement_unit})"


class RecipeTag(models.Model):
    color = ColorField(default="#FF0000")
    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Тэг рецепта",
    )
    slug = models.SlugField(
        max_length=40,
        unique=True,
        verbose_name="Slug тега рецепта",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = cyrillic_slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = [
            "name",
        ]
        verbose_name = "Тег рецепта"
        verbose_name_plural = "Теги рецептов"


class RecipeQuerySet(models.QuerySet):
    def with_favorites(self, user=None):
        subquery = RecipeFavorite.objects.filter(
            user=user,
            recipe=OuterRef("id"),
        )
        qs = self.annotate(is_favorited=Exists(subquery))
        return qs

    def with_shopping_cart(self, user=None):
        subquery = RecipeCart.objects.filter(
            user=user,
            recipe=OuterRef("id"),
        )
        qs = self.annotate(is_in_shopping_cart=Exists(subquery))
        return qs


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Картинка",
    )
    text = models.TextField(
        max_length=1000,
        verbose_name="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4320),
        ],
    )
    tags = models.ManyToManyField(
        RecipeTag,
        related_name="recipes",
        verbose_name="Тег",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        db_index=True,
    )

    objects = models.Manager()
    ext_objects = RecipeQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=("author", "name"), name="Unique recipe per author"
            ),
        ]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipeingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        related_name="recipeingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200),
        ],
    )

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"


class RecipeFavorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="Unique RecipeFavorite per user and recipe",
            ),
        ]
        verbose_name = "Объект избранного"
        verbose_name_plural = "Объекты избранного"

    def __str__(self):
        return f"Избранное — '{self.recipe.name}' у '{self.user.username}'"


class RecipeCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Рецепт",
    )

    def __str__(self):
        return (
            f"Рецепт '{self.recipe.name}' из корзины покупок "
            f"у {self.user.username}"
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="Unique RecipeCart per user and recipe",
            ),
        ]
        verbose_name = "Объект корзины покупок"
        verbose_name_plural = "Объекты корзины покупок"
