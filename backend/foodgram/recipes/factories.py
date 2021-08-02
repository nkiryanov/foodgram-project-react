import random

import factory
from foodgram.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
)
from foodgram.users.factories import UserFactory


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    name = factory.Faker("sentence")
    author = factory.SubFactory(UserFactory)
    image = factory.django.ImageField(color=factory.Faker("color_name"))
    text = factory.Faker("text")
    cooking_time = factory.Faker("random_int", max=50)

    @factory.post_generation
    def add_tags(self, create, extracted, **kwargs):
        if not create:
            return

        tags_amount = random.randint(1, 3)
        tags = RecipeTag.objects.order_by("?")[:tags_amount]
        self.tags.add(*tags)


class RecipeIngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecipeIngredient

    recipe = factory.SubFactory(RecipeFactory)
    ingredient = factory.Iterator(Ingredient.objects.all())
    amount = factory.Faker(
        "pydecimal",  # noqa
        positive=True,
        left_digits=2,
        right_digits=1,
    )


class RecipeWithIngredientsFactory(RecipeFactory):
    recipe_ing_1 = factory.RelatedFactory(
        RecipeIngredientFactory,
        factory_related_name="recipe",
    )
    recipe_ing_2 = factory.RelatedFactory(
        RecipeIngredientFactory,
        factory_related_name="recipe",
    )


class RecipeTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecipeTag
