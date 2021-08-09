from django.contrib.auth import get_user_model
from foodgram.recipes.filters import IngredientFilter, RecipeFilter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Ingredient, Recipe, RecipeFavorite, RecipeTag
from .serializers import (
    BaseRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeTagSerializer,
)

User = get_user_model()


class RecipeTagViewSet(ReadOnlyModelViewSet):
    queryset = RecipeTag.objects.all()
    serializer_class = RecipeTagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            user = None

        queryset = (
            Recipe.custom_objects.prefetch_related("ingredients")
            .prefetch_related("author__following")
            .prefetch_related("tags")
        )
        queryset = queryset.with_favorites(user=user)
        return queryset.order_by("-pub_date")

    @action(
        methods=["get", "delete"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe_to_favorite = self.get_object()

        is_favorite_exists = RecipeFavorite.objects.filter(
            user=request.user,
            recipe=recipe_to_favorite,
        ).exists()

        if request.method == "GET":
            if is_favorite_exists:
                raise NotAcceptable("Такой рецепт уже в избранном.")

            RecipeFavorite.objects.create(
                user=request.user,
                recipe=recipe_to_favorite,
            )

            serializer = BaseRecipeSerializer(recipe_to_favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if not is_favorite_exists:
                raise NotFound("Такого рецепта в избранном нет.")

            RecipeFavorite.objects.filter(
                user=request.user,
                recipe=recipe_to_favorite,
            ).delete()

            return Response(status=status.HTTP_201_CREATED)
