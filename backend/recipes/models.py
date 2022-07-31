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
        verbose_name='теги рецепта',
    )
    
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='время готовки',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'       