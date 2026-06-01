from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (IMAGE_UPLOAD_PATH, MAX_MEASUREMENT_LENGTH, NAME_LENGTH,
                        SLUG_MAX_LEGTH)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, verbose_name="Название")
    slug = models.SlugField(max_length=SLUG_MAX_LEGTH, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=NAME_LENGTH, verbose_name="Название", unique=True
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_LENGTH,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_ingredient"
            )
        ]


class Recipe(models.Model):
    name = models.CharField(max_length=NAME_LENGTH)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes",
        verbose_name="Автор"
    )
    image = models.ImageField(upload_to=IMAGE_UPLOAD_PATH,
                              verbose_name="Изображение")
    text = models.TextField(verbose_name="Текстовое описание")
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления",
        help_text="Время приготовления блюда (в минутах).",
    )
    tags = models.ManyToManyField(Tag,
                                  verbose_name="Теги", related_name="recipes")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", related_name="recipes"
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Количество"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            )
        ]
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_user_author"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} подписан на {self.author}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            ),
        ]

    def __str__(self):
        return f"{self.user} -> {self.recipe}"


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="favorites")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe"
            )
        ]
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
