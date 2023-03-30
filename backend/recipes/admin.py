from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag
)


class IngredientResource(resources.ModelResource):

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientAdmin(ImportExportModelAdmin):
    from_encoding = "utf-8-sig"
    resource_classes = [IngredientResource]


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug"
    )


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "name",
        "image",
        "text",
        "cooking_time",
        "favorite_count"
    )
    list_filter = (
        "author",
        "name",
        "text",
        "tags"
    )

    @admin.display(description="Избранное")
    def favorite_count(self, obj):
        return obj.favorite.count()


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "tag"
    )


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "ingredient",
        "amount"
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe"
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe"
    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
