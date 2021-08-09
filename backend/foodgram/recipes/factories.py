import random

import factory
from django.contrib.auth import get_user_model
from foodgram.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
)

from .utils import cyrillic_slugify

User = get_user_model()


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
    It supports 'tags__num' and 'add_ingredients' values. If them passed
    creates recipes with that values.
    """

    class Meta:
        model = Recipe

    name = factory.Faker("sentence")
    author = factory.Iterator(User.objects.all())
    image = factory.django.ImageField(color=factory.Faker("color_name"))
    text = factory.Faker("text")
    cooking_time = factory.Faker("random_int", max=50)

    def _post_generation_helper():
        pass

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
    def add_ingredients(self, create, extracted, **kwargs):
        if not create:
            return

        at_least = 1

        how_many = extracted or at_least
        how_many = min(how_many, 20)

        ingredients = Ingredient.objects.order_by("?")[:how_many]

        for ingredient in ingredients:
            amount = random.randint(1, 100)
            RecipeIngredient.objects.create(
                recipe=self,
                ingredient=ingredient,
                amount=amount,
            )
