from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ( FavoriteViewSet, RecipeViewSet,
                    ShoppingListViewSet, IngredientViewSet, TagViewSet)

router = DefaultRouter()
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorites',
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingListViewSet,
    basename='user_shopping_list',
)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),       
    ]
