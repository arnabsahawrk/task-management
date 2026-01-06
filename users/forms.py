from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from django import forms
import re
from tasks.forms import StyledFormMixin
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth import get_user_model

from users.models import CustomUser

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].help_text = ""


class CustomRegistrationForm(StyledFormMixin, forms.ModelForm):
    password = forms.CharField()
    confirm_password = forms.CharField()

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
        ]

    def clean_password(self):  # field error
        password = self.cleaned_data.get("password")
        errors = []

        if not password:
            raise forms.ValidationError("Password is required")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        if not re.search(r"[0-9]", password):
            errors.append("Password must contain at least one digit")

        if not re.search(r"[@#$%^&+=]", password):
            errors.append("Password must contain at least one special character")

        if errors:
            raise forms.ValidationError(errors)

        return password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        email_exits = User.objects.filter(email=email).exists()

        if email_exits:
            raise forms.ValidationError("Email already exits")

        return email

    def clean(self):  # non field error
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AssignRoleForm(StyledFormMixin, forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(), empty_label="Select a role"
    )


class CreateGroupForm(StyledFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Permission",
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]


class CustomPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass


class CustomPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass


class CustomPasswordResetConfirmForm(StyledFormMixin, SetPasswordForm):
    pass


"""
class EditUserProfileForm(StyledFormMixin, forms.ModelForm):
    bio = forms.CharField(required=False, widget=forms.Textarea, label="Bio")
    profile_image = forms.ImageField(required=False, label="Profile Image")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)

        if self.profile:
            self.fields["bio"].initial = self.profile.bio
            self.fields["profile_image"].initial = self.profile.profile_image

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()

        if self.profile:
            self.profile.bio = self.cleaned_data.get("bio")

            image = self.cleaned_data.get("profile_image")
            if image:
                self.profile.profile_image = image

            if commit:
                self.profile.save()

        return user
"""


class EditUserProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "bio", "profile_image"]
