import sys
import os

from django.conf.urls import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bibos_admin.views.home', name='home'),
    url(r'^accounts/login/', 'django.contrib.auth.views.login', 
        { 'template_name': 'login.html'}, name='login'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout', 
        { 'template_name': 'login.html'}, name='logout'),
    url(r'^', include('system.urls')),
    url(r'^admin-xml/$', 'django_xmlrpc.views.handle_xmlrpc'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

)
# Static media when running manually
if 'runserver' in sys.argv or 'runserver_plus':
    urlpatterns += patterns(
        '', 
        url(
            r'^media/(.*)$', 'django.views.static.serve',
            kwargs={'document_root': settings.MEDIA_ROOT}), ) 
