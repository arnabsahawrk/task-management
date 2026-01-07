from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from users.forms import (
    AssignRoleForm,
    CustomPasswordChangeForm,
    CustomPasswordResetConfirmForm,
    CustomPasswordResetForm,
    CustomRegistrationForm,
    EditUserProfileForm,
    LoginForm,
    CreateGroupForm,
)
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.views.generic import (
    TemplateView,
    UpdateView,
    CreateView,
    FormView,
    ListView,
)
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from django.contrib.auth import get_user_model

from users.models import CustomUser

User = get_user_model()


def is_admin(user):
    if not user.is_authenticated:
        return False

    return user.groups.filter(name="Admin").exists()


class SignUpView(CreateView):
    form_class = CustomRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("sign-in")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get("password"))
        user.is_active = False
        user.save()
        messages.success(
            self.request, "A activation mail has sent. Please check your mail."
        )
        return redirect(self.get_success_url())


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        return next_url or super().get_success_url()


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password-change.html"
    form_class = CustomPasswordChangeForm


@method_decorator(
    user_passes_test(is_admin, login_url="no-permission"), name="dispatch"
)
class AssignRoleView(FormView):
    form_class = AssignRoleForm
    template_name = "admin/assign-role.html"
    success_url = reverse_lazy("admin-dashboard")

    def form_valid(self, form):
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, id=user_id)
        role = form.cleaned_data["role"]
        user.groups.clear()
        user.groups.add(role)
        messages.success(
            self.request,
            f"User {user.username} has been assigned to the {role.name} role",
        )
        return super().form_valid(form)


@method_decorator(
    user_passes_test(is_admin, login_url="no-permission"), name="dispatch"
)
class CreateGroupView(CreateView):
    form_class = CreateGroupForm
    template_name = "admin/create-group.html"
    success_url = reverse_lazy("create-group")

    def form_valid(self, form):
        group = form.save()
        messages.success(
            self.request, f"Group {group.name} has been created successfully"
        )
        return redirect(self.get_success_url())


@method_decorator(
    user_passes_test(is_admin, login_url="no-permission"), name="dispatch"
)
class GroupListView(ListView):
    model = Group
    template_name = "admin/group-list.html"
    context_object_name = "groups"
    queryset = Group.objects.prefetch_related("permissions").all()


class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user

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


class EditProfileView(UpdateView):
    model = CustomUser
    form_class = EditUserProfileForm
    template_name = "accounts/update_profile.html"
    context_object_name = "form"

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect("profile")


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
