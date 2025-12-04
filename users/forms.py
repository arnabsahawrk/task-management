from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
import re
from tasks.forms import StyledFormMixin


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
        model = User
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
