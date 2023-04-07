from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import CustomUser
from foodgram.settings import MIN_VALUE, MAX_VALUE

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
        constraints = [
            # Ограничение добавление одинаковых ингредиентов
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient"
            ),
        ]
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


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
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


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
            MaxValueValidator(
                MAX_VALUE,
                message="Убедитесь, что это значение меньше либо равно 32767."
            ),
        ]
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


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

    class Meta:
        verbose_name = "Тег рецепта"
        verbose_name_plural = "Теги рецептов"

    def __str__(self):
        return f"{self.recipe} {self.tag}"


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
            MaxValueValidator(
                MAX_VALUE,
                message="Убедитесь, что это значение меньше либо равно 32767."
            ),
        ]
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.recipe} {self.ingredient} {self.amount}"


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

    def __str__(self):
        return f"{self.user} добавил в корзину покупок {self.recipe}"


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

    def __str__(self):
        return f"{self.user} добавил в избранное {self.recipe}"
