"""Utility methods for the BibOS project."""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


def notify_users(data, security_problem, pc):
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
        message = EmailMessage("Sikkerhedsadvarsel for PC : " + pc.name
                               + ". Sikkerhedsproblem : " +
                               security_problem.name, body,
                               settings.DEFAULT_FROM_EMAIL, email_list)
        message.send(fail_silently=False)
    except Exception:
        return False

    return True
