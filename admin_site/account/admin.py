
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
    def get_queryset(self, request):
        all_users = super(MyUserAdmin, self).get_queryset(request)
        if _check_privilege(request.user):
            return all_users
        else:
            return all_users.filter(
                bibos_profile__site=request.user.bibos_profile.site)

    limited_fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if _check_privilege(request.user):
            return super(MyUserAdmin, self).get_fieldsets(request, obj)
        else:
            return MyUserAdmin.limited_fieldsets

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
