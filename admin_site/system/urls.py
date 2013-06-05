from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from models import Site

from views import SiteList, SiteView, SiteCreate, SiteUpdate, AdminIndex
from views import ComputersView, GroupsView, UsersView, JobsView, ScriptsView


urlpatterns = patterns(
    '',
    url(r'^$', AdminIndex.as_view(), name='index'),
    url(r'^sites/$', SiteList.as_view(), name='sites'),
    url(r'^sites/new/$', SiteCreate.as_view(), name='new_site'),
    url(r'^sites/(?P<pk>\d+)/edit/$', SiteUpdate.as_view(), name='edit_site'),
    url(r'^site/(?P<slug>\w+)/$', SiteView.as_view(), name='site'),
    url(r'^site/(?P<slug>\w+)/configuration/',
        SiteView.as_view(template_name='system/site_configuration.html'),
        name='configuration'),
    url(r'^site/(?P<slug>\w+)/computers/$', ComputersView.as_view(),
        name='computers'),
    url(r'^site/(?P<slug>\w+)/computers/(?P<uid>\w+)/$',
        ComputersView.as_view(), name='computer'),
    url(r'^site/(?P<slug>\w+)/groups/$', GroupsView.as_view(),
        name='groups'),
    url(r'^site/(?P<slug>\w+)/groups/(?P<uid>\w+)/$',
        GroupsView.as_view(), name='group'),
    url(r'^site/(?P<slug>\w+)/jobs/', JobsView.as_view(), name='jobs'),
    url(r'^site/(?P<slug>\w+)/scripts/',
        ScriptsView.as_view(),
        name='scripts'),
    url(r'^site/(?P<slug>\w+)/users/$', UsersView.as_view(), name='users'),
    url(r'^site/(?P<slug>\w+)/users/(?P<username>\w+)/$',
        UsersView.as_view(), name='user'),
)
