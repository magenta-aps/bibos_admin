
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


class MyUserProfileAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        all_profiles = super(MyUserProfileAdmin, self).get_queryset(request)
        if _check_privilege(request.user):
            return all_profiles
        else:
            return all_profiles.filter(site=request.user.bibos_profile.site)


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(UserProfile, MyUserProfileAdmin)
