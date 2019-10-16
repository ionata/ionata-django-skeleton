"""Project wide tests."""
# pylint: disable=invalid-name
from typing import List

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import testcases


class SetupSkeletonTestCase(testcases.TestCase):
    """Test the setup_skeletons management command."""

    def test_groups_are_created(self):
        """Test groups are created."""
        call_command("setup_skeletons", verbosity=0)
        for group_info in settings.AUTH_GROUPS:
            group = (
                Group.objects.filter(name=group_info["name"])
                .prefetch_related("permissions")
                .first()
            )
            # ensure the Group is not None
            self.assertIsNotNone(
                group, msg=f"The Group named `{group_info['name']}` does not exist."
            )
            permissions: List[Permission] = []
            for perm in group_info["permissions"]:
                app_label, codename = perm.split(".")
                permission = Permission.objects.filter(
                    content_type__app_label=app_label, codename=codename
                ).first()
                # ensure the Permission is not None
                self.assertIsNotNone(
                    permission,
                    msg=f"The Permission named `{codename}` does not exist "
                    f"for the `{app_label}` app.",
                )
                permissions.append(permission)
            # ensure all the permissions are in the group's permissions
            self.assertCountEqual(permissions, group.permissions.all())
