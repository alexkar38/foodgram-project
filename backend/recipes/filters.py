from django_filters.rest_framework import FilterSet, filters

from .models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(FilterSet):
    tags = filters.CharFilter(field_name="tags__slug", method="filter_tags")
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(method="filter_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_in_shopping_cart", "is_favorited")

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(purchases__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, value):
        values = self.data.getlist("tags")
        lookup = f"{name}__in"
        return queryset.filter(**{lookup: values}).distinct()
