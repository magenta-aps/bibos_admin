from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.template import Context

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView

from account.models import UserProfile

from models import Site, PC, PCGroup
from forms import SiteForm


@login_required
def index(request):
    user = request.user
    profile = user.get_profile()

    if profile.type == UserProfile.SUPER_ADMIN:
        # Redirect to list of sites
        return redirect('/sites/')
    else:
        # User belongs to one site only; redirect to that site
        site_url = profile.site.url
        return redirect('site/{0}/'.format(site_url))


# Site-based passive (non-form) views

class SiteView(DetailView):
    """Base class for all views based on a single site."""
    model = Site
    slug_field = 'uid'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SiteView, self).dispatch(*args, **kwargs)


# Now follows all site-based views, i.e. subclasses
# of SiteView.

class JobsView(SiteView):
    template_name = 'system/site_jobs.html'


class ScriptsView(SiteView):
    template_name = 'system/site_scripts.html'


class ComputersView(SiteView):

    template_name = 'system/site_computers.html'

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(ComputersView, self).get_context_data(**kwargs)
        site = context['site']
        if 'uid' in self.kwargs:
            uid = self.kwargs['uid']
            pc = get_object_or_404(PC, uid=uid)
        else:
            pc = site.pcs.all()[0]
        context['selected_pc'] = pc

        return context


class GroupsView(SiteView):

    template_name = 'system/site_groups.html'

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(GroupsView, self).get_context_data(**kwargs)
        # Then get selected group, if any
        site = context['site']
        if 'uid' in self.kwargs:
            uid = self.kwargs['uid']
            group = get_object_or_404(PCGroup, uid=uid)
        else:
            group = site.groups.all()[0]
        context['selected_group'] = group

        return context


class UsersView(SiteView):

    template_name = 'system/site_users.html'

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(UsersView, self).get_context_data(**kwargs)
        # Then get selected group, if any
        site = context['site']
        if 'uid' in self.kwargs:
            uid = self.kwargs['uid']
            user = get_object_or_404(User, username=uid)
        else:
            user = site.users[0] if len(site.users) > 1 else None
        context['selected_user'] = user
        # Add choices for UserProfile type
        choices = UserProfile.type_choices
        choices_dict = [{'id': k, 'val': v} for (k, v) in choices]
        context['choices'] = choices_dict

        return context


class SiteCreate(CreateView):
    model = Site
    form_class = SiteForm


class SiteUpdate(UpdateView):
    model = Site
    form_class = SiteForm
