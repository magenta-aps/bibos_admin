"""Utility methods for the BibOS project."""

from django.conf import settings
from models import UserProfile
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

def notify_users(data, securityProblemId):
    """Notify users about security event. """
    
    #Subject = security type,
    #Body = technical summary
    user_profiles = UserProfile.objects.get(security_alerts=securityProblemId)
    for user in user_profiles:             
        try:
            message = EmailMessage(data[1], data[4], settings.ADMIN_EMAIL,
                                   User.objects.get(id=user.user_id).email)
            message.send()
        except Exception:
            # TODO: Handle this properly
            raise
        
    return True