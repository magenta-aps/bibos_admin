import sys
#import ipdb
#from bibos_admin import views
#from system import views

from django_xmlrpc.views import handle_xmlrpc
from django.views.static import serve

import django.contrib.auth.views
from django.conf.urls import include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'bibos_admin.views.home', name='home'),
    #ipdb.set_trace(),
#path('accounts/login/', auth_views.LoginView.as_view(template_name='myapp/login.html')),
    #url('accounts/login/', auth_views.LoginView.as_view(template_name='bibos_admin/login.html')),
    url('accounts/login/', auth_views.LoginView,
        {'template_name': 'login.html'}, name='login'),
    url(r'^xmlrpc/$', handle_xmlrpc, name='xmlrpc'),
    url(r'^accounts/logout/', auth_views.LogoutView,
        {'template_name': 'logout.html'}, name='logout'),
    url(r'^', include('system.urls')),
    url(r'^admin-xml/$', handle_xmlrpc),
    # Uncomment the admin/doc line below to enable admin documentation:
    #ipdb.set_trace(),
    url('admin/doc/', include('django.contrib.admindocs.urls')),
#    url(r'^admin/doc/', django.contrib.admindocs.urls),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]

# Static media when running manually
if 'runserver' in sys.argv or 'runserver_plus':
    urlpatterns += [
        url(
            r'^media/(.*)$', serve,
            kwargs={'document_root': settings.MEDIA_ROOT}), 
]
