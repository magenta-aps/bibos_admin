"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
import pep8

from django.conf import settings
from django.test import TestCase

print "FILE", os.path.dirname(__file__)

parent_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from account.models import UserProfile
from bibos_admin.wsgi import install_dir as parent_directory


# setup account_userprofile, auth_user, securityproblem
class SimpleTest(TestCase):
    def setUp(self):
        site_user = User.objects.create_superuser('danni',
                                                  'danni@magenta-aps.dk',
                                                  'hejsa')
        test_user = User.objects.create_superuser('test',
                                                  'test@magenta-aps.dk',
                                                  'hejsa')
        # security_problem = SecurityProblem.objects.create(name='Keyboard',
        # uid='KEYBOARD', description='Usb keyboard added.',
        # level='High', script_id=1, site_id=1)
        UserProfile.objects.create(user=site_user, type=1)
        UserProfile.objects.create(user=test_user, type=1)

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_notify_user(self):
        data = 'KEYBOARD, Summary, Raw data'
        split = data.split(',')
        email_list = []
        user_profiles = UserProfile.objects.filter(type=1)
        for user in user_profiles:
            email_list.append(User.objects.get(id=user.user_id).email)

        message = EmailMessage(split[0], split[1], settings.ADMIN_EMAIL,
                               email_list)

        self.assertEqual(len(email_list), 2)
        self.assertEquals(message.send(), 1)


def pep8_test(filepath):
    def do_test(self):
        arglist = ['--exclude=migrations', filepath]
        pep8.process_options(arglist)

        pep8.input_dir(filepath)
        output = pep8.get_statistics()
        # print "PEP8 OUTPUT: " + str(output)
        self.assertEqual(len(output), 0)

    return do_test


class Pep8Test(TestCase):
    """Test that the template system a well as the default clients and plugins
    are PEP8-compliant."""
    def j(d):
        result = os.path.abspath(os.path.join(parent_directory, d))
        return result

    system_dir = j('system')
    admin_dir = j('admin')
    client_dir = j('../bibos_client')
    utils_dir = j('../bibos_utils')
    test_system = pep8_test(system_dir)
    test_admin = pep8_test(admin_dir)
    test_client = pep8_test(client_dir)
    test_utils = pep8_test(utils_dir)
