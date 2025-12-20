from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from users.forms import (
    AssignRoleForm,
    CustomRegistrationForm,
    LoginForm,
    CreateGroupForm,
)
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User, Group

# from django.contrib.auth.forms import AuthenticationForm


# Create your views here.
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


def sign_out(request):
    if request.method == "POST":
        logout(request)
        return redirect("sign-in")
    else:
        return redirect("home")


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


def admin_dashboard(request):
    users = User.objects.all()
    return render(request, "admin/dashboard.html", {"users": users})


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


def group_list(request):
    groups = Group.objects.all()
    return render(request, "admin/group-list.html", {"groups": groups})
