# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

from functools import cmp_to_key
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View, ListView, DetailView, RedirectView
from django.views.generic import TemplateView

from django.db import transaction
from django.db.models import Q
from django.db.models import Count
from django.conf import settings

from account.models import UserProfile

from .models import Site, PC, PCGroup, ConfigurationEntry, Package
from .models import Job, Script, Input, SecurityProblem, SecurityEvent
from .models import MandatoryParameterMissingError
# PC Status codes
from .models import NEW, UPDATE
from .forms import SiteForm, GroupForm, ConfigurationEntryForm, ScriptForm
from .forms import UserForm, ParameterForm, PCForm, SecurityProblemForm

from urllib.parse import quote


def set_notification_cookie(response, message, error=False):
    descriptor = {
        "message": message,
        "type": "success" if not error else "error"
    }
    response.set_cookie('bibos-notification',
            quote(json.dumps(descriptor)))


def get_no_of_sec_events(site):
    """Utility function to get number of security events."""
    no_of_sec_events = SecurityEvent.objects.filter(
        problem__site=site
    ).exclude(
        problem__level=SecurityProblem.NORMAL
    ).exclude(status=SecurityEvent.RESOLVED).count()
    return no_of_sec_events


def get_latest_security_event(pc):
    """Utility function to get latest security event for pc."""
    sc = ""
    try:
        sc = SecurityEvent.objects.filter(pc_id=pc.id).latest('reported_time')
    except SecurityEvent.DoesNotExist:
        sc = "Ingen advarsler"
    return sc


# Mixin class to require login
class LoginRequiredMixin(View):
    """Subclass in all views where login is required."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class SuperAdminOnlyMixin(View):
    """Only allows access to super admins."""
    check_function = user_passes_test(lambda u: u.bibos_profile.type ==
                                      UserProfile.SUPER_ADMIN, login_url='/')

    @method_decorator(login_required)
    @method_decorator(check_function)
    def dispatch(self, *args, **kwargs):
        return super(SuperAdminOnlyMixin, self).dispatch(*args, **kwargs)


class SuperAdminOrThisSiteMixin(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Limit access to super users or users belonging to THIS site."""
        site = None
        slug_field = None
        # Find out which field is used as site slug
        if 'site_uid' in kwargs:
            slug_field = 'site_uid'
        elif 'slug' in kwargs:
            slug_field = 'slug'
        # If none given, give up
        if slug_field:
            site = get_object_or_404(Site, uid=kwargs[slug_field])
        check_function = user_passes_test(
            lambda u:
            (u.bibos_profile.type == UserProfile.SUPER_ADMIN) or
            (site and site == u.bibos_profile.site), login_url='/'
        )
        wrapped_super = check_function(
            super(SuperAdminOrThisSiteMixin, self).dispatch
        )
        return wrapped_super(*args, **kwargs)


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
        if selected is not None:
            context['selected_{0}'.format(display_name)] = selected
        context['{0}_list'.format(display_name)] = self.get_list()
        return context


class JSONResponseMixin(object):
    def render_to_response(self, context):
        """Returns a JSON response containing 'context' as payload"""
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        """Construct an `HttpResponse` object."""
        return HttpResponse(content,
                            content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        """Convert the context dictionary into a JSON object"""
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)


# Mixin class for CRUD views that use site_uid in URL
# The "site_uid" slug is configurable, but please avoid clashes
class SiteMixin(View):
    """Mixin class to extract site UID from URL"""

    site_uid = 'site_uid'

    def get_context_data(self, **kwargs):
        context = super(SiteMixin, self).get_context_data(**kwargs)
        site = get_object_or_404(Site, uid=self.kwargs[self.site_uid])
        context['site'] = site
        # Add information about outstanding security events.
        no_of_sec_events = get_no_of_sec_events(site)
        context['sec_events'] = no_of_sec_events

        return context


# Main index/site root view
class AdminIndex(RedirectView, LoginRequiredMixin):
    """Redirects to admin overview (sites list) or site main page."""
    def get_redirect_url(self, **kwargs):
        """Redirect based on user. This view will use the RequireLogin mixin,
        so we'll always have a logged-in user."""
        user = self.request.user
        profile = user.bibos_profile

        if profile.type == UserProfile.SUPER_ADMIN:
            # Redirect to list of sites
            url = '/sites/'
        else:
            # User belongs to one site only; redirect to that site
            site_url = profile.site.url
            url = '/site/{0}/'.format(site_url)
        return url


# Site overview list to be displayed for super user
class SiteList(ListView, SuperAdminOnlyMixin):
    """Displays list of sites."""
    model = Site
    context_object_name = 'site_list'


# Base class for Site-based passive (non-form) views
class SiteView(DetailView,  SuperAdminOrThisSiteMixin):
    """Base class for all views based on a single site."""
    model = Site
    slug_field = 'uid'

    def get_context_data(self, **kwargs):
        context = super(SiteView, self).get_context_data(**kwargs)
        site = self.get_object()
        # Add information about outstanding security events.
        no_of_sec_events = get_no_of_sec_events(site)
        context['sec_events'] = no_of_sec_events

        return context


class SiteDetailView(SiteView):
    """Class for showing the overview that is displayed when entering a site"""

    # For hver pc skal vi hente seneste security event.
    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        # Top level list of new PCs etc.
        context['pcs'] = self.object.pcs.filter(Q(is_active=False) |
                                                Q(is_update_required=True))
        context['pcs'] = sorted(context['pcs'], key=lambda s: s.name.lower())

        site = context['site']
        active_pcs = site.pcs.filter(is_active=True)
        context['active_pcs'] = active_pcs.count()
        context['ls_pcs'] = site.pcs.all().order_by('last_seen')
        securityevents = []
        for pc in context['ls_pcs']:
            securityevents.append(get_latest_security_event(pc))

        context['security_events'] = securityevents
        return context


class SiteConfiguration(SiteView):
    template_name = 'system/site_configuration.html'

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(SiteConfiguration, self).get_context_data(**kwargs)
        configs = self.object.configuration.entries.all()
        context['site_configs'] = configs.order_by('key')

        return context

    def post(self, request, *args, **kwargs):
        # Do basic method
        kwargs['updated'] = True
        response = self.get(request, *args, **kwargs)

        # Handle saving of data
        self.object.configuration.update_from_request(
            request.POST, 'site_configs'
        )

        set_notification_cookie(
            response,
            _('Configuration for %s updated') % kwargs['slug']
        )
        return response


