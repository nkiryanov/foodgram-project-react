from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable, NotFound
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import UserFollow
from .serializers import UserSubscriptionSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.extended_objects.with_recipes_count().order_by("id")

    @action(
        detail=True,
        methods=["get", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        follower = request.user
        following = self.get_object()

        is_subscribed = UserFollow.objects.filter(
            follower=follower,
            following=following,
        ).exists()

        if request.method == "GET":
            if follower == following:
                raise NotAcceptable("Нельзя подписаться на самого себя.")
            if is_subscribed:
                raise NotAcceptable("Такая подписка уже есть.")
            UserFollow.objects.create(follower=follower, following=following)
            response_data = UserSubscriptionSerializer(
                following,
                context={"request": request},
            )
            return Response(response_data.data)

        if request.method == "DELETE":
            if not is_subscribed:
                raise NotFound("Пользователь не подписан.")

            UserFollow.objects.filter(
                follower=follower,
                following=following,
            ).delete()
            return Response("OK", status.HTTP_201_CREATED)


class SubscriptionViewSet(ListModelMixin, GenericViewSet):
    queryset = User.extended_objects.with_recipes_count().order_by("id")
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        user_follow_list = user.following.values_list("following", flat=True)
        queryset = self.queryset.filter(id__in=user_follow_list)
        return queryset
