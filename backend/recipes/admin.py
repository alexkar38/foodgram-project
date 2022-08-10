from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, Tag, ShoppingList


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "count_favorites")
    list_filter = ("author", "name", "tags")

    def count_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin): 
    list_display = ("user", "recipe",)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin): 
    list_display = ("user", "recipe",)