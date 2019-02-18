
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile
from system.models import Site


def _check_privilege(user):
    if user.is_superuser:
        return True
    else:
        try:
            return user.bibos_profile.type == UserProfile.SUPER_ADMIN
        except UserProfile.DoesNotExist:
            return False


def _restrict_user_type(request, kwargs):
    if not _check_privilege(request.user):
        kwargs['choices'] = (UserProfile.SITE_USER, _("Site User")),
        if request.user.bibos_profile.type == UserProfile.SITE_ADMIN:
            kwargs['choices'] += (UserProfile.SITE_ADMIN, _("Site Admin")),
    return kwargs


def _restrict_site(request, kwargs):
    if not _check_privilege(request.user):
        kwargs['queryset'] = Site.objects.filter(
                id=request.user.bibos_profile.site.id)
    return kwargs


def _restrict_users(request, kwargs):
    if not _check_privilege(request.user):
        kwargs['queryset'] = \
            User.objects.filter(bibos_profile__site=request.user.bibos_profile.site)
    return kwargs


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 1

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'type':
            kwargs = _restrict_user_type(request, kwargs)
        return super(UserProfileInline, self).formfield_for_choice_field(
                db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs = _restrict_site(request, kwargs)
        return super(UserProfileInline, self).formfield_for_choice_field(
                db_field, request, **kwargs)


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

    inlines = [UserProfileInline]
    can_delete = False


class MyUserProfileAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        all_profiles = super(MyUserProfileAdmin, self).get_queryset(request)
        if _check_privilege(request.user):
            return all_profiles
        else:
            return all_profiles.filter(site=request.user.bibos_profile.site)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'type':
            kwargs = _restrict_user_type(request, kwargs)
        return super(MyUserProfileAdmin, self).formfield_for_choice_field(
                db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs = _restrict_site(request, kwargs)
        elif db_field.name == 'user':
            kwargs = _restrict_users(request, kwargs)
        return super(MyUserProfileAdmin, self).formfield_for_choice_field(
                db_field, request, **kwargs)


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(UserProfile, MyUserProfileAdmin)
