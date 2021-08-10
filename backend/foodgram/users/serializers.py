from django.contrib.auth import get_user_model
from djoser import serializers as djoser_serializers
from rest_framework import serializers

from ..users.models import UserFollow

User = get_user_model()


class UserSerializer(djoser_serializers.UserSerializer):
    """Uses djoser's UserSerializer with extra fields."""

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


class UserSubscriptionSerializer(UserSerializer):
    from foodgram.recipes.serializers import BaseRecipeSerializer

    recipes = BaseRecipeSerializer(many=True)
    recipes_count = serializers.IntegerField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )
