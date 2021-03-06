"""Replace the existing user class with our own in the admin."""
import django.contrib.auth.admin
import django.contrib.auth.forms
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _


class UserChangeForm(django.contrib.auth.forms.UserChangeForm):
    """Form for modifying users in admin."""

    class Meta(django.contrib.auth.forms.UserChangeForm.Meta):
        """Supply the meta parameters."""

        model = get_user_model()
        fields = "__all__"


class UserCreationForm(django.contrib.auth.forms.UserCreationForm):
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
class UserAdmin(django.contrib.auth.admin.UserAdmin):
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
