from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from users.serialaizers import ProfileSerializer

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingList, Tag)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Ingredient


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        model = IngredientAmount


class IngredientAmountWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        fields = (
            "id",
            "amount",
        )
        model = IngredientAmount


class AddToIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ("amount", "id")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Tag


class RecipeLiteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Recipe


class RecipeSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        recipe = obj
        queryset = recipe.recipes_ingredients_list.all()
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingList.objects.filter(recipe=obj, user=user).exists()


class RecipeFullSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    author = ProfileSerializer(read_only=True)
    ingredients = AddToIngredientAmountSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "image",
            "tags",
            "author",
            "ingredients",
            "name",
            "text",
            "cooking_time",
        )

    def create_bulk(self, recipe, ingredients_data):
        IngredientAmount.objects.bulk_create(
            [
                IngredientAmount(
                    ingredient=ingredient["ingredient"],
                    recipe=recipe,
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients_data
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        self.create_bulk(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_bulk(instance, ingredients_data)
        instance.name = validated_data.pop("name")
        instance.text = validated_data.pop("text")
        instance.cooking_time = validated_data.pop("cooking_time")
        if validated_data.get("image") is not None:
            instance.image = validated_data.pop("image")
        instance.save()
        instance.tags.set(tags_data)
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item["id"]
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    "Ингридиенты должны быть уникальными"
                )
            ingredient_list.append(ingredient)
        return data

    def validate_name(self, name):
        if not name:
            raise serializers.ValidationError("Не заполнено название рецепта!")
        if self.context.get("request").method == "POST":
            current_user = self.context.get("request").user
            if Recipe.objects.filter(author=current_user, name=name).exists():
                raise serializers.ValidationError(
                    "Рецепт с таким названием у вас уже есть!"
                )
        return name

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get("cooking_time")
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                "Время приготовления должно быть больше 0"
            )
        return data

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data
        return data


class RecipeImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        request = self.context.get("request")
        image_url = obj.image.url
        return request.build_absolute_uri(image_url)


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = "__all__"
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=["recipe", "user"],
                message=("Этот рецепт уже есть в вашем списке избранного."),
            ),
        ]


class ShoppingListSerializer(FavoriteSerializer):
    class Meta:
        model = ShoppingList
        fields = "__all__"
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=["recipe", "user"],
                message=("Этот рецепт уже есть в вашем списке покупок."),
            ),
        ]
