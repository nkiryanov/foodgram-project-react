from rest_framework import serializers

from ..users import serializers as user_serializers
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
