# Django
from django.urls import path
from django.views.generic import TemplateView

# Local
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='index',),

    # Footer
    path('about/', TemplateView.as_view(template_name='app/pages/about.html'), name='about',),
    path('privacy/', TemplateView.as_view(template_name='app/pages/privacy.html'), name='privacy',),
    path('terms/', TemplateView.as_view(template_name='app/pages/terms.html'), name='terms',),
    path('support/', TemplateView.as_view(template_name='app/pages/support.html'), name='support',),

    # Authentication
    path('login', views.login, name='login'),
    path('callback', views.callback, name='callback'),
    path('logout', views.logout, name='logout'),

    # Accounts
    path('account', views.account, name='account',),
    path('account/delete', views.account_delete, name='account-delete',),

    # Parent
    # path('parent', views.parent, name='parent',),
    # path('parent/create', views.parent_create, name='parent-create',),
    # path('parent/update', views.parent_update, name='parent-update',),
    # path('parent/delete', views.parent_delete, name='parent-delete',),
]
