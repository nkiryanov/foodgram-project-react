from django.contrib import admin
from django.db.models import Count
from foodgram.recipes.models import (
    Ingredient,
    MeasurementUnit,
    Recipe,
    RecipeCart,
    RecipeFavorite,
    RecipeIngredient,
)


class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "measurement_unit"]
    search_fields = ["name"]
    list_filter = ["measurement_unit"]


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "author", "pub_date", "favorite_count"]
    search_fields = ["name"]
    list_filter = ["author", "tags"]
    readonly_fields = ["favorite_count"]

    def favorite_count(self, obj):
        return obj.favorite_count

    favorite_count.short_description = "Раз добавили в избранное"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = (
            qs.annotate(favorite_count=Count("favorites"))
            .prefetch_related("favorites")
            .prefetch_related("tags")
            .prefetch_related("ingredients")
        )
        return qs

    autocomplete_fields = ["ingredients"]
    inlines = [RecipeIngredientInline]


class RecipeFavoriteAdmin(admin.ModelAdmin):
    fields = ["user", "recipe"]
    search_fields = ["user", "recipe"]


class RecipeCartAdmin(admin.ModelAdmin):
    fields = ["user", "recipe"]
    search_fields = ["user", "recipe"]


admin.site.register(MeasurementUnit, MeasurementUnitAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeFavorite, RecipeFavoriteAdmin)
admin.site.register(RecipeCart, RecipeCartAdmin)
