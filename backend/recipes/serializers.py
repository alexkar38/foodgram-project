#from django.conf.settings import AUTH_USER_MODEL
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import HybridImageField
from rest_framework import serializers, validators

from .models import Favorite, Ingredient, ShoppingList, IngredientAmount, Recipe, Tag
from users.serialaizers import ProfileSerializer



class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = IngredientAmount


class IngredientAmountWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = ['id', 'amount']
        model = IngredientAmount


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class RecipeLiteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Recipe


class RecipeSerializer(RecipeLiteSerializer):
    author = ProfileSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(many=True, read_only=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        fields = '__all__'
        model = Recipe


class RecipeWriteSerializer(serializers.ModelSerializer):
    #text = serializers.JSONField()
    author = ProfileSerializer(read_only=True)
    ingredients = IngredientAmountWriteSerializer(many=True)
    image = HybridImageField()

    class Meta:        
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',            
            'name',
            'image',
            'text',
            'cooking_time',
        )
        
    def validate_ingredients(self, value):
        for ingredient in value:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    _('Количество должно быть больше 0.')
                )
        return value

    
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.add_ingredients(ingredients_data)
        recipe.tags.set(tags_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )
        IngredientAmount.objects.filter(recipe=instance).delete()
        instance.add_ingredients(ingredients_data)
        instance.tags.set(tags_data)
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user'],
                message=_('Этот рецепт уже есть в вашем списке избранного.')
            ),
        ]


class ShoppingListSerializer(FavoriteSerializer):
    class Meta:
        model = ShoppingList
        fields = '__all__'
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=['recipe', 'user'],
                message=_('Этот рецепт уже есть в вашем списке покупок.')
            ),
        ]