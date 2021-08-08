from django_filters import rest_framework as filters

from .models import Recipe, RecipeTag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=RecipeTag.objects.all(),
        to_field_name="slug",
    )

    class Meta:
        model = Recipe
        fields = {
            "author": ["exact"],
        }
