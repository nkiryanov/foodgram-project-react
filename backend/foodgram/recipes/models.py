from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class MeasurementUnit(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Единица измерения",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Единицы измерения"

    def __str__(self):
        return f"{self.name}"


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

    class Meta:
        ordering = [
            "name",
        ]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class RecipeTag(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Тэг рецепта",
    )
    color = ColorField(default="#FF0000")
    slug = models.SlugField(
        max_length=40, unique=True, verbose_name="Slug тега рецепта"
    )

    def __str__(self):
        return f"{self.name}"


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

    class Meta:
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=("author", "name"), name="unique_recipe_by_author"
            ),
        ]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        verbose_name="Ингредиент",
    )
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[
            MinValueValidator(0),
        ],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"


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
                name="unique_recipefavorite_by_user_and_recipe",
            ),
        ]
        verbose_name = "Объект избранного"
        verbose_name_plural = "Объекты избранного"

    def __str__(self):
        return f"Избранный {self.recipe} у {self.user}"
