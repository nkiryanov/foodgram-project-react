from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from foodgram.recipes.serializers import SubscriptionSerializer
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.extended_objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        parent_qs = self.queryset
        user = self.request.user
        qs = parent_qs.with_follows(user=user)
        return qs


class SubscriptionViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        user_follow_list = user.following.values_list("following", flat=True)
        queryset = (
            User.extended_objects.with_recipes_count()
            .with_follows(user=user)
            .filter(id__in=user_follow_list)
        )
        return queryset
