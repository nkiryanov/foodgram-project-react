from django_filters import rest_framework as filters

from .models import Recipe, RecipeTag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=RecipeTag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = filters.BooleanFilter(method="is_favorited_filter")
    is_in_shopping_cart = filters.BooleanFilter(
        method="is_in_shopping_cart_filter"
    )

    def is_favorited_filter(self, queryset, name, value):
        qs = queryset.filter(is_favorited=value)
        return qs

    def is_in_shopping_cart_filter(self, queryset, name, value):
        qs = queryset.filter(is_in_shopping_cart=value)
        return qs

    class Meta:
        model = Recipe
        fields = {
            "author": ["exact"],
        }
