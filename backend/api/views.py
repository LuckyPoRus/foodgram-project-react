from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    GetRecipesSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, IsAdminOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeSerializer
        return CreateRecipeSerializer

    def create_delete(self, request, id, model):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        context = {"request": request}

        if self.request.method == "POST":
            model.objects.get_or_create(user=user, recipe=recipe)
            serializer = GetRecipesSerializer(recipe, context=context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["POST", "DELETE"],
        detail=True
    )
    def favorite(self, request, id=None):
        return self.create_delete(request, id, Favorite)

    @action(
        methods=["POST", "DELETE"],
        detail=True
    )
    def shopping_cart(self, request, id=None):
        return self.create_delete(request, id, ShoppingCart)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                "ingredient__name",
                "ingredient__measurement_unit"
            ).annotate(
                amount=Sum("amount")
            )
        )
        shopping_list = "\n".join([
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) '
            f'- {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = (
            "attachment; filename='shopping_list.txt'"
        )
        return response


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
