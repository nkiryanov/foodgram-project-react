from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import UserFollow
from .serializers import UserFollowSerializer, UserSubscriptionSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.extended_objects.with_recipes_count().order_by("id")

    @action(
        detail=True,
        methods=["get", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        user_to_follow = self.get_object()
        data = {
            "follower": request.user.id,
            "following": user_to_follow.id,
        }

        serializer = UserFollowSerializer(
            data=data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        if request.method == "GET":
            UserFollow.objects.create(
                follower=request.user,
                following=user_to_follow,
            )
            response_data = UserSubscriptionSerializer(
                user_to_follow, context={"request": request}
            )
            return Response(response_data.data)

        if request.method == "DELETE":
            UserFollow.objects.filter(
                follower=request.user,
                following=user_to_follow,
            ).delete()
            return Response("OK", status.HTTP_201_CREATED)


class SubscriptionViewSet(ListModelMixin, GenericViewSet):
    queryset = User.extended_objects.with_recipes_count()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        user_follow_list = user.following.values_list("following", flat=True)
        queryset = self.queryset.filter(id__in=user_follow_list)
        return queryset
