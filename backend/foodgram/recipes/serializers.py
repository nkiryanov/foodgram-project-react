from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

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


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]


class RecipeSerializer(serializers.ModelSerializer):
    tags = RecipeTagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = "__all__"


class CreateRecipeRecipeIngredientSerializer(serializers.ModelSerializer):
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


class CreateRecipeRecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = ["id"]


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        slug_field="id",
        queryset=RecipeTag.objects.all(),
        many=True,
    )
    ingredients = CreateRecipeRecipeIngredientSerializer(
        many=True,
        write_only=True,
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user

        recipe_ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=recipe_ingredient["ingredient"],
                amount=recipe_ingredient["amount"],
            )
            for recipe_ingredient in recipe_ingredients
        )

        return recipe
