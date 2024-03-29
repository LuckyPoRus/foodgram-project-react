from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import UserCreateSerializer, UserSerializer
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
from foodgram.settings import MIN_VALUE, MAX_VALUE

User = get_user_model()


class CustomUserSerializer(UserSerializer):
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
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()


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
    id = serializers.ReadOnlyField(
        source="ingredient.id"
    )
    name = serializers.ReadOnlyField(
        source="ingredient.name"
    )
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
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

    def get_user(self):
        return self.context.get("request").user

    def get_is_favorited(self, obj):
        user = self.get_user()
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE
    )

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
    cooking_time = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE
    )

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

    def create_ingredients(self, recipe, ingredients):
        create_ingredient = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient["id"]),
                amount=ingredient["amount"]
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredient)

    def create(self, validated_data):
        author = self.context.get("request").user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeSerializer(instance, context=context).data


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
    email = serializers.ReadOnlyField(
        source='author.email'
    )
    id = serializers.ReadOnlyField(
        source='author.id'
    )
    username = serializers.ReadOnlyField(
        source='author.username',
    )
    first_name = serializers.ReadOnlyField(
        source='author.first_name'
    )
    last_name = serializers.ReadOnlyField(
        source='author.last_name'
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=["author", "user"]
            )
        ]

    def validate(self, obj):
        user = self.context.get("request").user
        if Subscription.objects.filter(author=obj, user=user).exists():
            raise ValidationError(
                "Уже подписаны на этого пользователя"
            )
        return obj

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        recipes = Recipe.objects.filter(author=obj.author)
        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]
        serializer = GetRecipesSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def create(self, validated_data):
        user = self.context.get("request").user
        password = make_password(validated_data.get("new_password"))
        user.password = password
        user.save()
        return validated_data
