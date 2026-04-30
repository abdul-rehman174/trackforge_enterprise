from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

# Apps whose permissions we manage. Other apps (admin, contenttypes, sessions,
# auth.Permission, auth.Group) are intentionally left to the superuser only.
MANAGED_APPS = ("inventory", "procurement", "accounts")

# Per-role action sets. "all" means every action across MANAGED_APPS.
ROLE_ACTIONS = {
    "admin":   ["add", "change", "delete", "view"],
    "manager": ["add", "change", "view"],
    "staff":   ["add", "change", "view"],
    "user":    ["view"],
}

# Per-role app restrictions. None means all MANAGED_APPS.
ROLE_APPS = {
    "admin":   None,
    "manager": None,
    "staff":   ("inventory", "procurement"),
    "user":    None,
}


class Command(BaseCommand):
    help = "Create / refresh the admin, manager, staff and user role groups with the right permissions."

    def handle(self, *args, **options):
        for role, actions in ROLE_ACTIONS.items():
            group, created = Group.objects.get_or_create(name=role)
            apps = ROLE_APPS.get(role) or MANAGED_APPS

            perms = Permission.objects.filter(
                content_type__app_label__in=apps,
                codename__regex=r"^(" + "|".join(actions) + ")_",
            )

            group.permissions.set(perms)

            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(
                f"  {verb:8s} '{role}' group with {perms.count()} permissions across {list(apps)}"
            ))

        self.stdout.write(self.style.SUCCESS("\nDone. New users will pick up their role group's perms via the post_save signal."))
        self.stdout.write("To re-sync existing users, ask them to be re-saved or run: ")
        self.stdout.write("  python manage.py shell -c \"from accounts.models import CustomUser; [u.save() for u in CustomUser.objects.all()]\"")
