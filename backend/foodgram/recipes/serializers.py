from foodgram.users import serializers as user_serializers
from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeTag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    tags = RecipeTagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    author = user_serializers.UserSerializer()
    is_favorited = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
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


# class SubscriptionSerializer(user_serializers.UserSerializer):
#     recipes = BaseRecipeSerializer(many=True)
#     recipes_count = serializers.IntegerField()

#     class Meta(user_serializers.UserSerializer.Meta):
#         fields = user_serializers.UserSerializer.Meta.fields + (
#             "recipes",
#             "recipes_count",
#         )
