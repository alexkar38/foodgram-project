from http import HTTPStatus

from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeLiteSerializer


class RecipeCreateMixin(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        recipe = get_object_or_404(Recipe, id=self.kwargs["recipe_id"])
        return self.queryset.filter(recipe=recipe, user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["recipe_id"])
        data = {"recipe": self.kwargs["recipe_id"]}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = RecipeLiteSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTPStatus.CREATED,
        )
