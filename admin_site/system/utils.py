"""Utility methods for the BibOS project."""

from django.conf import settings
from account.models import UserProfile
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


def notify_users(data, security_problem):
    """Notify users about security event."""

    # Subject = security name,
    # Body = description + technical summary
    email_list = []
    alert_users = security_problem.alert_users.all()
    for user in alert_users:
        email_list.append(User.objects.get(id=user.id).email)

    body = ("Beskrivelse af sikkerhedsadvarsel: " +
            security_problem.description + "\n")
    body += "Kort resume af data fra log filen : " + data[2]
    try:
        message = EmailMessage("Sikkerhedsadvarsel: " +
                               security_problem.name, body,
                               settings.ADMIN_EMAIL, email_list)
        message.send()
    except Exception:
        raise

    return True
