from django.contrib.auth import get_user_model
from foodgram.recipes.filters import IngredientFilter, RecipeFilter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Ingredient, Recipe, RecipeCart, RecipeFavorite, RecipeTag
from .serializers import (
    BaseRecipeSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
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
    permission_classes = [AllowAny]
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            user = None

        queryset = (
            Recipe.custom_objects.prefetch_related("ingredients")
            .prefetch_related("author")
            .prefetch_related("tags")
        )
        queryset = queryset.with_favorites(user=user).with_cart(user=user)
        return queryset.order_by("-pub_date")

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return RecipeCreateSerializer
        return RecipeSerializer

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response("ok", status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _recipe_action_template(self, request, pk=None, related_model=None):
        """Template for similar ViewSet actions."""

        assert (
            related_model is not None
        ), "Связанная модель обязательный параметр."

        recipe = self.get_object()
        is_related_obj_exists = related_model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).exists()

        if request.method == "GET":
            if is_related_obj_exists:
                raise NotAcceptable("Такой рецепт у пользователя существует.")
            related_model.objects.create(
                user=request.user,
                recipe=recipe,
            )
            serializer = BaseRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if not is_related_obj_exists:
                raise NotFound("Такой рецепт у пользователя не найден.")
            related_model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            return Response(status=status.HTTP_201_CREATED)

    @action(
        methods=["get", "delete"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        related_model = RecipeFavorite
        return self._recipe_action_template(request, pk, related_model)

    @action(
        methods=["get", "delete"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        related_model = RecipeCart
        return self._recipe_action_template(request, pk, related_model)
