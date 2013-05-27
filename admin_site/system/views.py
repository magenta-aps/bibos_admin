# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from account.models import UserProfile


@login_required
def index(request):
    user = request.user
    profile = user.get_profile()

    if profile.type == UserProfile.SUPER_ADMIN:
        # Redirect to list of sites
        return redirect('sites/')
    else:
        # User belongs to one site only; redirect to that site
        return HttpResponse('To be specified!')


@login_required
def sites_overview(request):
    return render(request, 'system/sites.html')
