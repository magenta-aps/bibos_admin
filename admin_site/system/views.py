# Create your views here.

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from account.models import UserProfile

from models import Site


@login_required
def index(request):
    user = request.user
    profile = user.get_profile()

    if profile.type == UserProfile.SUPER_ADMIN:
        # Redirect to list of sites
        return redirect('/sites/')
    else:
        # User belongs to one site only; redirect to that site
        site_url = profile.site.uid.lower()
        return redirect('site/{0}/'.format(site_url))


@login_required
def sites_overview(request):
    # TODO: Load site list into context and pass to render
    return render(request, 'system/sites.html')


# TODO TODO TODO
# Use a decorator to extract the site parameter of all
# SITE functions.
# TODO TODO TODO

@login_required
def site(request, site_uid):
    # TODO: Load site info into context, pass to render
    uid = site_uid.upper()
    try:
        site = Site.objects.get(uid=uid)
    except Site.NotFound:
        raise Http404
    context = { 'site': site.name, 'site_url': site.uid.lower() }
    return render(request, 'system/site_overview.html', context)


@login_required
def configuration(request, site_uid):
    # TODO: Load site info into context, pass to render
    uid = site_uid.upper()
    try:
        site = Site.objects.get(uid=uid)
    except Site.NotFound:
        raise Http404
    context = { 'site': site.name, 'site_url': site.uid.lower() }
    return render(request, 'system/site_configuration.html', context)


@login_required
def computers(request, site_uid):
    # TODO: Load site info into context, pass to render
    uid = site_uid.upper()
    try:
        site = Site.objects.get(uid=uid)
    except Site.NotFound:
        raise Http404
    context = { 'site': site.name, 'site_url': site.uid.lower() }
    return render(request, 'system/site_computers.html', context)


@login_required
def groups(request, site_uid):
    # TODO: Load site info into context, pass to render
    uid = site_uid.upper()
    try:
        site = Site.objects.get(uid=uid)
    except Site.NotFound:
        raise Http404
    context = { 'site': site.name, 'site_url': site.uid.lower() }
    return render(request, 'system/site_groups.html', context)


@login_required
def jobs(request, site_uid):
    # TODO: Load site info into context, pass to render
    uid = site_uid.upper()
    try:
        site = Site.objects.get(uid=uid)
    except Site.NotFound:
        raise Http404
    context = { 'site': site.name, 'site_url': site.uid.lower() }
    return render(request, 'system/site_jobs.html', context)


@login_required
def scripts(request, site_uid):
    # TODO: Load site info into context, pass to render
    uid = site_uid.upper()
    try:
        site = Site.objects.get(uid=uid)
    except Site.NotFound:
        raise Http404
    context = { 'site': site.name, 'site_url': site.uid.lower() }
    return render(request, 'system/site_scripts.html', context)


@login_required
def users(request, site_uid):
    # TODO: Load site info into context, pass to render
    uid = site_uid.upper()
    try:
        site = Site.objects.get(uid=uid)
    except Site.NotFound:
        raise Http404
    context = { 'site': site.name, 'site_url': site.uid.lower() }
    return render(request, 'system/site_users.html', context)
