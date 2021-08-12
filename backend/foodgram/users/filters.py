from django_filters import rest_framework as filters


class SubscriptionFilter(filters.FilterSet):
    recipes_limit = filters.NumberFilter(method="recipes_limit_filter")

    def recipes_limit_filter(self, queryset, name, value):
        qs = queryset.limit_recipes(value)
        return qs
