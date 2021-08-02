from foodgram.recipes.models import Ingredient, RecipeTag
from foodgram.recipes.serializers import (
    IngredientSerializer,
    RecipeTagSerializer,
)
from rest_framework.viewsets import ReadOnlyModelViewSet


class RecipeTagViewSet(ReadOnlyModelViewSet):
    queryset = RecipeTag.objects.all()
    serializer_class = RecipeTagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
