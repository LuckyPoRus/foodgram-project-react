from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method="is_favorited_filter"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="is_in_shopping_cart_filter"
    )

    class Meta:
        fields = (
            "tags",
            "author",
        )
        model = Recipe

    def is_favorited_filter(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientSearch(SearchFilter):
    search_param = "name"
