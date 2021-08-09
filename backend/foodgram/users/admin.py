from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import UserFollow

User = get_user_model()


class UserFollowAdmin(admin.ModelAdmin):
    fields = ["follower", "following"]
    search_fields = ["follower__username", "following__username"]


admin.site.register(User, UserAdmin)
admin.site.register(UserFollow, UserFollowAdmin)
