from django.conf.urls import patterns, url

from views import SiteList, SiteView, SiteCreate, SiteUpdate, SiteDelete
from views import AdminIndex, ComputersView, GroupsView, UsersView, JobsView
from views import GroupCreate, GroupUpdate, JobSearch, SiteDetailView
from views import UserCreate
from views import ScriptList, ScriptUpdate, ScriptCreate, ScriptDelete
from views import ScriptRun
from views import ConfigurationEntryCreate, ConfigurationEntryUpdate
from views import ConfigurationEntryDelete
from views import PackageSearch

urlpatterns = patterns(
    '',
    url(r'^$', AdminIndex.as_view(), name='index'),
    url(r'^sites/$', SiteList.as_view(), name='sites'),
    url(r'^sites/new/$', SiteCreate.as_view(), name='new_site'),
    url(r'^sites/(?P<slug>\w+)/edit/$',
        SiteUpdate.as_view(),
        name='edit_site'),
    url(r'^sites/(?P<slug>\w+)/delete/$',
        SiteDelete.as_view(),
        name='delete_site'),
    url(r'^site/(?P<slug>\w+)/$', SiteDetailView.as_view(), name='site'),
    url(r'^site/(?P<slug>\w+)/configuration/$',
        SiteView.as_view(template_name='system/site_configuration.html'),
        name='configuration'),
    url(r'^site/(?P<site_uid>\w+)/configuration/new/$',
        ConfigurationEntryCreate.as_view(), name='new_config_entry'),
    url(r'^site/(?P<site_uid>\w+)/configuration/edit/(?P<pk>\d+)/$',
        ConfigurationEntryUpdate.as_view(), name='edit_config_entry'),
    url(r'^site/(?P<site_uid>\w+)/configuration/delete/(?P<pk>\d+)/$',
        ConfigurationEntryDelete.as_view(), name='delete_config_entry'),
    url(r'^site/(?P<slug>\w+)/computers/$', ComputersView.as_view(),
        name='computers'),
    url(r'^site/(?P<slug>\w+)/computers/(?P<uid>\w+)/$',
        ComputersView.as_view(), name='computer'),
    url(r'^site/(?P<slug>\w+)/groups/$', GroupsView.as_view(),
        name='groups'),
    url(r'^site/(?P<site_uid>\w+)/groups/new/$', GroupCreate.as_view(),
        name='new_group'),
    url(r'^site/(?P<site_uid>\w+)/groups/(?P<group_uid>\w+)/$',
        GroupUpdate.as_view(), name='group'),
    url(r'^site/(?P<slug>\w+)/jobs/search/',
        JobSearch.as_view(),
        name='jobsearch'),
    url(r'^site/(?P<slug>\w+)/jobs/', JobsView.as_view(), name='jobs'),
    # Scripts
    url(r'^site/(?P<slug>\w+)/scripts/(?P<script_pk>\d+)/delete/',
        ScriptDelete.as_view(),
        name='delete_script'),
    url(r'^site/(?P<slug>\w+)/scripts/(?P<script_pk>\d+)/run/',
        ScriptRun.as_view(),
        name='run_script'),
    url(r'^site/(?P<slug>\w+)/scripts/(?P<script_pk>\d+)/',
        ScriptUpdate.as_view(),
        name='script'),
    url(r'^site/(?P<slug>\w+)/scripts/new/',
        ScriptCreate.as_view(),
        name='new_script'),
    url(r'^site/(?P<slug>\w+)/scripts/',
        ScriptList.as_view(),
        name='scripts'),

    # Users
    url(r'^site/(?P<slug>\w+)/users/$', UsersView.as_view(), name='users'),
    url(r'^site/(?P<slug>\w+)/users/new/$',
        UserCreate.as_view(), name='new_user'),
    url(r'^site/(?P<slug>\w+)/users/(?P<username>\w+)/$',
        UsersView.as_view(), name='user'),

    # Packages
    url(r'^packages/',
        PackageSearch.as_view(),
        name='packages'),

)
