from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .manager import IngridientAmountQuerySet


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Название ингредиента", null=False
    )
    measurement_unit = models.CharField(
        max_length=20, verbose_name="Единица измерения", null=False
    )

    class Meta:
        verbose_name = "Ингредиент"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, unique=True, default="#ffffff")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="автор рецепта",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="название рецепта",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="ingredients",
        through="IngredientAmount",
        verbose_name="Ингредиенты",
    )

    image = models.ImageField(
        upload_to="recipe_images",
        verbose_name="фото блюда",
    )
    text = models.TextField(
        verbose_name="Рецепт",
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="tags",
        verbose_name="теги рецепта",
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="время готовки",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="favorites",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe, related_name="favorites", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Избранное"
        models.UniqueConstraint(
            fields=["recipe", "user"], name="favorite_unique"
        )

    def __str__(self):
        return f"{self.user} has favorites: {self.recipe.name}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_shopping_list",
        verbose_name="Пользоавтель",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="purchases",
        verbose_name="Покупка",
    )

    class Meta:
        verbose_name = "Покупки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="user_and_purchase_uniq_together",
            ),
        ]

    def __str__(self):
        return f"In {self.user} список покупок: {self.recipe}"


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredients_in_recipe",
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipes_ingredients_list",
        verbose_name="Рецепт",
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Количество ингредиентов",
    )

    class Meta:
        verbose_name = "Количество ингредиента"

    objects = IngridientAmountQuerySet.as_manager()
