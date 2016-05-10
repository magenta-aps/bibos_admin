"""Utility methods for the BibOS project."""

from django.conf import settings
from account.models import UserProfile
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

def notify_users(data, securityProblemId):
    """Notify users about security event.""" 
    
    #Subject = security type,
    #Body = technical summary
    email_list = []
    user_profiles = UserProfile.objects.filter(security_alerts=securityProblemId)
    for user in user_profiles:             
        email_list.append(User.objects.get(id=user.user_id).email)
    
    try:
        message = EmailMessage(data[1], data[4], settings.ADMIN_EMAIL,
                                email_list)
        message.send()
    except Exception:
        # TODO: Handle this properly
        raise
        
    return True