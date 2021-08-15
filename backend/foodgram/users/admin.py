from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import UserSubscription

User = get_user_model()


class UserSubscriptionAdmin(admin.ModelAdmin):
    fields = ["follower", "following"]
    search_fields = ["follower__username", "following__username"]


class ExtendedUserAdmin(UserAdmin):
    list_filter = ["email", "username"]


admin.site.register(User, UserAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
