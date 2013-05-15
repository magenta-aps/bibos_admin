"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
import pep8

from django.test import TestCase

from bibos_admin.wsgi import install_dir as parent_directory


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


def pep8_test(filepath):
    def do_test(self):
        #print "PATH:", filepath
        arglist = ['--exclude=lib', filepath]
        pep8.process_options(arglist)
        pep8.input_dir(filepath)
        output = pep8.get_statistics()
        #print "PEP8 OUTPUT: " + str(output)
        self.assertEqual(len(output), 0)

    return do_test


class Pep8Test(TestCase):
    """Test that the template system a well as the default clients and plugins
    are PEP8-compliant."""
    j = lambda dir: os.path.join(parent_directory, dir)

    test_system = pep8_test(j('system'))
    test_job = pep8_test(j('job'))
    test_admin = pep8_test(j('admin'))
    test_client = pep8_test(j('../client'))
    test_utils = pep8_test(j('../utils'))
