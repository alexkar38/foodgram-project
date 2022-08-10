from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    r"recipes/(?P<recipe_id>\d+)/favorite",
    views.FavoriteViewSet,
    basename="favorites",
)
router.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    views.ShoppingListViewSet,
    basename="shopping_cart",
)
router.register("tags", views.TagViewSet, basename="tags")
router.register("recipes", views.RecipeViewSet, basename="recipes")
router.register(
    r"ingredients",
    views.IngredientViewSet,
    basename="ingredients",
)


urlpatterns = [
    path("", include(router.urls)),
]
