from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser

MIN_VALUE = 1
MAX_LENGTH = 200
MAX_HEX_COLOR_LENGTH = 7


class Ingredient(models.Model):
    name = models.CharField(
        "Название ингредиента",
        max_length=MAX_LENGTH
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=MAX_LENGTH
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Tag(models.Model):
    name = models.CharField(
        "Название тега",
        max_length=MAX_LENGTH,
        unique=True
    )
    color = models.CharField(
        "Цветовой HEX-код",
        max_length=MAX_HEX_COLOR_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        "Уникальный слаг",
        max_length=MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта"
    )
    name = models.CharField(
        "Название рецепта",
        max_length=MAX_LENGTH
    )
    image = models.ImageField(
        "Картинка рецепта",
        upload_to="recipes/"
    )
    text = models.TextField(
        "Описание рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="RecipeIngredient",
        verbose_name="Список ингредиентов"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        through="RecipeTag",
        verbose_name="Список тегов"
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления в минутах",
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message="Убедитесь, что это значение больше либо равно 1."
            ),
        ]
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name="Тег"
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент"
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message="Убедитесь, что это значение больше либо равно 1."
            ),
        ]
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт"
    )

    class Meta:
        constraints = [
            # Ограничение добавление одинаковых рецептов в список покупок
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="shopping_cart_unique_recipe"
            ),
        ]
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Рецепт"
    )

    class Meta:
        constraints = [
            # Ограничение добавление одинаковых рецептов в избранное
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="favorite_unique_recipe"
            ),
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
