"""Replace the existing user class with our own in the admin."""
from django import forms  # type: ignore
from django.contrib import admin  # type: ignore
from django.contrib.auth import admin as auth_admin  # type: ignore
from django.contrib.auth import forms as auth_forms  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.contrib.auth import password_validation  # type: ignore
from django.utils.translation import ugettext_lazy as _  # type: ignore


class UserChangeForm(auth_forms.UserChangeForm):
    """Form for modifying users in admin."""

    class Meta(auth_forms.UserChangeForm.Meta):
        """Supply the meta parameters."""

        model = get_user_model()
        fields = "__all__"


class UserCreationForm(auth_forms.UserCreationForm):
    """Form to create a user with no privileges from an email and password."""

    error_messages = {
        "password_mismatch": _(""),
        "duplicate_email": _("A user with that email already exists"),
    }

    class Meta:
        """Supply the meta parameters."""

        model = get_user_model()
        fields = ["email"]

    def clean_password2(self):
        """Ensure the passwords match."""
        pass1 = self.cleaned_data.get("password1")
        pass2 = self.cleaned_data.get("password2")
        if pass1 and pass2 and pass1 != pass2:
            raise forms.ValidationError(
                "The two password fields didn't match.", code="password_mismatch"
            )
        if password_validation is not None:
            password_validation.validate_password(pass1, self.instance)
        return pass1


_fieldsets = {
    None: ["email", "password"],
    _("Permissions"): [
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
    ],
    _("Important dates"): ["date_joined", "last_login"],
}
_add_fieldsets = {"classes": ["wide"], "fields": ["email", "password1", "password2"]}


@admin.register(get_user_model())
class UserAdmin(auth_admin.UserAdmin):
    """The admin interface for the user model."""

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = [(k, {"fields": v}) for k, v in _fieldsets.items()]
    add_fieldsets = [(None, _add_fieldsets)]
    list_display = [
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    ]
    list_filter = ["is_staff", "is_superuser", "is_active", "groups"]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = ["groups", "user_permissions"]
    readonly_fields = ["date_joined"]
