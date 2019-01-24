
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile


def _check_privilege(user):
    if user.is_superuser:
        return True
    else:
        try:
            return user.bibos_profile.type == UserProfile.SUPER_ADMIN
        except UserProfile.DoesNotExist:
            return False


class UserInline(admin.TabularInline):
    model = UserProfile
    extra = 1


class MyUserAdmin(UserAdmin):
    inlines = [UserInline]
    can_delete = False


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(UserProfile)
