import random

import factory
from django.contrib.auth import get_user_model

from ..core.utils import cyrillic_slugify
from .models import (
    Ingredient,
    MeasurementUnit,
    Recipe,
    RecipeCart,
    RecipeFavorite,
    RecipeIngredient,
    RecipeTag,
)

User = get_user_model()


def add_ingredients(recipe, ingredients):
    for ingredient in ingredients:
        amount = random.randint(1, 50)
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=amount,
        )


class MeasurementUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MeasurementUnit
        django_get_or_create = ["name"]

    name = factory.Faker("text", max_nb_chars=50)


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient
        django_get_or_create = ["name"]

    name = factory.Faker("text", max_nb_chars=200)
    measurement_unit = factory.Iterator(MeasurementUnit.objects.all())


class RecipeTagFactory(factory.django.DjangoModelFactory):
    """Creates RecipeTags with random name and color."""

    class Meta:
        model = RecipeTag
        django_get_or_create = ["name", "slug"]

    name = factory.Faker("word")
    color = factory.Faker("color_name")
    slug = factory.LazyAttribute(lambda obj: cyrillic_slugify(obj.name))


class RecipeFactory(factory.django.DjangoModelFactory):
    """Rely on User and RecipeTag and Ingredient objects.

    Creates recipe with at least one tag and ingredient.
    It supports 'tags__num' and 'ingredients__num' values. If them passed
    creates recipes with that values.
    """

    class Meta:
        model = Recipe

    name = factory.Faker("sentence")
    author = factory.Iterator(User.objects.all())
    image = factory.django.ImageField(color=factory.Faker("color_name"))
    text = factory.Faker("text", max_nb_chars=1000)
    cooking_time = factory.Faker("random_int", max=50)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            tags = extracted
            self.tags.add(*tags)
            return

        at_least = 1
        num = kwargs.get("num", None)
        how_many = num or at_least

        tags_count = RecipeTag.objects.count()
        how_many = min(tags_count, how_many)

        tags = RecipeTag.objects.order_by("?")[:how_many]
        self.tags.add(*tags)

    @factory.post_generation
    def ingredients(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            ingredients = extracted
            add_ingredients(self, ingredients)
            return

        at_least = 1
        num = kwargs.get("num", None)
        how_many = num or at_least

        ingredients_count = Ingredient.objects.count()
        how_many = min(ingredients_count, how_many)

        ingredients = Ingredient.objects.order_by("?")[:how_many]
        add_ingredients(self, ingredients)


class RecipeCartFactory(factory.django.DjangoModelFactory):
    """Relates on User on Recipe objects. Be sure there are enough in DB."""

    class Meta:
        model = RecipeCart

    user = factory.Iterator(User.objects.all())
    recipe = factory.Iterator(Recipe.objects.all())


class RecipeFavoriteFactory(factory.django.DjangoModelFactory):
    """Relates on User on Recipe objects. Be sure there are enough in DB."""

    class Meta:
        model = RecipeFavorite

    user = factory.Iterator(User.objects.all())
    recipe = factory.Iterator(Recipe.objects.all())
