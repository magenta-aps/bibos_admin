from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from system.models import Site, SecurityProblem


class UserProfile(models.Model):
    """BibOS Admin specific user profile."""
    # This is the user to which the profile belongs
    user = models.OneToOneField(User, unique=True,
                                related_name='bibos_profile')

    SUPER_ADMIN = 0
    SITE_USER = 1
    SITE_ADMIN = 2
    type_choices = (
        (SUPER_ADMIN, _("Super Admin")),
        (SITE_USER, _("Site User")),
        (SITE_ADMIN, _("Site Admin"))
    )

    # The choices that can be used on the non-admin part of the website
    NON_ADMIN_CHOICES = (
        (SITE_USER, _("Site User")),
        (SITE_ADMIN, _("Site Admin"))
    )

    type = models.IntegerField(choices=type_choices, default=SITE_USER)
    site = models.ForeignKey(Site, null=True, blank=True)
    # TODO: Add more fields/user options as needed.
    # TODO: Make before_save integrity check that SITE_USER and
    # SITE_ADMIN users MUST be associated with a site.

    def __unicode__(self):
        return self.user.username

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.type != UserProfile.SUPER_ADMIN and self.site is None:
            raise ValidationError(_(
                'Non-admin users MUST be attached to a site'
            ))
