import os

from allauth.account.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def elevate_instructor_on_login(request, user, **kwargs):  # noqa: ARG001
    instructor_username = os.environ.get('INSTRUCTOR_USERNAME', '')
    if not instructor_username or user.username != instructor_username:
        return
    from django.contrib.auth.models import Group
    changed = False
    if not user.is_staff:
        user.is_staff = True
        user.save(update_fields=['is_staff'])
        changed = True
    g = Group.objects.filter(pk=2).first()
    if g and not user.groups.filter(pk=2).exists():
        user.groups.add(g)
        changed = True
    if changed:
        import logging
        logging.getLogger(__name__).info("Elevated %s to instructor", user.username)
