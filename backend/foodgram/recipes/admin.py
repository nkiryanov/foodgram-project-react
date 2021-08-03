from django.contrib import admin
from foodgram.recipes.models import (
    Ingredient,
    MeasurementUnit,
    Recipe,
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
    list_display = ["name", "author", "pub_date"]
    search_fields = ["name"]
    list_filter = ["author"]
    autocomplete_fields = ["ingredients"]
    inlines = [RecipeIngredientInline]


class FavoriteAdmin(admin.ModelAdmin):
    fields = ["user", "recipe"]
    search_fields = ["user", "recipe"]


admin.site.register(MeasurementUnit, MeasurementUnitAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeFavorite, FavoriteAdmin)
