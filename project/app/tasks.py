# Standard Libary
import csv

import requests
# First-Party
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
# Django
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.http import FileResponse
from django.template.loader import render_to_string
from django_rq import job

from .forms import SchoolForm
from .models import Account


# Auth0
def get_auth0_token():
    get_token = GetToken(settings.AUTH0_TENANT)
    token = get_token.client_credentials(
        settings.AUTH0_CLIENT_ID,
        settings.AUTH0_CLIENT_SECRET,
        f'https://{settings.AUTH0_TENANT}/api/v2/',
    )
    return token

def get_auth0_client():
    token = get_auth0_token()
    client = Auth0(
        settings.AUTH0_TENANT,
        token['access_token'],
    )
    return client

def get_user_data(user_id):
    client = get_auth0_client()
    data = client.users.get(user_id)
    return data

def put_auth0_payload(endpoint, payload):
    token = get_auth0_token()
    access_token = token['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.put(
        f'https://{settings.AUTH0_TENANT}/api/v2/{endpoint}',
        headers=headers,
        json=payload,
    )
    return response

@job
def update_user(user):
    data = get_user_data(user.username)
    user.data = data
    user.name = data.get('name', '')
    user.picture = data.get('picture', '')
    user.first_name = data.get('given_name', '')
    user.last_name = data.get('family_name', '')
    user.email = data.get('email', None)
    user.phone = data.get('phone_number', None)
    user.save()
    return user


@job
def delete_user(user_id):
    client = get_auth0_client()
    response = client.users.delete(user_id)
    return response

# User
def create_account(user):
    account = Account.objects.create(
        user=user,
        name=user.name,
        email=user.email,
    )
    return account


# Utility
def build_email(template, subject, from_email, context=None, to=[], cc=[], bcc=[], attachments=[], html_content=None):
    body = render_to_string(template, context)
    if html_content:
        html_rendered = render_to_string(html_content, context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
        cc=cc,
        bcc=bcc,
    )
    if html_content:
        email.attach_alternative(html_rendered, "text/html")
    for attachment in attachments:
        with attachment[1].open() as f:
            email.attach(attachment[0], f.read(), attachment[2])
    return email

@job
def send_email(email):
    return email.send()


@job
def send_confirmation(user):
    email = build_email(
        template='app/emails/confirmation.txt',
        subject='Welcome to Kids All In!',
        from_email='David Binetti <dbinetti@kidsallin.com>',
        context={'user': user},
        to=[user.email],
    )
    return email.send()

def schools_list(filename='ada.csv'):
    with open(filename) as f:
        reader = csv.reader(
            f,
            skipinitialspace=True,
        )
        next(reader)
        rows = [row for row in reader]
        t = len(rows)
        i = 0
        errors = []
        output = []
        for row in rows:
            i += 1
            print(f"{i}/{t}")
            school = {
                'name': str(row[0]).strip().title(),
                'nces_school_id': int(row[1]),
                'phone': str(row[7]),
                # 'website': str(row[21].replace(" ", "")) if row[21] != 'No Data' else '',
                'is_charter': True if row[9]=='1-Yes' else False,
                'is_magnet': True if row[10]=='1-Yes' else False,
                'latitude': float(row[12]),
                'longitude': float(row[13]),
            }
            form = SchoolForm(school)
            if not form.is_valid():
                errors.append((row, form))
            output.append(school)
        if not errors:
            return output
        else:
            print('Error!')
            return errors
