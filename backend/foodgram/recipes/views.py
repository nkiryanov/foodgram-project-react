from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable, NotFound
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from xhtml2pdf import pisa

from ..users.permissions import IsAuthor, ReadOnly
from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, RecipeCart, RecipeFavorite, RecipeTag
from .serializers import (
    BaseRecipeSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    RecipeTagSerializer,
)


class RecipeTagViewSet(ReadOnlyModelViewSet):
    queryset = RecipeTag.objects.all()
    serializer_class = RecipeTagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.prefetch_related("measurement_unit")
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = (
        Recipe.ext_objects.prefetch_related("tags")
        .prefetch_related("recipeingredients__ingredient")
        .prefetch_related("recipeingredients__ingredient__measurement_unit")
    )
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor | ReadOnly]
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            user = None

        queryset = super().get_queryset()
        queryset = (
            queryset.author_with_subscriptions(user=user)
            .with_favorites(user=user)
            .with_shopping_cart(user=user)
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "create" or self.action == "partial_update":
            return RecipeCreateSerializer
        return RecipeSerializer

    def _recipe_action_template(self, request, pk=None, related_model=None):
        """Template for similar ViewSet actions."""

        allowed_methods = [
            "GET",
            "DELETE",
        ]

        assert (
            related_model is not None
        ), "'related_model' (связанная модель) обязательный параметр."

        assert request.method in allowed_methods, (
            f"В request не допустимый метод. Поддерживаемые методы "
            f"{allowed_methods}"
        )

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
        """Add or remove recipe to user's favorite list."""
        related_model = RecipeFavorite
        return self._recipe_action_template(request, pk, related_model)

    @action(
        methods=["get", "delete"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Add or remove recipe in user's shopping cart."""
        related_model = RecipeCart
        return self._recipe_action_template(request, pk, related_model)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """
        Generate and return list of ingredient's form user's shopping cart.
        """
        user = request.user
        queryset = Ingredient.ext_objects.user_cart(user=user)

        if not queryset.exists():
            raise NotFound("Список покупок пустой.")

        context = {"ingredient_list": queryset}
        context["STATIC_ROOT"] = settings.STATIC_ROOT

        template_path = "cart_list_pdf.html"
        template = get_template(template_path)
        html = template.render(context)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="cart.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            raise NotAcceptable("Не удается подготовить PDF с списком.")
        return response
