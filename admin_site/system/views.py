import json
import datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template import Context

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View, ListView, DetailView, RedirectView

from django.db.models import Q

from account.models import UserProfile

from models import Site, PC, PCGroup, ConfigurationEntry, Package
from forms import SiteForm, GroupForm, ConfigurationEntryForm, ScriptForm
from forms import UserForm, ParameterForm, PCForm
from job.models import Job, Script, Input, Batch, Parameter

import signals


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
        if selected is not None:
            context['selected_{0}'.format(display_name)] = selected
        context['{0}_list'.format(display_name)] = self.get_list()

        return context


class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content,
                            content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
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


class SiteDetailView(SiteView):
    """Class for showing the overview that is displayed when entering a site"""

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        # For now, show only not-yet-activated PCs
        context['pcs'] = self.object.pcs.all()
        context['pcs'] = [pc for pc in context['pcs'] if pc.status.state != '']

        query = {
            'batch__site': context['site'],
            'status': Job.FAILED
        }
        params = self.request.GET or self.request.POST

        orderby = params.get('orderby', '-pk')
        if not orderby in JobSearch.VALID_ORDER_BY:
            orderby = '-pk'
        context['orderby'] = orderby

        if orderby.startswith('-'):
            context['orderby_key'] = orderby[1:]
            context['orderby_direction'] = 'desc'
        else:
            context['orderby_key'] = orderby
            context['orderby_direction'] = 'asc'

        context['orderby_base_url'] = context['site'].get_absolute_url() + '?'

        jobs = JobSearch.get_jobs_display_data(
            Job.objects.filter(**query).order_by(orderby, 'pk')
        )
        if len(jobs) > 0:
            context['jobs'] = jobs

        context['pcs'] = sorted(context['pcs'], key=lambda s: s.name.lower())

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
        result = self.get(request, *args, **kwargs)

        # Handle saving of data
        self.object.configuration.update_from_request(
            request.POST, 'site_configs'
        )
        return result


