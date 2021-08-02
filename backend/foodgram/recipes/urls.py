from django.urls import include, path
from foodgram.recipes.views import IngredientViewSet, RecipeTagViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    "ingredients",
    IngredientViewSet,
    basename="ingredients",
)
router.register(
    "tags",
    RecipeTagViewSet,
    basename="tags",
)

urlpatterns = [
    path("", include(router.urls)),
]
