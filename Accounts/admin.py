from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


class AccountModeladmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined', 'last_login', 'status', 'is_staff', 'is_superuser')
    list_display_links = ('username', 'email')
    list_filter = ('username', 'email', 'date_joined')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('date_joined',)

    filter_horizontal = ()
    fieldsets = ()
    list_per_page = 25


admin.site.register(User, AccountModeladmin)
