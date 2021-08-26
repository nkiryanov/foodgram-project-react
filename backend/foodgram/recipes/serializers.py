from typing import Sequence

from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ..users.serializers import UserSerializer
from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = "__all__"
        read_only_fields = ["color", "name", "slug"]


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source="ingredient",
        slug_field="id",
        queryset=Ingredient.objects.all(),
    )
    name = serializers.SlugRelatedField(
        source="ingredient",
        slug_field="name",
        read_only=True,
    )
    measurement_unit = serializers.SlugRelatedField(
        source="ingredient.measurement_unit",
        slug_field="name",
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            "id",
            "name",
            "measurement_unit",
            "amount",
        ]


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source="ingredient",
        slug_field="id",
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            "id",
            "amount",
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """
    Simple recipes serializer but requires annotated queryset with
        - "is_favorited" field
        - "is_in_shopping_cart" filed
        - pass author to UserSerializer that requires:
            - "is_subscribed" field
    """

    author = UserSerializer()
    tags = RecipeTagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        source="recipeingredients",
        many=True,
    )
    is_favorited = serializers.BooleanField(
        read_only=True,
        default=False,
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False,
    )

    class Meta:
        model = Recipe
        fields = "__all__"


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating recipes."""

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.SlugRelatedField(
        slug_field="id",
        queryset=RecipeTag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientSerializer(
        source="recipeingredients",
        many=True,
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "author",
            "tags",
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=["author", "name"],
            ),
        ]

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                "Рецепт не может быть без тегов."
            )

        unique_tags = set(tags)
        if len(unique_tags) != len(tags):
            raise serializers.ValidationError(
                "Массиов тегов должен быть уникальным."
            )
        return tags

    def validate_ingredients(self, recipeingredients):
        if not recipeingredients:
            raise serializers.ValidationError(
                "Рецепт не может быть без ингредиентов."
            )

        not_unique_ingredients = [
            recipeingredient["ingredient"].id
            for recipeingredient in recipeingredients
        ]
        unique_ingredients = set(not_unique_ingredients)

        not_unique_ingredients_amount = len(not_unique_ingredients)
        unique_ingredients_amount = len(unique_ingredients)

        if unique_ingredients_amount != not_unique_ingredients_amount:
            raise serializers.ValidationError(
                "Каждый ингредиент в рецепте должен быть уникальным."
            )

        return recipeingredients

    def _save_related_objects(
        self,
        instance: Recipe,
        tags: Sequence[RecipeTag],
        recipeingredients: Sequence[RecipeIngredient],
    ) -> None:

        assert (
            instance is not None
            and tags is not None
            and recipeingredients is not None
        ), "каждый из параметров должен быть непустым."

        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        recipe_ingredients = (
            RecipeIngredient(
                recipe=instance,
                ingredient=recipeingredient["ingredient"],
                amount=recipeingredient["amount"],
            )
            for recipeingredient in recipeingredients
        )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        """
        Creates "Recipe" and sets tags and ingredients (recipeingredients) for
        it. Related objects (tags or ingredients) should be set, not be
        updated.
        """

        recipeingredients = validated_data.pop("recipeingredients")
        tags = validated_data.pop("tags")

        recipe = Recipe.objects.create(**validated_data)

        self._save_related_objects(
            instance=recipe,
            tags=tags,
            recipeingredients=recipeingredients,
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Assumes that the whole object provided. It doesn't support partial
        update and overide all related objects.
        """

        recipeingredients = validated_data.pop("recipeingredients")
        tags = validated_data.pop("tags")

        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        self._save_related_objects(
            instance=instance,
            tags=tags,
            recipeingredients=recipeingredients,
        )
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data
