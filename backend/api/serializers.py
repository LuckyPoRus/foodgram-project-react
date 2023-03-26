from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get("request")
        if not user or user.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        model = RecipeIngredient

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get("request")
        if not user or user.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request')
        if not user or user.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        fields = (
            "id",
            "amount",
        )
        model = RecipeIngredient


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = CreateRecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )
        model = Recipe

    def validate_tags(self, value):
        if not value:
            raise ValidationError(
                "Необходимо добавить тег"
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                "Необходимо добавить ингредиент"
            )
        ingredients_list = []
        for item in value:
            ingredient = get_object_or_404(Ingredient, id=item["id"])
            if ingredient in ingredients_list:
                raise ValidationError(
                    "Такой ингредиент уже добавлен"
                )
            if int(item["amount"]) <= 0:
                raise ValidationError(
                    "Количество ингрдиентов должно быть больше 0"
                )
            ingredients_list.append(ingredient)
        return value

    def create(self, validated_data):
        author = self.context.get("request").user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient["amount"]
            ingredient = get_object_or_404(Ingredient, id=ingredient["id"])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient["amount"]
                ingredient = get_object_or_404(Ingredient, id=ingredient["id"])
                RecipeIngredient.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={"amount": amount}
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeSerializer(instance, context=context).data()


class CustomUserRegisterSerializer(UserCreateSerializer):

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        model = User


class GetRecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        model = Recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        model = Subscription

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        recipes = Recipe.objects.filter(author=obj)
        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]
        serializer = GetRecipesSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