# Now follows all site-based views, i.e. subclasses
# of SiteView.
class JobsView(SiteView):
    template_name = 'system/site_jobs.html'

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(JobsView, self).get_context_data(**kwargs)
        context['batches'] = self.object.batches.all()
        context['pcs'] = self.object.pcs.all()
        context['groups'] = self.object.groups.all()
        context['status_choices'] = [
            (name, value, Job.STATUS_TO_LABEL[value])
            for (value, name) in Job.STATUS_CHOICES
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
    def get_jobs_display_data(joblist):
        return [{
            'script_name': job.batch.script.name,
            'started': str(job.started) if job.started else None,
            'finished': str(job.finished) if job.started else None,
            'status': job.status,
            'label': job.status_label,
            'pc_name': job.pc.name,
            'batch_name': job.batch.name
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
        if not orderby in JobSearch.VALID_ORDER_BY:
            orderby = '-pk'

        context['job_list'] = Job.objects.filter(**query).order_by(
            orderby,
            'pk'
        )
        return context

    def convert_context_to_json(self, context):
        result = JobSearch.get_jobs_display_data(context['job_list'])
        return json.dumps(result)


class ScriptMixin(object):
    script = None
    script_inputs = None

    def setup_script_editing(self, **kwargs):
        # Get site
        self.site = get_object_or_404(Site, uid=kwargs['slug'])
        # Add the global and local script lists
        self.scripts = Script.objects.filter(
            Q(site=self.site) | Q(site=None)
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

        # If we selected a script add it to context
        if self.script is not None:
            context['selected_script'] = self.script
            if self.script.site is None:
                context['global_selected'] = True
            if context['script_inputs'] is None:
                context['script_inputs'] = [{
                    'pk': input.pk,
                    'name': input.name,
                    'value_type': input.value_type
                } for input in self.script.inputs.all()]
        else:
            context['script_inputs'] = []

        context['script_inputs_json'] = json.dumps(context['script_inputs'])

        return context

    def validate_script_inputs(self):
        params = self.request.POST
        num_inputs = params.get('script-number-of-inputs', 0)
        inputs = []
        success = True
        if num_inputs > 0:
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


class ScriptCreate(ScriptMixin, CreateView):
    template_name = 'system/scripts/create.html'
    form_class = ScriptForm

    def get_context_data(self, **kwargs):
        context = super(ScriptCreate, self).get_context_data(**kwargs)
        context['type_choices'] = Input.VALUE_CHOICES
        return context

    def form_valid(self, form):
        if self.validate_script_inputs():
            self.object = form.save()
            self.script = self.object
            self.save_script_inputs()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form, transfer_inputs=False)

    def form_invalid(self, form, transfer_inputs=True):
        if transfer_inputs:
            self.validate_script_inputs()

        return super(ScriptCreate, self).form_invalid(form)

    def get_success_url(self):
        return '/site/%s/scripts/%s/' % (self.site.uid, self.script.pk)


class ScriptUpdate(ScriptMixin, UpdateView):
    template_name = 'system/scripts/update.html'
    form_class = ScriptForm

    def get_context_data(self, **kwargs):
        # Get context from super class
        context = super(ScriptUpdate, self).get_context_data(**kwargs)
        if self.script is not None and self.script.executable_code is not None:
            context['script_preview'] = self.script.executable_code.read()
        context['type_choices'] = Input.VALUE_CHOICES
        return context

    def get_object(self, queryset=None):
        return self.script

    def form_valid(self, form):
        if self.validate_script_inputs():
            self.save_script_inputs()
            return super(ScriptUpdate, self).form_valid(form)
        else:
            return self.form_invalid(form, transfer_inputs=False)

    def form_invalid(self, form, transfer_inputs=True):
        if transfer_inputs:
            self.validate_script_inputs()

        return super(ScriptUpdate, self).form_invalid(form)

    def get_success_url(self):
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
            context['message'] = _('Du skal angive mindst en PC eller gruppe')
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
            context['message'] = _('Du skal angive mindst en PC eller gruppe')
            self.step1(context)
            return

        if not form.is_valid():
            self.step2(context)
        else:
            # Create batch
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            batch = Batch(site=context['site'], script=context['script'],
                          name=' '.join([context['script'].name, now_str]))
            batch.save()
            context['batch'] = batch

            # Add parameters
            for i, inp in enumerate(
                context['script'].inputs.all().order_by('position')
            ):
                value = form.cleaned_data['parameter_%s' % i]
                if(inp.value_type == Input.FILE):
                    p = Parameter(input=inp, batch=batch, file_value=value)
                else:
                    p = Parameter(input=inp, batch=batch, string_value=value)
                p.save()

            # Create a job ofr each pc
            for pc_pk in pcs:
                job = Job(batch=batch, pc=PC.objects.get(pk=pc_pk))
                job.save()

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


class PCUpdate(SiteMixin, UpdateView):
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

        context['active_accordion'] = params.get('accordion', 'details')

        orderby = params.get('orderby', '-pk')
        if not orderby in JobSearch.VALID_ORDER_BY:
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

        context['orderby_base_url'] = ''.join([
            pc.get_absolute_url(),
            '?accordion=joblist&'
        ])

        context['selected_pc'] = pc

        return context

    def form_valid(self, form):
        self.object.custom_packages.update_by_package_names(
            self.request.POST.getlist('pc_packages_add'),
            self.request.POST.getlist('pc_packages_remove')
        )
        self.object.configuration.update_from_request(
            self.request.POST, 'pc_config'
        )
        return super(PCUpdate, self).form_valid(form)


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

    def get_context_data(self, **kwargs):
        # First, get basic context from superclass
        context = super(UsersView, self).get_context_data(**kwargs)
        # Add choices for UserProfile type
        choices = UserProfile.type_choices
        choices_dict = [{'id': k, 'val': v} for (k, v) in choices]
        context['choices'] = choices_dict

        return context


class UserCreate(CreateView, LoginRequiredMixin):
    model = User
    form_class = UserForm
    lookup_field = 'username'
    template_name = 'system/site_users.html'

    def get_context_data(self, **kwargs):
        context = super(UserCreate, self).get_context_data(**kwargs)
        # Add choices for UserProfile type
        choices = UserProfile.type_choices
        choices_dict = [{'id': k, 'val': v} for (k, v) in choices]
        context['choices'] = choices_dict
        # Add site
        site = get_object_or_404(Site, uid=self.kwargs['slug'])
        context['site'] = site

        return context

    def form_valid(self, form):
        site = get_object_or_404(Site, uid=self.kwargs['slug'])
        self.object = form.save()
        profile = self.object.bibos_profile.create(
            user=self.object,
            type=self.request.POST['type'],
            site=site
        )
        result = super(UserCreate, self).form_valid(form)
        return result

    def get_success_url(self):
        return '/site/{0}/users/'.format(self.kwargs['slug'])


class UserUpdate(UpdateView, LoginRequiredMixin):
    model = User
    form_class = UserForm
    lookup_field = 'username'


class SiteCreate(CreateView, LoginRequiredMixin):
    model = Site
    form_class = SiteForm
    slug_field = 'uid'

    def get_success_url(self):
        return '/sites/'


class SiteUpdate(UpdateView, LoginRequiredMixin):
    model = Site
    form_class = SiteForm
    slug_field = 'uid'

    def get_success_url(self):
        return '/sites/'


class SiteDelete(DeleteView, LoginRequiredMixin):
    model = Site
    slug_field = 'uid'

    def get_success_url(self):
        return '/sites/'


class ConfigurationEntryCreate(SiteMixin, CreateView, LoginRequiredMixin):
    model = ConfigurationEntry
    form_class = ConfigurationEntryForm

    def form_valid(self, form):
        site = get_object_or_404(Site, uid=self.kwargs['site_uid'])
        self.object = form.save(commit=False)
        self.object.owner_configuration = site.configuration

        return super(ConfigurationEntryCreate, self).form_valid(form)

    def get_success_url(self):
        return '/site/{0}/configuration/'.format(self.kwargs['site_uid'])


class ConfigurationEntryUpdate(SiteMixin, UpdateView, LoginRequiredMixin):
    model = ConfigurationEntry
    form_class = ConfigurationEntryForm

    def get_success_url(self):
        return '/site/{0}/configuration/'.format(self.kwargs['site_uid'])


class ConfigurationEntryDelete(SiteMixin, DeleteView, LoginRequiredMixin):
    model = ConfigurationEntry

    def get_success_url(self):
        return '/site/{0}/configuration/'.format(self.kwargs['site_uid'])


class GroupCreate(SiteMixin, CreateView, LoginRequiredMixin):
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


class GroupUpdate(SiteMixin, LoginRequiredMixin, UpdateView):
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

        pc_queryset = site.pcs.all()
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

        return context

    def form_valid(self, form):
        self.object.custom_packages.update_by_package_names(
            self.request.POST.getlist('group_packages_add'),
            self.request.POST.getlist('group_packages_remove')
        )
        self.object.configuration.update_from_request(
            self.request.POST, 'group_configuration'
        )
        return super(GroupUpdate, self).form_valid(form)

    def form_invalid(self, form):
        return super(GroupUpdate, self).form_invalid(form)


class GroupDelete(SiteMixin, LoginRequiredMixin, DeleteView):
    model = PCGroup

    def get_object(self, queryset=None):
        return PCGroup.objects.get(uid=self.kwargs['group_uid'])

    def get_success_url(self):
        return '/site/{0}/groups/'.format(self.kwargs['site_uid'])


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
