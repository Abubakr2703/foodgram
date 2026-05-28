from drf_extra_fields.fields import Base64ImageField

from django.contrib.auth import get_user_model

from rest_framework import serializers

from recipes.models import (
    RecipeIngredient,
    Recipe,
    Tag,
    Ingredient,
    Subscription,
    Favorite,
    ShoppingCart
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'ingredient')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'text', 'image',
                  'author', 'cooking_time', 'tags', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('author',)
        read_only_fields = ('user',)

    def validate_author(self, value):
        request = self.context['request']
        if request.user == value:
            raise serializers.ValidationError("Нельзя подписаться на себя")
        if Subscription.objects.filter(user=request.user,
                                       author=value).exists():
            raise serializers.ValidationError("Уже подписан")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'recipes',
            'is_subscribed', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        else:
            return Subscription.objects.filter(
                user=request.user, author=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        limit = self.context.get('recipes_limit', 3)
        recipes = obj.recipes.all()[:limit]
        serializer = RecipeShortSerializer(
            recipes, many=True, context=self.context)
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'author')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    amount = serializers.IntegerField(min_value=1)


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientAmountSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'name', 'text', 'cooking_time', 'image', 'tags', 'ingredients')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ing_data in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ing_data['ingredient'],
                amount=ing_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            for ing_data in ingredients:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ing_data['ingredient'],
                    amount=ing_data['amount']
                )
        return instance
