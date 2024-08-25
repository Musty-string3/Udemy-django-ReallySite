from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'email',
                'password',
            ),
        }),
        (None, {
            "fields": (
                'is_active',
                'is_admin',
            ),
        }),
    )

    list_display = ('email', 'is_active')
    list_filter = ()
    ordering = ()
    filter_horizontal = ()

    # --- adminでuser作成用に追加 ---
    add_fieldsets = (
        (None, {
            "fields": (
                'email',
                'password',
            ),
        }),
    )

admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
