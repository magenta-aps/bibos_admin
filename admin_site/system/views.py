from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.template import Context

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import View, ListView, DetailView, RedirectView

from account.models import UserProfile

from models import Site, PC, PCGroup
from forms import SiteForm, GroupForm


# Mixin class to require login
class LoginRequiredMixin(View):
    """Subclass in all views where login is required."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


# Mixin class for list selection (single select).
class SelectionMixin(View):
    """This supplies the ability to highlight a selected object of a given
    class. This is useful if a Detail view contains a list of children which
    the user is allowed to select."""
    # The Python class of the Django model corresponding to the objects you
    # want to be able to select. MUST be specified in subclass.
    selection_class = None
    # A callable which will return a list of objects which SHOULD belong to the
    # class specified by selection_class. MUST be specified in subclass.
    get_list = None
    # The field which is used to look up the selected object.
    lookup_field = 'uid'
    # Overrides the default class name in context.
    class_display_name = None

    def get_context_data(self, **kwargs):
        # First, call superclass
        context = super(SelectionMixin, self).get_context_data(**kwargs)
        # Then get selected object, if any
        if self.lookup_field in self.kwargs:
            lookup_val = self.kwargs[self.lookup_field]
            lookup_params = {self.lookup_field: lookup_val}
            selected = get_object_or_404(self.selection_class, **lookup_params)
        else:
            selected = self.get_list()[0] if self.get_list() else None

        display_name = (self.class_display_name if self.class_display_name else
                        self.selection_class.__name__.lower())
        context['selected_{0}'.format(display_name)] = selected

        return context


# Main index/site root view
class AdminIndex(RedirectView, LoginRequiredMixin):
    """Redirects to admin overview (sites list) or site main page."""
    def get_redirect_url(self, **kwargs):
        """Redirect based on user. This view will use the RequireLogin mixin,
        so we'll always have a logged-in user."""
        user = self.request.user
        profile = user.get_profile()

        if profile.type == UserProfile.SUPER_ADMIN:
            # Redirect to list of sites
            url = '/sites/'
        else:
            # User belongs to one site only; redirect to that site
            site_url = profile.site.url
            url = '/site/{0}/'.format(site_url)
        return url


# Site overview list to be displayed for super user
class SiteList(ListView, LoginRequiredMixin):
    """Displays list of sites."""
    model = Site
    context_object_name = 'site_list'


# Base class for Site-based passive (non-form) views
class SiteView(DetailView, LoginRequiredMixin):
    """Base class for all views based on a single site."""
    model = Site
    slug_field = 'uid'


# Now follows all site-based views, i.e. subclasses
# of SiteView.

class JobsView(SiteView):
    template_name = 'system/site_jobs.html'


class ScriptsView(SiteView):
    template_name = 'system/site_scripts.html'


class ComputersView(SelectionMixin, SiteView):

    template_name = 'system/site_computers.html'
    selection_class = PC

    def get_list(self):
        return self.object.pcs.all()


class GroupsView(SelectionMixin, SiteView):

    template_name = 'system/site_groups.html'
    selection_class = PCGroup
    class_display_name = 'group'

    def get_list(self):
        return self.object.groups.all()


class UsersView(SelectionMixin, SiteView):

    template_name = 'system/site_users.html'
    selection_class = User
    lookup_field = 'username'

    def get_list(self):
        return self.object.users

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(UsersView, self).get_context_data(**kwargs)
        # Add choices for UserProfile type
        choices = UserProfile.type_choices
        choices_dict = [{'id': k, 'val': v} for (k, v) in choices]
        context['choices'] = choices_dict

        return context


class SiteCreate(CreateView, LoginRequiredMixin):
    model = Site
    form_class = SiteForm
    slug_field = 'uid'


class SiteUpdate(UpdateView, LoginRequiredMixin):
    model = Site
    form_class = SiteForm
    slug_field = 'uid'

# TODO: This does NOT work yet!
# See
# https://docs.djangoproject.com/en/1.5/topics/class-based-views/mixins/#an-alternative-better-solution
# for hints on how to do this.
# TODO TODO TODO

class GroupCreate(CreateView, LoginRequiredMixin):
    model = PCGroup
    form_class = GroupForm
    slug_field = 'uid'

    def get_context_data(self, **kwargs):
        context = super(GroupCreate, self).get_context_data(**kwargs)
        site = Site.objects.get(uid=self.kwargs['site_uid'])
        context['site'] = site
        
        return context



class GroupUpdate(CreateView, LoginRequiredMixin):
    model = PCGroup
    slug_field = 'uid'
