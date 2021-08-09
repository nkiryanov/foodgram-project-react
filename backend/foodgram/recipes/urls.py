from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeTagViewSet, RecipeViewSet

recipes_router = DefaultRouter()


recipes_router.register(
    "ingredients",
    IngredientViewSet,
    basename="ingredients",
)
recipes_router.register(
    "tags",
    RecipeTagViewSet,
    basename="tags",
)
recipes_router.register(
    "recipes",
    RecipeViewSet,
    basename="recipes",
)

urlpatterns = [
    path("", include(recipes_router.urls)),
]
