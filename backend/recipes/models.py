from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)
    quantity = models.FloatField(max_length=40)
    unit_of_measurement = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name 


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True)
    hexcolor = models.CharField(max_length=7, unique=True, default="#ffffff")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор рецепта',
    )

    name = models.CharField(
        max_length=200,
        verbose_name='название рецепта',
    )

    image = models.ImageField(
        upload_to='recipe_images',
        verbose_name='фото блюда',
    )

    description = models.CharField(
        max_length=200,
        verbose_name='описание рецепта',
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='теги рецепта',
    )
    
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='время готовки',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'       


class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='favorites',
                               on_delete=models.CASCADE)
    added = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления в избранное'
    )

    class Meta:
        verbose_name = 'Избранное'
        models.UniqueConstraint(fields=['recipe', 'user'], name='favorite_unique')

    def __str__(self):
        return f"{self.user} has favorites: {self.recipe.name}"


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_shopping_list',
                             verbose_name='Пользоавтель')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='purchases',
                               verbose_name='Покупка')
    added = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления в список покупок'
    )

    class Meta:
        verbose_name = 'Покупки'

    def __str__(self):
        return f'In {self.user} список покупок: {self.recipe}'


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredients_in_recipe', verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipes_ingredients_list', verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)],
        verbose_name='Количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Количество'

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'