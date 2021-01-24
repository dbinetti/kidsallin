# Django
# Third-Party
import pytest
from django.urls import reverse


def test_deploy():
    assert True

@pytest.mark.django_db
def test_index(admin_client):
    path = reverse('admin:index')
    response = admin_client.get(path)
    assert response.status_code == 200

@pytest.mark.django_db
def test_parent(admin_client):
    path = reverse('admin:app_parent_changelist')
    response = admin_client.get(path)
    assert response.status_code == 200

@pytest.mark.django_db
def test_user(admin_client, user):
    path = reverse('admin:app_user_change', args=(user.id,))
    response = admin_client.get(path)
    assert response.status_code == 200
