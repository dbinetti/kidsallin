import csv

import jwt
import requests
from auth0.v3.authentication.users import Users
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string

from .forms import DeleteForm
from .forms import ParentForm


# Root
def index(request):
    if request.user.is_authenticated:
        return redirect('parent')
    return render(
        request,
        'app/pages/index.html',
    )

# Authentication
def login(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    state = f"{get_random_string()}"
    request.session['state'] = state
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'redirect_uri': redirect_uri,
        'screen_hint': 'signup',
    }
    url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/authorize',
        params=params,
    ).prepare().url
    return redirect(url)

def callback(request):
    # Reject if state doesn't match
    browser_state = request.session.get('state')
    server_state = request.GET.get('state')
    if browser_state != server_state:
        return HttpResponse(status=400)

    # Get Auth0 Code
    code = request.GET.get('code', None)
    if not code:
        return HttpResponse(status=400)
    token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }
    token = requests.post(
        token_url,
        json=token_payload,
    ).json()
    payload = jwt.decode(
        token['id_token'],
        options={
            'verify_signature': False,
        }
    )
    payload['username'] = payload.pop('sub')
    user = authenticate(request, **payload)
    if user:
        log_in(request, user)
        return redirect('parent')
    return HttpResponse(status=403)

def logout(request):
    log_out(request)
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'return_to': request.build_absolute_uri(reverse('index')),
    }
    logout_url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/v2/logout',
        params=params,
    ).prepare().url
    messages.success(
        request,
        "You Have Been Logged Out!",
    )
    return redirect(logout_url)

# Parent
@login_required
def parent(request):
    parent = request.user.parent
    if request.POST:
        form = ParentForm(request.POST, instance=parent)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Updated!",
            )
            return redirect('parent')
    else:
        form = ParentForm(instance=parent)
    return render(
        request,
        'app/pages/parent.html',
        context={
            'form': form,
        }
    )


# Delete
@login_required
def delete(request):
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            user = request.user
            user.delete()
            messages.error(
                request,
                "Account Deleted!",
            )
            return redirect('index')
    else:
        form = DeleteForm()
    return render(
        request,
        'app/pages/delete.html',
        {'form': form,},
    )
