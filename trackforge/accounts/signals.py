from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_group_based_on_role(sender, instance, created, **kwargs):
    """Add new users to the group matching their role.

    If the role groups haven't been provisioned yet (i.e. `setup_groups`
    hasn't been run), we silently skip — the user is still created and
    can sign in; an admin can assign permissions later.
    """
    if not created:
        return
    role = getattr(instance, "role", None)
    if not role:
        return
    try:
        group = Group.objects.get(name=role)
    except Group.DoesNotExist:
        return
    instance.groups.add(group)
