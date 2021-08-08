from django.contrib.auth import get_user_model
from djoser import serializers as djoser_serializers
from rest_framework import serializers

from ..recipes.models import Recipe
from ..users.models import UserFollow

User = get_user_model()


class UserSerializer(djoser_serializers.UserSerializer):
    """Uses djoser's UserSerializer with extra fields."""

    # is_subscribed = serializers.BooleanField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(djoser_serializers.UserSerializer.Meta):
        fields = djoser_serializers.UserSerializer.Meta.fields + (
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        is_subscribed = False
        if user.is_authenticated:
            is_subscribed = UserFollow.objects.filter(
                follower=user,
                following=obj,
            ).exists()
        return is_subscribed


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):
    """Uses djoser's UserCreateSerializer with extra fields."""

    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        fields = djoser_serializers.UserCreateSerializer.Meta.fields + (
            "first_name",
            "last_name",
        )


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = [
            "follower",
            "following",
        ]

    def validate(self, data):
        request = self.context.get("request")
        follower = data.get("follower")
        following = data.get("following")

        is_userfollow_exist = UserFollow.objects.filter(
            follower=follower,
            following=following,
        ).exists()

        if request.method == "GET":
            if follower == following:
                raise serializers.ValidationError(
                    {"errors": "Нельзя подписаться на самого себя."}
                )
            if is_userfollow_exist:
                raise serializers.ValidationError(
                    {"errors": "Такая подписка уже есть."}
                )

        if request.method == "DELETE":
            if not is_userfollow_exist:
                raise serializers.ValidationError(
                    {"errors": "Пользователь не подписан."}
                )

        return data


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]


class UserSubscriptionSerializer(UserSerializer):
    recipes = BaseRecipeSerializer(many=True)
    recipes_count = serializers.IntegerField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )
