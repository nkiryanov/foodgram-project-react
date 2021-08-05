from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Subscription

User = get_user_model()


class SubscriptionAdmin(admin.ModelAdmin):
    fields = ["user", "author"]
    search_fields = ["user", "author"]


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
