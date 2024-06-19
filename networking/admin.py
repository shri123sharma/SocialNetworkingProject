from django.contrib import admin

from .models import FriendRequest, UserData


class UserDataAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserData model.

    Displays selected fields in the list view, enables searching by email and name,
    and provides filters for is_active, is_staff, and is_superuser fields.
    """

    list_display = ["id", "email", "name", "is_active", "is_staff", "is_superuser"]
    search_fields = ["email", "name"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    ordering = ["id"]


admin.site.register(UserData, UserDataAdmin)


class FriendAdmin(admin.ModelAdmin):
    """
    Admin configuration for FriendRequest model.

    Displays selected fields in the list view and orders records by ID.
    """

    list_display = ["id", "sender", "receiver", "status", "timestamp"]
    ordering = ["id"]


admin.site.register(FriendRequest, FriendAdmin)
