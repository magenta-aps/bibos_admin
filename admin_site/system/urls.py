from django.conf.urls import patterns, url

from views import SiteList, SiteView, SiteCreate, SiteUpdate, SiteDelete
from views import AdminIndex, PCsView, GroupsView, UsersView, JobsView
from views import GroupCreate, GroupUpdate, GroupDelete, JobSearch, UserDelete
from views import SiteDetailView, UserCreate, UserUpdate, SiteConfiguration
from views import ScriptList, ScriptUpdate, ScriptCreate, ScriptDelete
from views import ScriptRun, PCUpdate, JobRestarter, MarkPackageUpgrade
from views import ConfigurationEntryCreate, ConfigurationEntryUpdate
from views import ConfigurationEntryDelete, DocView
from views import PackageSearch

urlpatterns = patterns(
    '',
    url(r'^$', AdminIndex.as_view(), name='index'),
    url(r'^sites/$', SiteList.as_view(), name='sites'),
    url(r'^sites/new/$', SiteCreate.as_view(), name='new_site'),
    url(r'^sites/(?P<slug>[ \w]+)/edit/$',
        SiteUpdate.as_view(),
        name='edit_site'),
    url(r'^sites/(?P<slug>[ \w]+)/delete/$',
        SiteDelete.as_view(),
        name='delete_site'),
    url(r'^site/(?P<slug>[ \w]+)/$', SiteDetailView.as_view(), name='site'),
    url(r'^site/(?P<slug>[ \w]+)/configuration/$',
        SiteConfiguration.as_view(),
        name='configuration'),
    url(r'^site/(?P<site_uid>[ \w]+)/configuration/new/$',
        ConfigurationEntryCreate.as_view(), name='new_config_entry'),
    url(r'^site/(?P<site_uid>[ \w]+)/configuration/edit/(?P<pk>\d+)/$',
        ConfigurationEntryUpdate.as_view(), name='edit_config_entry'),
    url(r'^site/(?P<site_uid>[ \w]+)/configuration/delete/(?P<pk>\d+)/$',
        ConfigurationEntryDelete.as_view(), name='delete_config_entry'),
    url(r'^site/(?P<slug>[ \w]+)/computers/$', PCsView.as_view(),
        name='computers'),
    url(r'^site/(?P<site_uid>[ \w]+)/computers/(?P<uid>\w+)/upgrade_packages/$',
        MarkPackageUpgrade.as_view(), name='mark_upgrade_packages'),
    url(r'^site/(?P<site_uid>[ \w]+)/computers/(?P<pc_uid>\w+)/$',
        PCUpdate.as_view(), name='computer'),
    url(r'^site/(?P<slug>[^/]+)/groups/$', GroupsView.as_view(),
        name='groups'),
    url(r'^site/(?P<site_uid>[ \w]+)/groups/new/$', GroupCreate.as_view(),
        name='new_group'),
    url(r'^site/(?P<site_uid>[ \w]+)/groups/(?P<group_uid>[ \w]+)/$',
        GroupUpdate.as_view(), name='group'),
    url(r'^site/(?P<site_uid>[ \w]+)/groups/(?P<group_uid>\w+)/delete/$',
        GroupDelete.as_view(), name='group_delete'),
    url(r'^site/(?P<slug>[ \w]+)/jobs/search/',
        JobSearch.as_view(),
        name='jobsearch'),
    url(r'^site/(?P<site_uid>[ \w]+)/jobs/(?P<pk>\d+)/restart/',
        JobRestarter.as_view(),
        name='restart_job'
    ),
    url(r'^site/(?P<slug>[ \w]+)/jobs/', JobsView.as_view(), name='jobs'),
    # Scripts
    url(r'^site/(?P<slug>[ \w]+)/scripts/(?P<script_pk>\d+)/delete/',
        ScriptDelete.as_view(),
        name='delete_script'),
    url(r'^site/(?P<slug>[ \w]+)/scripts/(?P<script_pk>\d+)/run/',
        ScriptRun.as_view(),
        name='run_script'),
    url(r'^site/(?P<slug>[ \w]+)/scripts/(?P<script_pk>\d+)/',
        ScriptUpdate.as_view(),
        name='script'),
    url(r'^site/(?P<slug>[ \w]+)/scripts/new/',
        ScriptCreate.as_view(),
        name='new_script'),
    url(r'^site/(?P<slug>[ \w]+)/scripts/',
        ScriptList.as_view(),
        name='scripts'),

    # Users
    url(r'^site/(?P<slug>[ \w]+)/users/$', UsersView.as_view(), name='users'),
    url(r'^site/(?P<site_uid>[ \w]+)/new_user/$',
        UserCreate.as_view(), name='new_user'),
    url(r'^site/(?P<site_uid>[ \w]+)/users/(?P<username>\w+)/$',
        UserUpdate.as_view(), name='user'),
    url(r'^site/(?P<site_uid>[ \w]+)/users/(?P<username>\w+)/delete/$',
        UserDelete.as_view(), name='delete_user'),

    # Packages
    url(r'^packages/', PackageSearch.as_view(), name='packages'),

    # Documentation
    url(r'^documentation/(?P<name>[ \w]+)/', DocView.as_view(), name='doc'),
    url(r'^documentation/', DocView.as_view(), name='doc_root'),
)
