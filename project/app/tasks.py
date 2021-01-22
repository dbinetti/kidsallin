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


# Auth0
def get_auth0_token():
    get_token = GetToken(settings.AUTH0_DOMAIN)
    token = get_token.client_credentials(
        settings.AUTH0_CLIENT_ID,
        settings.AUTH0_CLIENT_SECRET,
        f'https://{settings.AUTH0_DOMAIN}/api/v2/',
    )
    return token

def get_auth0_client():
    token = get_auth0_token()
    client = Auth0(
        settings.AUTH0_DOMAIN,
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
        f'https://{settings.AUTH0_DOMAIN}/api/v2/{endpoint}',
        headers=headers,
        json=payload,
    )
    return response

@job
def update_user(user):
    data = get_user_data(user.username)
    user.data = data
    user.name = data.get('name', '')
    user.first_name = data.get('given_name', '')
    user.last_name = data.get('family_name', '')
    user.email = data.get('email', None)
    user.phone = data.get('phone_number', None)
    user.save()
    return user


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
def send_confirmation(parent):
    email = build_email(
        template='app/emails/confirmation.txt',
        subject='Kids All In Confirmation',
        from_email='Kids All In <support@kidsallin.com>',
        context={'parent': parent},
        to=[parent.email],
    )
    return email.send()

@job
def delete_user(user_id):
    client = get_auth0_client()
    response = client.users.delete(user_id)
    return response


def schools_list(filename='publics.csv'):
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
            status_map = {
                'Active': 10,
                'Closed': 20,
                'Merged': 30,
            }
            funding_map = {
                'Directly funded': 10,
                'Locally funded': 20,
                'Disallowed': 30,
            }
            status_key = str(row[3]) if row[3] != 'No Data' else None
            cd_status = status_map.get(status_key, None)
            if cd_status != 10:
                continue
            name = str(row[6]) if row[6] != 'No Data' else ''
            if not name:
                continue
            try:
                charter_number = int(row[25]) if row[25] != 'No Data' else None
            except ValueError:
                charter_number = None
            school = {
                'name': name,
                'cd_status': cd_status,
                'cd_id': int(row[0][-7:]) if row[0] != 'No Data' else None,
                'nces_district_id': int(row[1]) if row[1] != 'No Data' else None,
                'nces_school_id': int(row[2]) if row[2] != 'No Data' else None,
                'district_name': str(row[5]) if row[5] != 'No Data' else '',
                'county': str(row[4]) if row[4] != 'No Data' else '',
                'address': str(row[8]) if row[8] != 'No Data' else '',
                'city': str(row[9]) if row[9] != 'No Data' else '',
                'state': str(row[11]) if row[11] != 'No Data' else '',
                'zipcode': str(row[10]) if row[10] != 'No Data' else '',
                'phone': str(row[17]) if row[17] != 'No Data' else '',
                'website': str(row[21].replace(" ", "")) if row[21] != 'No Data' else '',
                # 'soc': int(row[29]) if row[29] != 'No Data' else None,

                'is_charter': True if row[24]=='Y' else False,
                'charter_number': charter_number,
                'funding_type': funding_map[str(row[26])] if row[26] != 'No Data' else None,
                # 'edops_type': getattr(School.EDOPS, str(row[31].strip().lower()), None),
                # 'eil': getattr(School.EIL, str(row[33].strip().lower()), None),
                'grade_span': str(row[35]) if row[35] != 'No Data' else '',
                # 'virtual_type': getattr(School.VIRTUAL, str(row[37].strip().lower()), None),
                'is_magnet': True if row[38]=='Y' else False,
                'fed_nces_school_id': int(row[40]) if row[40] != 'No Data' else None,

                'latitude': float(row[41]) if row[41] != 'No Data' else None,
                'longitude': float(row[42]) if row[42] != 'No Data' else None,
                'admin_first_name': str(row[43]) if row[43] != 'No Data' else '',
                'admin_last_name': str(row[44]) if row[44] != 'No Data' else '',
                'admin_email': str(row[45].replace(
                    ' ', ''
                ).replace(
                    'ndenson@compton.k12.ca.u', 'ndenson@compton.k12.ca.us'
                ).replace(
                    'bmcconnell@compton.k12.ca.u', 'bmcconnell@compton.k12.ca.us'
                )) if row[45] not in [
                    'Information Not Available',
                    'No Data',
                ] else '',
            }
            # form = SchoolForm(school)
            # if not form.is_valid():
            #     errors.append((row, form))
            #     break
            output.append(school)
        if not errors:
            return output
        else:
            print('Error!')
            return errors
