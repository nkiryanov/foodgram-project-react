from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Subscription

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        parent_qs = super().get_queryset()
        subquery = Subscription.objects.filter(
            user=user,
            author=OuterRef("id"),
        )
        qs = parent_qs.annotate(is_subscribed=Exists(subquery))
        return qs
