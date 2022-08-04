from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCart, FavoriteApiView, RecipeViewSet,
                    ShoppingView, IngredientView, TagView)

router = DefaultRouter()
router.register('tags', TagView, basename='tags')
router.register('recipes', RecipeViewSet)
router.register(r'ingredients', IngredientView, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),    
    path('recipes/<int:favorite_id>/favorite/', FavoriteApiView.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingView.as_view()),
]