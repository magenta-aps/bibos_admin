from setuptools import setup

setup(
    name='bibos_client',
    version='0.0.3.0',
    description='Clients for the BibOS system',
    url='https://github.com/magenta-aps/',
    author='C. Agger and J.U.B. Krag, Magenta ApS',
    author_email='carstena@magenta-aps.dk',
    license='GPLv3',
    packages=['bibos_client'],
    install_requires=['netifaces', 'bibos_utils'],
    scripts=[
        'bin/bibos_find_gateway',
        'bin/bibos_register_in_admin',
        'bin/bibos_push_config_keys',
        'bin/bibos_upload_dist_packages',
        'bin/bibos_upload_packages',
        'bin/jobmanager',
        'bin/register_new_bibos_client.sh'
    ],
    zip_safe=False
)
