from http import HTTPStatus

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from . import serializers
from .filters import IngredientFilter, RecipeFilter
from .mixins import RecipeCreateMixin
from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingList, Tag)
from .permissions import IsOwnerOrReadOnly
from .utils import get_pdf


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = [AllowAny]
    filter_class = IngredientFilter
    pagination_class = None


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    permission_classes = [
        IsOwnerOrReadOnly,
    ]
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return serializers.RecipeFullSerializer
        return serializers.RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        purchases = IngredientAmount.objects.purchases(user)
        file = get_pdf(purchases)
        return FileResponse(file, as_attachment=True, filename="purchases.pdf")


class ShoppingListViewSet(RecipeCreateMixin):
    queryset = ShoppingList.objects.all()
    serializer_class = serializers.ShoppingListSerializer

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingList.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class FavoriteViewSet(RecipeCreateMixin):
    queryset = Favorite.objects.all()
    serializer_class = serializers.FavoriteSerializer

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=HTTPStatus.NO_CONTENT)
