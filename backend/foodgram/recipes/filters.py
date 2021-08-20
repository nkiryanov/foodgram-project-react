from django.db.models import Case, Q, Value, When
from django_filters import rest_framework as filters

from .models import Recipe, RecipeTag


class IngredientFilter(filters.FilterSet):
    """
    Filter ingredients with 'name' in it's name.
    It also reorders the queryset. Ingredients that starts with 'name' are
    listed first.
    """

    name = filters.CharFilter(method="name_filter")

    def name_filter(self, queryset, name, value):
        qs = queryset.filter(Q(name__icontains=value))
        qs = qs.annotate(
            name_startswith=Case(
                When(
                    Q(name__istartswith=value),
                    then=Value(True),
                ),
                default=Value(False),
            ),
        )
        return qs.order_by("-name_startswith")


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
