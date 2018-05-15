#!/usr/bin/env python
import os
import sys
import dotenv

if __name__ == "__main__":

    install_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__))
    )

    dotenv.load_dotenv(install_dir + '/bibos_admin/.env')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bibos_admin.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
