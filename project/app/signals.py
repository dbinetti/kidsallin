from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import User
from .tasks import create_account
from .tasks import delete_user
from .tasks import send_confirmation

# from .tasks import update_user


@receiver(pre_delete, sender=User)
def delete_auth0(sender, instance, **kwargs):
    delete_user(instance.username)

# @receiver(user_logged_in, sender=User)
# def update_auth0(request, user, **kwargs):
#     update_user.delay(user)

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        create_account(instance)
        send_confirmation.delay(instance)