# Now follows all site-based views, i.e. subclasses
# of SiteView.
class JobsView(SiteView):
    template_name = 'system/site_jobs.html'

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(JobsView, self).get_context_data(**kwargs)
        context['batches'] = self.object.batches.all()[:100]
        context['pcs'] = self.object.pcs.all()
        context['groups'] = self.object.groups.all()
        preselected = set([
            Job.NEW,
            Job.SUBMITTED,
            Job.RUNNING,
            Job.FAILED,
            Job.DONE,
        ])
        context['status_choices'] = [
            {
                'name': name,
                'value': value,
                'label': Job.STATUS_TO_LABEL[value],
                'checked':
                'checked="checked' if value in preselected else ''
            } for (value, name) in Job.STATUS_CHOICES
        ]
        params = self.request.GET or self.request.POST

        for k in ['batch', 'pc', 'group']:
            v = params.get(k, None)
            if v is not None and v.isdigit():
                context['selected_%s' % k] = int(v)

        return context


class JobSearch(JSONResponseMixin, SiteView):
    http_method_names = ['get', 'post']
    VALID_ORDER_BY = []
    for i in ['pk', 'batch__script__name', 'started', 'finished', 'status',
              'pc__name', 'batch__name']:
        VALID_ORDER_BY.append(i)
        VALID_ORDER_BY.append('-' + i)

    @staticmethod
    def get_jobs_display_data(joblist, site=None):
        if len(joblist) == 0:
            return []

        if site is None:
            site = joblist[0].batch.site
        return [{
            'pk': job.pk,
            'script_name': job.batch.script.name,
            'started': job.started.strftime("%Y-%m-%d %H:%M:%S") if
            job.started else None,
            'finished': job.finished.strftime("%Y-%m-%d %H:%M:%S") if
            job.finished else None,
            'status': job.status_translated + '',
            'label': job.status_label,
            'pc_name': job.pc.name,
            'batch_name': job.batch.name,
            # Yep, it's meant to be double-escaped - it's HTML-escaped
            # content that will be stored in an HTML attribute
            'has_info': job.has_info,
            'restart_url': '/site/%s/jobs/%s/restart/' % (site.uid, job.pk)
        } for job in joblist]

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(JobSearch, self).get_context_data(**kwargs)
        params = self.request.GET or self.request.POST
        query = {'batch__site': context['site']}

        if 'status' in params:
            query['status__in'] = params.getlist('status')

        for k in ['pc', 'batch']:
            v = params.get(k, '')
            if v != '':
                query[k] = v

        group = params.get('group', '')
        if group != '':
            query['pc__pc_groups'] = group

        orderby = params.get('orderby', '-pk')
        if orderby not in JobSearch.VALID_ORDER_BY:
            orderby = '-pk'
        limit = int(params.get('do_limit', '0'))

        if limit:
            context['job_list'] = Job.objects.filter(**query).order_by(
                orderby,
                'pk'
            )[:limit]
        else:
            context['job_list'] = Job.objects.filter(**query).order_by(
                orderby,
                'pk'
            )

        return context

    def convert_context_to_json(self, context):
        result = JobSearch.get_jobs_display_data(
            context['job_list'],
            site=context['site']
        )
        return json.dumps(result)


class JobRestarter(DetailView, SuperAdminOrThisSiteMixin):
    template_name = 'system/jobs/restart.html'
    model = Job

    def status_fail_response(self):
        response = HttpResponseRedirect(self.get_success_url())
        set_notification_cookie(
            response,
            _('Can only restart jobs with status %s') % Job.FAILED
        )
        return response

    def get(self, request, *args, **kwargs):
        self.site = get_object_or_404(Site, uid=kwargs['site_uid'])
        self.object = self.get_object()

        # Only restart jobs that have failed
        if self.object.status != Job.FAILED:
            return self.status_fail_response()

        context = self.get_context_data(object=self.object)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(JobRestarter, self).get_context_data(**kwargs)
        context['site'] = self.site
        context['selected_job'] = self.object
        return context

    def post(self, request, *args, **kwargs):
        self.site = get_object_or_404(Site, uid=kwargs['site_uid'])
        self.object = self.get_object()

        if self.object.status != Job.FAILED:
            return self.status_fail_response()

        new_job = self.object.restart(user=self.request.user)
        response = HttpResponseRedirect(self.get_success_url())
        set_notification_cookie(
            response,
            "Job %s restarted as job %s" % (self.object.pk, new_job.pk)
        )
        return response

    def get_success_url(self):
        return '/site/%s/jobs/' % self.kwargs['site_uid']


class JobInfo(DetailView, LoginRequiredMixin):
    template_name = 'system/jobs/info.html'
    model = Job

    def get(self, request, *args, **kwargs):
        self.site = get_object_or_404(Site, uid=kwargs['site_uid'])
        return super(JobInfo, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JobInfo, self).get_context_data(**kwargs)
        if self.site != self.object.batch.site:
            raise Http404
        context['site'] = self.site
        context['job'] = self.object
        return context


