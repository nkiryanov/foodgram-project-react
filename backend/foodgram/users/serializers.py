from djoser import serializers as djoser_serializers
from rest_framework import serializers


class UserSerializer(djoser_serializers.UserSerializer):
    """Uses djoser's UserSerializer with extra fields."""

    is_subscribed = serializers.BooleanField(default=True, read_only=True)

    class Meta(djoser_serializers.UserSerializer.Meta):
        fields = djoser_serializers.UserSerializer.Meta.fields + (
            "first_name",
            "last_name",
            "is_subscribed",
        )


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):
    """Uses djoser's UserCreateSerializer with extra fields."""

    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        fields = djoser_serializers.UserCreateSerializer.Meta.fields + (
            "first_name",
            "last_name",
        )
