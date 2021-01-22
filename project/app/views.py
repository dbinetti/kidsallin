import csv

import requests
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


# Root
def index(request):
    if request.user.is_authenticated:
        return redirect('account')
    return render(
        request,
        'app/pages/index.html',
    )

# Authentication
def login(request):
    # Set landing page depending on initial button
    initial = request.GET.get('initial', 'None')
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    state = f"{initial}|{get_random_string()}"
    request.session['state'] = state

    params = {
        'response_type': 'code',
        'client_id': settings.AUTH0_CLIENT_ID,
        'scope': 'openid profile email',
        'redirect_uri': redirect_uri,
        'state': state,
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

    # get initial
    initial = browser_state.partition("|")[0]

    # Get Auth0 Code
    code = request.GET.get('code', None)
    if not code:
        return HttpResponse(status=400)
    token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'code': code,
        'grant_type': 'authorization_code'
    }
    token = requests.post(
        token_url,
        json=token_payload,
    ).json()
    access_token = token['access_token']
    user_url = f'https://{settings.AUTH0_DOMAIN}/userinfo?access_token={access_token}'
    payload = requests.get(user_url).json()
    # format payload key
    payload['username'] = payload.pop('sub')
    user = authenticate(request, **payload)
    if user:
        log_in(request, user)
        if initial == 'recipient':
            return redirect('recipient-create')
        if initial == 'volunteer':
            return redirect('volunteer-create')
        if user.is_admin:
            return redirect('admin:index')
        recipient = getattr(user, 'recipient', None)
        volunteer = getattr(user, 'volunteer', None)
        if recipient and volunteer:
            return redirect('account')
        if recipient:
            return redirect('recipient')
        if volunteer:
            return redirect('volunteer')
        return redirect('account')
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

#Account
@login_required
def account(request):
    user = request.user
    parent = getattr(user, 'parent', None)
    return render(
        request,
        'app/pages/account.html',
        context={
            'user': user,
            'parent': parent,
        }
    )

@login_required
def account_delete(request):
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
        'app/pages/account_delete.html',
        {'form': form,},
    )

# # Parent
# @login_required
# def parent(request):
#     try:
#         recipient = request.user.recipient
#     except AttributeError:
#         return redirect('recipient-create')
#     assignments = getattr(recipient, 'assignments', None)
#     return render(
#         request,
#         'app/pages/recipient.html',
#         context={
#             'recipient': recipient,
#             'assignments': assignments,
#         }
#     )

# @login_required
# def recipient_create(request):
#     recipient = getattr(request.user, 'recipient', None)
#     if recipient:
#         return redirect('recipient')

#     initial = {
#         'name': request.user.name,
#         'email': request.user.email,
#     }
#     form = RecipientForm(request.POST) if request.POST else RecipientForm(initial=initial)

#     if form.is_valid():
#         recipient = form.save(commit=False)
#         recipient.user = request.user
#         recipient.save()
#         send_recipient_confirmation.delay(recipient)
#         messages.success(
#             request,
#             "Registration complete!  We will reach out before November 8th with futher details.",
#         )
#         return redirect('recipient')
#     return render(
#         request,
#         'app/pages/recipient_create.html',
#         context={
#             'form': form,
#         }
#     )

# @login_required
# def recipient_update(request):
#     recipient = getattr(request.user, 'recipient', None)
#     if not recipient:
#         return redirect('recipient-create')
#     form = RecipientForm(request.POST, instance=recipient) if request.POST else RecipientForm(instance=recipient)
#     if form.is_valid():
#         form.save()
#         messages.success(
#             request,
#             "Recipient information updated!",
#         )
#         return redirect('recipient')
#     return render(
#         request,
#         'app/pages/recipient_update.html',
#         context={
#             'form': form,
#         }
#     )

# @login_required
# def recipient_delete(request):
#     if request.method == "POST":
#         form = DeleteForm(request.POST)
#         if form.is_valid():
#             recipient = getattr(request.user, 'recipient', None)
#             if recipient:
#                 recipient.delete()
#             messages.error(
#                 request,
#                 "Removed!",
#             )
#             return redirect('account')
#     else:
#         form = DeleteForm()
#     return render(
#         request,
#         'app/pages/recipient_delete.html',
#         {'form': form,},
#     )
