from django.conf.urls import patterns, url

from system import views


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'sites/', views.sites_overview, name='sites'),
)
