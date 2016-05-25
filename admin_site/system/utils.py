"""Utility methods for the BibOS project."""

from django.conf import settings
from account.models import UserProfile
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


def notify_users(data, securityProblem):
    """Notify users about security event."""

    # Subject = security name,
    # Body = description + technical summary
    email_list = []
    for user in securityProblem.alert_users:
        email_list.append(User.objects.get(id=user.user_id).email)

    body = ("Beskrivelse af sikkerhedsadvarsel: " +
            securityProblem.description + "\n")
    body += "Kort resume af data fra log filen : " + data[2]
    try:
        message = EmailMessage("Sikkerhedsadvarsel: " +
                               securityProblem.name, body,
                               settings.ADMIN_EMAIL, email_list)
        message.send()
    except Exception:
        raise

    return True
