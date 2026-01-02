from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from users.forms import (
    AssignRoleForm,
    CustomPasswordChangeForm,
    CustomPasswordResetConfirmForm,
    CustomPasswordResetForm,
    CustomRegistrationForm,
    LoginForm,
    CreateGroupForm,
)
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.views.generic import TemplateView
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse_lazy


def is_admin(user):
    if not user.is_authenticated:
        return False

    return user.groups.filter(name="Admin").exists()


def sign_up(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = CustomRegistrationForm()
    if request.method == "POST":
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            # username = form.cleaned_data.get("username")
            # password = form.cleaned_data.get("password1")
            # confirm_password = form.cleaned_data.get("password2")

            # if password == confirm_password:
            #     User.objects.create(username=username, password=password)

            user = form.save(commit=False)
            print("User", user)
            user.set_password(form.cleaned_data.get("password"))
            print(form.cleaned_data)
            user.is_active = False
            form.save()
            messages.success(
                request, "A activation mail has sent. Please check your mail."
            )
            return redirect("sign-in")
        else:
            print("Password are not same")

    return render(request, "registration/register.html", {"form": form})


def sign_in(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm()
    if request.method == "POST":

        """username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)"""

        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")

    return render(request, "registration/login.html", {"form": form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        return next_url or super().get_success_url()


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password-change.html"
    form_class = CustomPasswordChangeForm


@login_required
def sign_out(request):
    if request.method != "POST":
        return redirect("home")
    logout(request)
    return redirect("sign-in")


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect("sign-in")
        else:
            return HttpResponse("Invalid Id or Token")
    except User.DoesNotExist:
        return HttpResponse("User not found")


@user_passes_test(is_admin, login_url="no-permission")
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch("groups", queryset=Group.objects.all(), to_attr="all_groups")
    ).all()

    user_data = [
        {
            "user": user,
            "group_name": (
                user.all_groups[0].name if user.all_groups else "No Groups Assigned"  # type: ignore
            ),
        }
        for user in users
    ]

    return render(request, "admin/dashboard.html", {"users": user_data})


@user_passes_test(is_admin, login_url="no-permission")
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]
            user.groups.clear()
            user.groups.add(role)

            messages.success(
                request,
                f"User {user.username} has been assigned to the {role.name} role",
            )
            return redirect("admin-dashboard")

    else:
        form = AssignRoleForm()

    return render(request, "admin/assign-role.html", {"form": form})


@user_passes_test(is_admin, login_url="no-permission")
def create_group(request):
    if request.method == "POST":
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(
                request, f"Group {group.name} has been created successfully"
            )
            return redirect("create-group")
    else:
        form = CreateGroupForm()

    return render(request, "admin/create-group.html", {"form": form})


@user_passes_test(is_admin, login_url="no-permission")
def group_list(request):
    groups = Group.objects.prefetch_related("permissions").all()
    return render(request, "admin/group-list.html", {"groups": groups})


class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["username"] = user.username
        context["email"] = getattr(user, "email", "")
        context["name"] = (
            user.get_full_name() if not isinstance(user, AnonymousUser) else ""
        )
        context["since"] = getattr(user, "date_joined", "")
        context["last"] = getattr(user, "last_login", "")
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "registration/reset-password.html"
    success_url = reverse_lazy("sign-in")
    html_email_template_name = "registration/reset-email.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["protocol"] = "https" if self.request.is_secure() else "http"
        context["domain"] = self.request.get_host()
        return context

    def form_valid(self, form):
        messages.success(self.request, "A reset email sent. Please check your email.")
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = "registration/reset-password.html"
    success_url = reverse_lazy("sign-in")

    def form_valid(self, form):
        messages.success(self.request, "Password reset successfully.")
        return super().form_valid(form)
