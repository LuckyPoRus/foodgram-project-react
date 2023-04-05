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
    list_display = (
        "name",
        "measurement_unit"
    )
    list_filter = (
        "name",
    )
    search_fields = (
        "name",
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug"
    )
    search_fields = (
        "name",
    )


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient


class RecipeTagsInLine(admin.TabularInline):
    model = RecipeTag


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "name",
        "image",
        "text",
        "get_tags",
        "cooking_time",
        "favorite_count"
    )
    list_filter = (
        "author",
        "name",
        "text",
        "tags"
    )
    search_fields = (
        "author__email",
        "name",
        "tags__name"
    )
    inlines = (
        RecipeIngredientInLine,
        RecipeTagsInLine,
    )

    @admin.display(description="Теги")
    def get_tags(self, obj):
        return ', '.join([t.name for t in obj.tags.all()])

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
