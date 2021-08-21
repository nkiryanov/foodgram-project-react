from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .filters import SubscriptionFilter
from .models import UserSubscription
from .serializers import UserSubscriptionSerializer, UserWithRecipesSerializer

User = get_user_model()


class CustomUserQuerysetMixin:
    """
    Adds annotated UserQueryset with fields
    - is_subsribed
    - recipe_count
    """

    queryset = User.ext_objects.order_by("id")

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            user = None

        queryset = super().get_queryset()
        queryset = queryset.with_recipes_count().with_subscriptions(user=user)
        return queryset


class CustomUserViewSet(CustomUserQuerysetMixin, DjoserUserViewSet):
    @action(
        detail=True,
        methods=["get", "delete"],
        permission_classes=[IsAuthenticated],
        serializer_class=UserSubscriptionSerializer,
    )
    def subscribe(self, request, id=None):
        """Action to follow and unfollow users."""
        follower = request.user
        following = self.get_object()

        if request.method == "GET":
            context = {"request": request}
            serializer = self.get_serializer_class()
            data = {
                "follower": follower.id,
                "following": following.id,
            }
            serializer = serializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            response_data = UserWithRecipesSerializer(
                following,
                context={"request": request},
            )
            return Response(response_data.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            number_deleted_objects, _ = UserSubscription.objects.filter(
                follower=follower,
                following=following,
            ).delete()

            if number_deleted_objects == 0:
                raise NotFound("Пользователь не подписан.")

            return Response("OK", status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(
    CustomUserQuerysetMixin,
    ListModelMixin,
    GenericViewSet,
):
    """
    Returns following list of users with their recipes. The number of
    user's recipes could be limited with filter.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserWithRecipesSerializer
    filterset_class = SubscriptionFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        user_follow_list = user.following.values_list("following", flat=True)
        queryset = queryset.filter(id__in=user_follow_list)
        return queryset