class ScriptMixin(object):
    script = None
    script_inputs = ''
    is_security = False

    def setup_script_editing(self, **kwargs):
        # Get site
        self.site = get_object_or_404(Site, uid=kwargs['slug'])
        # Add the global and local script lists
        self.scripts = Script.objects.filter(
            Q(site=self.site) | Q(site=None),
            is_security_script=self.is_security
        ).exclude(
            site__name='system'
        )

        if 'script_pk' in kwargs:
            self.script = get_object_or_404(Script, pk=kwargs['script_pk'])

    def get(self, request, *args, **kwargs):
        self.setup_script_editing(**kwargs)
        return super(ScriptMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.setup_script_editing(**kwargs)
        return super(ScriptMixin, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Get context from super class
        context = super(ScriptMixin, self).get_context_data(**kwargs)
        context['site'] = self.site
        context['local_scripts'] = sorted(self.scripts.filter(site=self.site),
                                          key=lambda s: s.name.lower())
        context['global_scripts'] = sorted(self.scripts.filter(site=None),
                                           key=lambda s: s.name.lower())

        context['script_inputs'] = self.script_inputs
        context['is_security'] = self.is_security
        if self.is_security:
            context['script_url'] = 'security_script'
        else:
            context['script_url'] = 'script'

        # If we selected a script add it to context
        if self.script is not None:
            context['selected_script'] = self.script
            if self.script.site is None:
                context['global_selected'] = True
            if context['script_inputs'] is '':
                context['script_inputs'] = [{
                    'pk': input.pk,
                    'name': input.name,
                    'value_type': input.value_type
                } for input in self.script.ordered_inputs]
        elif context['script_inputs'] is '':
            context['script_inputs'] = []

        context['script_inputs_json'] = json.dumps(context['script_inputs'])
        # Add information about outstanding security events.
        no_of_sec_events = get_no_of_sec_events(self.site)
        context['sec_events'] = no_of_sec_events

        return context

    def validate_script_inputs(self):
        params = self.request.POST
        num_inputs = params.get('script-number-of-inputs', 0)
        inputs = []
        success = True
        if int(num_inputs) > 0:
            for i in range(int(num_inputs)):
                data = {
                    'pk': params.get('script-input-%d-pk' % i, None),
                    'name': params.get('script-input-%d-name' % i, ''),
                    'value_type': params.get('script-input-%d-type' % i, ''),
                    'position': i,
                }

                if data['name'] is None or data['name'] == '':
                    data['name_error'] = 'Fejl: Du skal angive et navn'
                    success = False

                if data['value_type'] not in [value for (value, name)
                                              in Input.VALUE_CHOICES]:
                    data['type_error'] = 'Fejl: Du skal angive en korrekt type'
                    success = False

                inputs.append(data)

            self.script_inputs = inputs

        return success

    def save_script_inputs(self):
        seen = []
        for input_data in self.script_inputs:
            input_data['script'] = self.script

            pk = None
            if 'pk' in input_data:
                pk = input_data['pk'] or None
                del input_data['pk']

            if pk is None or pk == '':
                script_input = Input.objects.create(**input_data)
                script_input.save()
                seen.append(script_input.pk)
            else:
                Input.objects.filter(pk=pk).update(**input_data)
                seen.append(int(pk))

        for inp in self.script.inputs.all():
            if inp.pk not in seen:
                inp.delete()


class ScriptList(ScriptMixin, SiteView):
    template_name = 'system/scripts/list.html'

    def get(self, request, *args, **kwargs):
        self.setup_script_editing(**kwargs)
        try:
            # Sort by -site followed by lowercased name
            def sort_by(a, b):
                if a.site == b.site:
                    # cmp deprecated: cmp(a, b) has been changed to the ((a > b) - (a < b)) format
                    return ((a.name.lower() > b.name.lower()) - (a.name.lower() < b.name.lower()))
                else:
                    if b.site is not None:
                        return 1
                    else:
                        return -1
            # cmp deprecated: cmp converted to key function
            script = sorted(self.scripts, key=cmp_to_key(sort_by))[0]
            return HttpResponseRedirect(script.get_absolute_url(
            site_uid=self.site.uid
            ))
        except IndexError:
            return HttpResponseRedirect(
                "/site/%s/security/scripts/new/" % self.site.uid
                if self.is_security else
                "/site/%s/scripts/new/" % self.site.uid
            )


class ScriptCreate(ScriptMixin, CreateView, SuperAdminOrThisSiteMixin):
    template_name = 'system/scripts/create.html'
    form_class = ScriptForm

    def get_context_data(self, **kwargs):
        context = super(ScriptCreate, self).get_context_data(**kwargs)
        context['type_choices'] = Input.VALUE_CHOICES
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super(ScriptCreate, self).get_form(form_class)
        form.prefix = 'create'
        return form

    def form_valid(self, form):
        if self.validate_script_inputs():
            self.object = form.save()
            self.script = self.object
            if self.is_security:
                self.object.is_security_script = True
                self.object.save()
            self.save_script_inputs()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form, transfer_inputs=False)

    def form_invalid(self, form, transfer_inputs=True):
        if transfer_inputs:
            self.validate_script_inputs()

        return super(ScriptCreate, self).form_invalid(form)

    def get_success_url(self):
        if self.is_security:
            return '/site/%s/security/scripts/%s/' % (self.site.uid,
                                                      self.script.pk)
        else:
            return '/site/%s/scripts/%s/' % (self.site.uid, self.script.pk)


class ScriptUpdate(ScriptMixin, UpdateView, LoginRequiredMixin):
    template_name = 'system/scripts/update.html'
    form_class = ScriptForm

    def get_context_data(self, **kwargs):
        # Get context from super class
        context = super(ScriptUpdate, self).get_context_data(**kwargs)
        if self.script is not None and self.script.executable_code is not None:
            context['script_preview'] = self.script.executable_code.read(4096)
        context['type_choices'] = Input.VALUE_CHOICES
        self.create_form = ScriptForm()
        self.create_form.prefix = 'create'
        context['create_form'] = self.create_form
        return context

    def get_object(self, queryset=None):
        return self.script

    def form_valid(self, form):
        if self.validate_script_inputs():
            self.save_script_inputs()
            response = super(ScriptUpdate, self).form_valid(form)
            set_notification_cookie(
                response,
                _('Script %s updated') % self.script.name
            )
            return response
        else:
            return self.form_invalid(form, transfer_inputs=False)

    def form_invalid(self, form, transfer_inputs=True):
        if transfer_inputs:
            self.validate_script_inputs()

        return super(ScriptUpdate, self).form_invalid(form)

    def get_success_url(self):
        if self.is_security:
            return '/site/%s/security/scripts/%s/' % (self.site.uid,
                                                      self.script.pk)
        else:
            return '/site/%s/scripts/%s/' % (self.site.uid, self.script.pk)


class ScriptRun(SiteView):
    action = None
    form = None
    STEP1 = 'choose_pcs_and_groups'
    STEP2 = 'choose_parameters'
    STEP3 = 'run_script'

    def post(self, request, *args, **kwargs):
        return super(ScriptRun, self).get(request, *args, **kwargs)

    def step1(self, context):
        self.template_name = 'system/scripts/run_step1.html'
        context['pcs'] = self.object.pcs.all().order_by('name')
        context['groups'] = self.object.groups.all().order_by('name')
        context['action'] = ScriptRun.STEP2

    def step2(self, context):
        self.template_name = 'system/scripts/run_step2.html'
        if 'pcs' not in context:
            # Transfer chosen groups and PCs as PC pks
            pcs = [int(pk) for pk in self.request.POST.getlist('pcs', [])]
            for group_pk in self.request.POST.getlist('groups', []):
                group = PCGroup.objects.get(pk=group_pk)
                for pc in group.pcs.all():
                    pcs.append(int(pc.pk))
            # Uniquify
            context['pcs'] = list(set(pcs))

        if len(context['pcs']) == 0:
            context['message'] = _('You must specify at least one group or pc')
            self.step1(context)
            return

        # Set up the form
        if 'form' not in context:
            context['form'] = ParameterForm(script=context['script'])

        # Go to step3 on submit
        context['action'] = ScriptRun.STEP3

    def step3(self, context):
        self.template_name = 'system/scripts/run_step3.html'
        form = ParameterForm(self.request.POST,
                             self.request.FILES,
                             script=context['script'])
        context['form'] = form
        pcs = self.request.POST.getlist('pcs', [])

        context['num_pcs'] = len(pcs)
        if context['num_pcs'] == 0:
            context['message'] = _('You must specify at least one group or pc')
            self.step1(context)
            return

        if not form.is_valid():
            self.step2(context)
        else:
            args = []
            for i in range(0, context['script'].inputs.count()):
                args.append(form.cleaned_data['parameter_%s' % i])

            context['batch'] = context['script'].run_on(
                context['site'],
                PC.objects.filter(pk__in=pcs),
                *args,
                user=self.request.user
            )

    def get_context_data(self, **kwargs):
        context = super(ScriptRun, self).get_context_data(**kwargs)
        context['script'] = get_object_or_404(Script,
                                              pk=self.kwargs['script_pk'])

        action = self.request.POST.get('action', 'choose_pcs_and_groups')
        if action == ScriptRun.STEP1:
            self.step1(context)
        elif action == ScriptRun.STEP2:
            self.step2(context)
        elif action == ScriptRun.STEP3:
            self.step3(context)
        else:
            raise Exception(
                "POST to ScriptRun with wrong action %s" % self.action
            )

        return context


class ScriptDelete(ScriptMixin, DeleteView):
    pass


class PCsView(SelectionMixin, SiteView):

    template_name = 'system/site_pcs.html'
    selection_class = PC

    def get_list(self):
        return self.object.pcs.all().extra(
            select={'lower_name': 'lower(name)'}
        ).order_by('lower_name')

    def render_to_response(self, context):
        if('selected_pc' in context):
            return HttpResponseRedirect('/site/%s/computers/%s/' % (
                context['site'].uid,
                context['selected_pc'].uid
            ))
        else:
            return super(PCsView, self).render_to_response(context)


class PCUpdate(SiteMixin, UpdateView, LoginRequiredMixin):
    template_name = 'system/pc_form.html'
    form_class = PCForm
    slug_field = 'uid'

    VALID_ORDER_BY = []
    for i in ['pk', 'batch__script__name', 'started', 'finished', 'status',
              'batch__name']:
        VALID_ORDER_BY.append(i)
        VALID_ORDER_BY.append('-' + i)

    def get_object(self, queryset=None):
        return PC.objects.get(uid=self.kwargs['pc_uid'])

    def get_context_data(self, **kwargs):
        context = super(PCUpdate, self).get_context_data(**kwargs)

        site = context['site']
        form = context['form']
        pc = self.object
        params = self.request.GET or self.request.POST

        context['pc_list'] = site.pcs.all().extra(
            select={'lower_name': 'lower(name)'}
        ).order_by('lower_name')

        waiting_for_packages = False
        pkg_list_count = pc.package_list.packages.count()
        if (not pc.is_active) or (pkg_list_count == 0):
            waiting_for_packages = True

        context['waiting_for_package_list'] = waiting_for_packages
        if not waiting_for_packages:
            group_set = site.groups.all()

            selected_group_ids = form['pc_groups'].value()
            context['available_groups'] = group_set.exclude(
                pk__in=selected_group_ids
            )
            context['selected_groups'] = group_set.filter(
                pk__in=selected_group_ids
            )

            ii = self.object.custom_packages.install_infos
            context['package_infos'] = ii.order_by('-do_add', 'package__name')

            a, r = pc.pending_package_updates
            context['pending_packages_add'] = sorted(a)
            context['pending_packages_remove'] = sorted(r)

        orderby = params.get('orderby', '-pk')
        if orderby not in JobSearch.VALID_ORDER_BY:
            orderby = '-pk'
        context['joblist'] = pc.jobs.order_by('status', 'pk').order_by(
            orderby,
            'pk'
        )

        if orderby.startswith('-'):
            context['orderby_key'] = orderby[1:]
            context['orderby_direction'] = 'desc'
        else:
            context['orderby_key'] = orderby
            context['orderby_direction'] = 'asc'

        context['orderby_base_url'] = pc.get_absolute_url() + '?'

        context['selected_pc'] = pc

        context['security_event'] = get_latest_security_event(pc)
        context['has_security_warnings'] = pc.securityevent_set.exclude(
            status=SecurityEvent.RESOLVED
        ).exclude(
            problem__level=SecurityProblem.NORMAL
        ).count() > 0

        return context

    def form_valid(self, form):
        self.object.custom_packages.update_by_package_names(
            self.request.POST.getlist('pc_packages_add'),
            self.request.POST.getlist('pc_packages_remove')
        )
        self.object.configuration.update_from_request(
            self.request.POST, 'pc_config'
        )
        response = super(PCUpdate, self).form_valid(form)
        set_notification_cookie(
            response,
            _('Computer %s updated') % self.object.name
        )
        return response


class PCDelete(DeleteView, SuperAdminOrThisSiteMixin):
    model = PC

    def get_object(self, queryset=None):
        return PC.objects.get(uid=self.kwargs['pc_uid'])

    def get_success_url(self):
        return '/site/{0}/computers/'.format(self.kwargs['site_uid'])


class MarkPackageUpgrade(SiteMixin, View):
    def post(self, request, *args, **kwargs):
        site = get_object_or_404(Site, uid=kwargs['site_uid'])
        pc = get_object_or_404(PC, uid=kwargs['uid'])
        num = pc.package_list.flag_for_upgrade(
            request.POST.getlist('packages', [])
        )
        response = HttpResponseRedirect(
            '/site/%s/computers/%s/#pc-packages' % (
                site.uid,
                pc.uid
            )
        )
        set_notification_cookie(
            response,
            _('Marked %s packages for upgrade') % num
        )
        return response


class GroupsView(SelectionMixin, SiteView):
    template_name = 'system/site_groups.html'
    selection_class = PCGroup
    class_display_name = 'group'

    def get_list(self):
        return self.object.groups.all().extra(
            select={'lower_name': 'lower(name)'}
        ).order_by('lower_name')

    def render_to_response(self, context):
        if('selected_group' in context):
            return HttpResponseRedirect('/site/%s/groups/%s/' % (
                context['site'].uid,
                context['selected_group'].url
            ))
        else:
            return HttpResponseRedirect(
                '/site/%s/groups/new/' % context['site'].uid,
            )


class UsersView(SelectionMixin, SiteView):

    template_name = 'system/site_users.html'
    selection_class = User
    lookup_field = 'username'

    def get_list(self):
        return self.object.users

    def render_to_response(self, context):
        if('selected_user' in context):
            return HttpResponseRedirect('/site/%s/users/%s/' % (
                context['site'].uid,
                context['selected_user'].username
            ))
        else:
            return HttpResponseRedirect(
                '/site/%s/new_user/' % context['site'].uid,
            )


class UsersMixin(object):
    def add_site_to_context(self, context):
        self.site = get_object_or_404(Site, uid=self.kwargs['site_uid'])
        context['site'] = self.site
        return context

    def add_userlist_to_context(self, context):
        if 'site' not in context:
            self.add_site_to_context(context)
        context['user_list'] = context['site'].users
        # Add information about outstanding security events.
        no_of_sec_events = get_no_of_sec_events(self.site)
        context['sec_events'] = no_of_sec_events
        return context


class UserCreate(CreateView, UsersMixin, SuperAdminOrThisSiteMixin):
    model = User
    form_class = UserForm
    lookup_field = 'username'
    template_name = 'system/users/create.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super(UserCreate, self).get_form(form_class)
        form.prefix = 'create'
        return form

    def get_context_data(self, **kwargs):
        context = super(UserCreate, self).get_context_data(**kwargs)
        self.add_userlist_to_context(context)
        return context

    def form_valid(self, form):
        self.object = form.save()

        site = get_object_or_404(Site, uid=self.kwargs['site_uid'])
        UserProfile.objects.create(
            user=self.object,
            type=form.cleaned_data['usertype'],
            site=site
        )
        result = super(UserCreate, self).form_valid(form)
        return result

    def get_success_url(self):
        return '/site/%s/users/%s/' % (
            self.kwargs['site_uid'],
            self.object.username
        )


class UserUpdate(UpdateView, UsersMixin, SuperAdminOrThisSiteMixin):
    model = User
    form_class = UserForm
    template_name = 'system/users/update.html'

    def get_object(self, queryset=None):
        self.selected_user = User.objects.get(username=self.kwargs['username'])
        return self.selected_user

    def get_context_data(self, **kwargs):
        self.context_object_name = 'selected_user'
        context = super(UserUpdate, self).get_context_data(**kwargs)
        self.add_userlist_to_context(context)

        loginusertype = self.request.user.bibos_profile.type

        context['selected_user'] = self.selected_user
        context['form'].setup_usertype_choices(loginusertype)

        context['create_form'] = UserForm(prefix='create')
        context['create_form'].setup_usertype_choices(loginusertype)

        return context

    def form_valid(self, form):
        self.object = form.save()

        profile = self.object.bibos_profile
        profile.type = form.cleaned_data['usertype']
        response = super(UserUpdate, self).form_valid(form)
        set_notification_cookie(
            response,
            _('User %s updated') % self.object.username
        )
        return response

    def get_success_url(self):
        return '/site/%s/users/%s/' % (
            self.kwargs['site_uid'],
            self.object.username
        )


class UserDelete(DeleteView, UsersMixin, SuperAdminOrThisSiteMixin):
    model = User
    template_name = 'system/users/delete.html'

    def get_object(self, queryset=None):
        self.selected_user = User.objects.get(username=self.kwargs['username'])
        return self.selected_user

    def get_context_data(self, **kwargs):
        context = super(UserDelete, self).get_context_data(**kwargs)
        self.add_userlist_to_context(context)
        context['selected_user'] = self.selected_user
        context['create_form'] = UserForm(prefix='create')

        return context

    def get_success_url(self):
        return '/site/%s/users/' % self.kwargs['site_uid']

    def delete(self, request, *args, **kwargs):
        response = super(UserDelete, self).delete(request, *args, **kwargs)
        set_notification_cookie(
            response,
            _('User %s deleted') % self.kwargs['username']
        )
        return response


class SiteCreate(CreateView, SuperAdminOnlyMixin):
    model = Site
    form_class = SiteForm
    slug_field = 'uid'

    def get_success_url(self):
        return '/sites/'


class SiteUpdate(UpdateView, SuperAdminOnlyMixin):
    model = Site
    form_class = SiteForm
    slug_field = 'uid'

    def get_success_url(self):
        return '/sites/'


class SiteDelete(DeleteView, SuperAdminOnlyMixin):
    model = Site
    slug_field = 'uid'

    def get_success_url(self):
        return '/sites/'


class ConfigurationEntryCreate(SiteMixin, CreateView,
                               SuperAdminOrThisSiteMixin):
    model = ConfigurationEntry
    form_class = ConfigurationEntryForm

    def form_valid(self, form):
        site = get_object_or_404(Site, uid=self.kwargs['site_uid'])
        self.object = form.save(commit=False)
        self.object.owner_configuration = site.configuration

        return super(ConfigurationEntryCreate, self).form_valid(form)

    def get_success_url(self):
        return '/site/{0}/configuration/'.format(self.kwargs['site_uid'])


class ConfigurationEntryUpdate(SiteMixin, UpdateView,
                               SuperAdminOrThisSiteMixin):
    model = ConfigurationEntry
    form_class = ConfigurationEntryForm

    def get_success_url(self):
        return '/site/{0}/configuration/'.format(self.kwargs['site_uid'])


class ConfigurationEntryDelete(SiteMixin, DeleteView,
                               SuperAdminOrThisSiteMixin):
    model = ConfigurationEntry

    def get_success_url(self):
        return '/site/{0}/configuration/'.format(self.kwargs['site_uid'])


class GroupCreate(SiteMixin, CreateView, SuperAdminOrThisSiteMixin):
    model = PCGroup
    form_class = GroupForm
    slug_field = 'uid'

    def get_context_data(self, **kwargs):
        context = super(GroupCreate, self).get_context_data(**kwargs)

        # We don't want to edit computers yet
        if 'pcs' in context['form'].fields:
            del context['form'].fields['pcs']

        return context

    def form_valid(self, form):
        site = get_object_or_404(Site, uid=self.kwargs['site_uid'])
        self.object = form.save(commit=False)
        self.object.site = site

        return super(GroupCreate, self).form_valid(form)


class Error(Exception):
    pass


class OutdatedClientError(Error):
    pass


class GroupUpdate(SiteMixin, SuperAdminOrThisSiteMixin, UpdateView):
    template_name = 'system/site_groups.html'
    form_class = GroupForm
    model = PCGroup

    def get_object(self, queryset=None):
        return PCGroup.objects.get(uid=self.kwargs['group_uid'])

    def get_context_data(self, **kwargs):
        context = super(GroupUpdate, self).get_context_data(**kwargs)

        group = self.object
        form = context['form']
        site = context['site']

        ii = group.custom_packages.install_infos
        context['package_infos'] = ii.order_by('-do_add', 'package__name')

        pc_queryset = site.pcs.filter(is_active=True).annotate(
            pkg_count=Count('package_list__statuses')
        ).filter(pkg_count__gt=0)
        form.fields['pcs'].queryset = pc_queryset

        selected_pc_ids = form['pcs'].value()
        context['available_pcs'] = pc_queryset.exclude(
            pk__in=selected_pc_ids
        )
        context['selected_pcs'] = pc_queryset.filter(
            pk__in=selected_pc_ids
        )

        context['selected_group'] = group

        context['newform'] = GroupForm()
        del context['newform'].fields['pcs']

        context['all_scripts'] = sorted(
            Script.objects.filter(
                Q(site=site) | Q(site=None),
                is_security_script=False
            ).exclude(
                site__name='system'
            ), key=lambda s: s.name.lower())

        return context

    def form_valid(self, form):
        # Capture a view of the group's PCs and policy scripts before the
        # update
        members_pre = set(self.object.pcs.all())
        policy_pre = set(self.object.policy.all())

        try:
            with transaction.atomic():
                self.object.custom_packages.update_by_package_names(
                    self.request.POST.getlist('group_packages_add'),
                    self.request.POST.getlist('group_packages_remove')
                )
                self.object.configuration.update_from_request(
                    self.request.POST, 'group_configuration'
                )
                self.object.update_policy_from_request(
                    self.request, 'group_policies'
                )

                response = super(GroupUpdate, self).form_valid(form)

                members_post = set(self.object.pcs.all())
                policy_post = set(self.object.policy.all())

                # Work out which PCs and policy scripts have come and gone
                surviving_members = members_post.intersection(members_pre)
                new_members = members_post.difference(members_pre)
                new_policy = policy_post.difference(policy_pre)

                # If we have a policy, make sure all group members actually
                # support ordered job execution
                if len(policy_post) > 0:
                    for g in members_post:
                        if not g.supports_ordered_job_execution():
                            raise OutdatedClientError(g)

                # Run all policy scripts on new PCs...
                if new_members:
                    ordered_policy = list(policy_post)
                    ordered_policy.sort(key=lambda asc: asc.position)
                    for asc in ordered_policy:
                        asc.run_on(self.request.user, new_members)

                new_policy = list(new_policy)
                new_policy.sort(key=lambda asc: asc.position)
                # ... and run new policy scripts on old PCs
                for asc in new_policy:
                    asc.run_on(self.request.user, surviving_members)

                set_notification_cookie(
                    response,
                    _('Group %s updated') % self.object.name
                )
                return response
        except OutdatedClientError as e:
            set_notification_cookie(
                response,
                _('Computer {0} must be upgraded in order to join a group with scripts attached').format(e),
                error=True)
            return response
        except MandatoryParameterMissingError as e:
            # If this happens, it happens *before* we have a valid
            # HttpResponse, so make one with form_invalid()
            response = self.form_invalid(form)
            parameter = e.args[0]
            set_notification_cookie(
                response,
                _('No value was specified for the mandatory input "{0}" of script "{1}"').format(
                        parameter.name, parameter.script.name),
                error=True)
            return response

    def form_invalid(self, form):
        return super(GroupUpdate, self).form_invalid(form)


class GroupDelete(SiteMixin, SuperAdminOrThisSiteMixin, DeleteView):
    model = PCGroup

    def get_object(self, queryset=None):
        return PCGroup.objects.get(uid=self.kwargs['group_uid'])

    def get_success_url(self):
        return '/site/{0}/groups/'.format(self.kwargs['site_uid'])

    def delete(self, request, *args, **kwargs):
        name = self.get_object().name
        response = super(GroupDelete, self).delete(request, *args, **kwargs)
        set_notification_cookie(
            response,
            _('Group %s deleted') % name
        )
        return response


class SecurityProblemsView(SelectionMixin, SiteView):

    template_name = 'system/site_security_problems.html'
    selection_class = SecurityProblem
    class_display_name = 'security_problem'

    def get_list(self):
        return self.object.security_problems.all().extra(
            select={'lower_name': 'lower(name)'}
        ).order_by('lower_name')

    def render_to_response(self, context):
        if 'selected_security_problem' in context:
            return HttpResponseRedirect('/site/%s/security_problems/%s/' % (
                context['site'].uid,
                context['selected_security_problem'].uid
            ))
        else:
            """
            return HttpResponseRedirect(
                '/site/%s/security_problems/new/' % context['site'].uid,
            )
            """
            site = context['site']
            context['newform'] = SecurityProblemForm()
            context['newform'].fields[
                'alert_users'
            ].queryset = User.objects.filter(bibos_profile__site=site)
            context['newform'].fields[
                'alert_groups'
            ].queryset = site.groups.all()
            # Limit list of scripts to only include security scripts.
            script_set = Script.objects.filter(
                Q(site__isnull=True) | Q(site=site)
            ).filter(is_security_script=True)
            context['newform'].fields['script'].queryset = script_set

            return super(
                SecurityProblemsView, self
            ).render_to_response(context)


class SecurityProblemCreate(SiteMixin, CreateView, SuperAdminOrThisSiteMixin):
    template_name = 'system/site_security_problems.html'
    model = SecurityProblem
    fields = '__all__'

    def get_success_url(self):
        return '/site/{0}/security_problems/'.format(self.kwargs['site_uid'])


class SecurityProblemUpdate(SiteMixin, UpdateView, SuperAdminOrThisSiteMixin):
    template_name = 'system/site_security_problems.html'
    model = SecurityProblem
    form_class = SecurityProblemForm

    def get_object(self, queryset=None):
        return SecurityProblem.objects.get(uid=self.kwargs['uid'],
                                           site__uid=self.kwargs['site_uid'])

    def get_context_data(self, **kwargs):

        context = super(SecurityProblemUpdate, self).get_context_data(**kwargs)

        site = context['site']
        form = context['form']
        group_set = site.groups.all()
        selected_group_ids = form['alert_groups'].value()
        context['available_groups'] = group_set.exclude(
            pk__in=selected_group_ids
        )
        context['selected_groups'] = group_set.filter(
            pk__in=selected_group_ids
        )

        user_set = User.objects.filter(bibos_profile__site=site)
        selected_user_ids = form['alert_users'].value()
        context['available_users'] = user_set.exclude(
            pk__in=selected_user_ids
        )
        context['selected_users'] = user_set.filter(
            pk__in=selected_user_ids
        )
        # Limit list of scripts to only include security scripts.
        script_set = Script.objects.filter(
            Q(site__isnull=True) | Q(site=site)
        ).filter(is_security_script=True)
        form.fields['script'].queryset = script_set

        # TODO: If the JS available/selected stuff above works out, the next
        # two lines can be deleted.
        form.fields['alert_users'].queryset = user_set
        form.fields['alert_groups'].queryset = group_set
        # Extra fields
        context['selected_security_problem'] = self.object
        context['newform'] = SecurityProblemForm()
        context['newform'].fields['script'].queryset = script_set
        context['newform'].fields['alert_users'].queryset = user_set
        context['newform'].fields['alert_groups'].queryset = group_set

        return context

    def get_success_url(self):
        return '/site/{0}/security_problems/'.format(self.kwargs['site_uid'])


class SecurityProblemDelete(SiteMixin, DeleteView, SuperAdminOrThisSiteMixin):
    model = SecurityProblem
    # form_class = <hopefully_not_necessary>

    def get_object(self, queryset=None):
        return SecurityProblem.objects.get(uid=self.kwargs['uid'],
                                           site__uid=self.kwargs['site_uid'])

    def get_success_url(self):
        return '/site/{0}/security_problems/'.format(self.kwargs['site_uid'])


class SecurityEventsView(SiteView):
    template_name = 'system/site_security.html'

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(SecurityEventsView, self).get_context_data(**kwargs)
        # Supply extra info as needed.
        level_preselected = set([
            SecurityProblem.CRITICAL,
            SecurityProblem.HIGH
        ])
        context['level_choices'] = [
            {
                'name': name,
                'value': value,
                'label': SecurityProblem.LEVEL_TO_LABEL[value],
                'checked':
                'checked="checked' if value in level_preselected else ''
            } for (value, name) in SecurityProblem.LEVEL_CHOICES
        ]
        status_preselected = set([
            SecurityEvent.NEW,
            SecurityEvent.ASSIGNED
        ])
        context['status_choices'] = [
            {
                'name': name,
                'value': value,
                'label': SecurityEvent.STATUS_TO_LABEL[value],
                'checked':
                'checked="checked' if value in status_preselected else ''
            } for (value, name) in SecurityEvent.STATUS_CHOICES
        ]

        if 'pc_uid' in self.kwargs:
            context['pc_uid'] = self.kwargs['pc_uid']
        return context


class SecurityEventSearch(JSONResponseMixin, SiteView):
    http_method_names = ['get', 'post']
    VALID_ORDER_BY = []
    for i in [
        'pk', 'problem__name', 'occurred_time', 'assigned_user__username'
    ]:
        VALID_ORDER_BY.append(i)
        VALID_ORDER_BY.append('-' + i)

    @staticmethod
    def get_event_display_data(eventlist, site=None):
        if len(eventlist) == 0:
            return []

        if site is None:
            site = eventlist[0].batch.site

        return [{
            'pk': event.pk,
            'site_uid': site.uid,
            'problem_name': event.problem.name,
            'pc_id': event.pc.id,
            'occurred': event.ocurred_time.strftime("%Y-%m-%d %H:%M:%S"),
            'status': event.get_status_display(),
            'status_label': event.STATUS_TO_LABEL[event.status],
            'level': SecurityProblem.LEVEL_TO_LABEL[event.problem.level] + '',
            'pc_name': event.pc.name,
            'assigned_user': (event.assigned_user.username if
                              event.assigned_user else '')
        } for event in eventlist]

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(SecurityEventSearch, self).get_context_data(**kwargs)
        params = self.request.GET or self.request.POST
        query = {'problem__site': context['site']}
        if params.get('pc', None):
            query['pc__uid'] = params['pc']

        if 'level' in params:
            query['problem__level__in'] = params.getlist('level')

        if 'status' in params:
            query['status__in'] = params.getlist('status')

        orderby = params.get('orderby', '-pk')
        if orderby not in SecurityEventSearch.VALID_ORDER_BY:
            orderby = '-pk'
        limit = int(params.get('do_limit', '0'))

        if limit:
            context[
                'securityevent_list'
            ] = SecurityEvent.objects.filter(**query).order_by(
                orderby,
                'pk'
            )[:limit]
        else:
            context[
                'securityevent_list'
            ] = SecurityEvent.objects.filter(**query).order_by(
                orderby,
                'pk'
            )
        return context

    def convert_context_to_json(self, context):
        result = SecurityEventSearch.get_event_display_data(
            context['securityevent_list'],
            site=context['site']
        )
        # print json.dumps(result)
        return json.dumps(result)


class SecurityEventUpdate(SiteMixin, UpdateView, SuperAdminOrThisSiteMixin):
    model = SecurityEvent
    fields = ['assigned_user', 'status', 'note']

    def get_object(self, queryset=None):
        return SecurityEvent.objects.get(id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(SecurityEventUpdate, self).get_context_data(**kwargs)

        qs = context["form"].fields["assigned_user"].queryset
        qs = qs.filter(
                Q(bibos_profile__site=self.get_object().pc.site) |
                Q(bibos_profile__type=UserProfile.SUPER_ADMIN))
        context["form"].fields["assigned_user"].queryset = qs

        # Set fields to read-only
        return context

    def post(self, request, *args, **kwargs):
        result = super(SecurityEventUpdate,
                       self).post(request, *args, **kwargs)
        return result

    def get_success_url(self):
        return '/site/{0}/security/'.format(self.kwargs['site_uid'])


class PackageSearch(JSONResponseMixin, ListView):
    raw_result = False

    def get_queryset(self):
        params = self.request.GET or self.request.POST

        by_name = params.get('get_by_name', None)
        if by_name:
            return Package.objects.filter(name=by_name)[:1]

        q = params.get('q', None)
        conditions = []
        if q is not None:
            conditions.append(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )

        qs = Package.objects.filter(*conditions)

        if params.get('distinct_by_name', None):
            self.raw_result = True
            qs = qs.values('name', 'description').annotate()
            qs = qs.order_by('name', 'description')
        else:
            qs = qs.order_by('name', 'version')

        try:
            limit = int(params.get('limit', 20))
        except:
            limit = 10

        if limit == 'all':
            return qs
        else:
            return qs[:limit]

    def convert_context_to_json(self, context):
        if(self.raw_result):
            return json.dumps([i for i in self.object_list])
        else:
            return json.dumps([{
                'pk': p.pk,
                'name': p.name,
                'description': p.description,
                'version': p.version
            } for p in self.object_list])


documentation_menu_items = [
    ('', 'BibOS Administration'),
    ('status', 'Status'),
    ('site_configuration', 'Site-konfiguration'),
    ('computers', 'Computere'),
    ('groups', 'Grupper'),
    ('jobs', 'Jobs'),
    ('scripts', 'Scripts'),
    ('users', 'Brugere'),

    ('', 'Installation af BibOS'),
    ('install_dvd', 'Installation via DVD'),
    ('install_usb', 'Installation via USB'),
    ('install_network', 'Installation via netværk'),
    ('postinstall', 'Postinstall-script'),
    ('pdf_guide', 'Brugervenlig installationsguide (PDF)'),

    ('', 'BibOS-gateway'),
    ('gateway_install', 'Installation af BibOS-gateway'),
    ('gateway_admin', 'Administration af gateway'),
    ('gateway_use', 'Anvendelse af gateway på BibOS-maskiner'),
    ('', 'Om'),
    ('om_bibos_admin', 'Om BibOS-Admin'),

    ('', 'Teknisk dokumentation'),
    ('tech/bibos', 'BibOS teknisk dokumentation'),
    ('tech/admin', 'BibOS Admin teknisk dokumentation'),

]


class DocView(TemplateView):
    docname = 'status'

    def template_exists(self, subpath):
        fullpath = os.path.join(settings.TEMPLATE_DIRS[0], subpath)
        return os.path.isfile(fullpath)

    def get_context_data(self, **kwargs):  # noqa
        if 'name' in self.kwargs:
            self.docname = self.kwargs['name']
        else:
            # This will be mapped to documentation/index.html
            self.docname = 'index'

        if self.docname.find("..") != -1:
            raise Http404

        # Try <docname>.html and <docname>/index.html
        name_templates = [
            'documentation/{0}.html',
            'documentation/{0}/index.html'
        ]

        templatename = None
        for nt in name_templates:
            expanded = nt.format(self.docname)
            if self.template_exists(expanded):
                templatename = expanded
                break

        if templatename is None:
            raise Http404
        else:
            self.template_name = templatename

        context = super(DocView, self).get_context_data(**kwargs)
        context['docmenuitems'] = documentation_menu_items
        docnames = self.docname.split("/")

        context['menu_active'] = docnames[0]

        # Set heading according to chosen item
        current_heading = None
        for link, name in context['docmenuitems']:
            if link == '':
                current_heading = name
            elif link == docnames[0]:
                context['docheading'] = current_heading
                break

        # Add a submenu if it exists
        submenu_template = "documentation/" + docnames[0] + "/__submenu__.html"
        if self.template_exists(submenu_template):
            context['submenu_template'] = submenu_template

        if len(docnames) > 1 and docnames[1]:
            # Don't allow direct access to submenus
            if docnames[1] == '__submenu__':
                raise Http404
            context['submenu_active'] = docnames[1]

        params = self.request.GET or self.request.POST
        back_link = params.get('back')
        if back_link is None:
            referer = self.request.META.get('HTTP_REFERER')
            if referer and referer.find("/documentation/") == -1:
                back_link = referer
        if back_link:
            context['back_link'] = back_link

        return context


class TechDocView(TemplateView):
    template_name = 'documentation/tech.html'

    def get_context_data(self, **kwargs):
        if 'name' in kwargs:
            self.docname = kwargs['name']
            name = self.docname
        context = super(TechDocView, self).get_context_data(**kwargs)
        context['docmenuitems'] = documentation_menu_items
        overview_urls = {'bibos': 'BibOS Desktop', 'admin': 'BibOS Admin'}

        overview_items = {
            'admin': [
                ('tech/install_guide', 'Installationsvejledning'),
                ('tech/developer_guide', 'Udviklerdokumentation'),
                ('tech/release_notes', 'Release notes'),
            ],
            'bibos': [
                ('tech/create_bibos_image', 'Lav nyt BibOS-image'),
                ('tech/save_harddisk_image',
                 'Gem harddisk-image med Clonezilla'),
                ('tech/build_bibos_cd', 'Byg BibOS-CD fra Clonezilla-image'),
                ('tech/image_release_notes', 'Release notes'),
            ]
        }

        def get_category(name):
            c = None
            for k in overview_items:
                if 'tech/' + name in [a for a, b in overview_items[k]]:
                    c = k
                    break
            return c

        dir = settings.SOURCE_DIR
        image_dir = settings.BIBOS_IMAGE_DIR

        def d(f):
            return os.path.join(dir, f)

        def i(f):
            return os.path.join(image_dir, f)

        url_mapping = {
            'install_guide': d('doc/HOWTO_INSTALL_SERVER.txt'),
            'developer_guide': d('doc/DEVELOPMENT_HOWTO.txt'),
            'release_notes': d('NEWS'),
            'create_bibos_image': i(
                'doc/HOWTOCreate_a_new_BibOS_image_from_scratch.txt'
            ),
            'save_harddisk_image': i(
                'doc/HOWTO_save_a_bibos_harddisk_image.txt'
            ),
            'build_bibos_cd': i(
                'doc/HOWTOBuild_BibOS_CD_from_clonezilla_image.txt'
            ),
            'image_release_notes': i('NEWS'),
        }

        if name in overview_urls:
            category = name
        elif name in url_mapping:
            # Get category of this document
            category = get_category(name)
            # Mark document as active
            context['doc_active'] = 'tech/' + name
            # Now supply file contents
            filename = url_mapping[name]
            with open(filename, "r") as f:
                context['tech_content'] = f.read()
        else:
            raise Http404

        # Supply info from category
        context['doc_title'] = overview_urls[category]
        context['menu_active'] = 'tech/' + category
        context['url_list'] = overview_items[category]

        return context

class JSONSiteSummary(JSONResponseMixin, SiteView):
    """Produce a JSON document summarising the state of all of the computers in
    a site."""

    interesting_properties = [
        'id', 'name', 'description', 'distribution_id', 'configuration_id',
        'package_list_id', 'custom_packages_id', 'site_id', 'is_active',
        'is_update_required', 'do_send_package_info', 'creation_time',
        'last_seen', 'location']

    def get_context_data(self, **kwargs):
        pcs = []
        for p in self.object.pcs.all():
            pc = {}
            for pn in JSONSiteSummary.interesting_properties:
                pv = getattr(p, pn)
                # Don't convert these types to string representations...
                if pv == None \
                        or isinstance(pv, bool) \
                        or isinstance(pv, float) \
                        or isinstance(pv, int):
                    pass
                # ... use the right date format for datetimes...
                elif isinstance(pv, datetime):
                    pv = pv.isoformat()
                # ... and use simple string representations for everything else
                else:
                    pv = str(pv)
                pc[pn] = pv
            pcs.append(pc)
        return pcs
