import random

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import redirect

from tasks.forms import TaskDetailModelForm, TaskModelForm
from typing import cast
from tasks.models import Project, Task
from django.contrib.auth.decorators import (
    user_passes_test,
    login_required,
    permission_required,
)
from django.utils.decorators import method_decorator

from users.views import is_admin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.db.models import ProtectedError


def is_manager(user):
    if not user.is_authenticated:
        return False

    return user.groups.filter(name="Manager").exists()


def is_employee(user):
    if not user.is_authenticated:
        return False

    return user.groups.filter(name="Employee").exists()


manager_dashboard_decorators = [
    login_required,
    user_passes_test(is_manager, login_url="no-permission"),
]


@method_decorator(manager_dashboard_decorators, name="dispatch")
class ManagerDashboardView(ListView):
    template_name = "dashboard/manager-dashboard.html"
    model = Task
    context_object_name = "tasks"

    def get_queryset(self):
        task_type = self.request.GET.get("type")
        base_query = Task.objects.select_related("detail").prefetch_related(
            "assigned_to"
        )

        if task_type == "completed":
            return base_query.filter(status="COMPLETED")
        elif task_type == "pending":
            return base_query.filter(status="PENDING")
        elif type == "in-progress":
            return base_query.filter(status="IN_PROGRESS")
        return base_query.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["counts"] = Task.objects.aggregate(
            total_tasks=Count("id"),
            pending_task=Count("id", filter=Q(status="PENDING")),
            completed_tasks=Count("id", filter=Q(status="COMPLETED")),
            in_progress_tasks=Count("id", filter=Q(status="IN_PROGRESS")),
        )
        return context


employee_dashboard_decorators = [
    user_passes_test(is_employee, login_url="no-permission"),
]


@method_decorator(employee_dashboard_decorators, name="dispatch")
class EmployeeDashboardView(ListView):
    model = Task
    template_name = "dashboard/employee-dashboard.html"
    context_object_name = "tasks"


class CreateTaskCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """CreateView-based implementation for creating a Task with its Detail."""

    permission_required = "tasks.add_task"
    login_url = "sign-in"
    model = Task
    form_class = TaskModelForm
    template_name = "task-form.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_form"] = self.get_form()
        context["task_detail_form"] = TaskDetailModelForm()
        return context

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save(commit=False)
            projects = Project.objects.all()
            task.project = random.choice(projects)
            task.save()

            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            return redirect("create-task")


update_decorators = [
    login_required,
    permission_required("tasks.change_task", raise_exception=True),
]


class UpdateTaskUpdateView(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = "task-form.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        context["task_form"] = self.get_form()
        context["task_detail_form"] = TaskDetailModelForm(
            instance=context["task"].detail
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)
        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=getattr(self.object, "detail", None)
        )

        if task_form.is_valid() and task_detail_form.is_valid():
            task_form.save()
            task_detail_form.save()

            messages.success(request, "Task Updated Successfully")
            return redirect("update-task", getattr(self.object, "id"))

        return redirect("update-task", getattr(self.object, "id"))


class DeleteTaskView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Task
    permission_required = "tasks.delete_task"
    success_url = reverse_lazy("manager-dashboard")

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, "Task Deleted Successfully")
            return response
        except ProtectedError:
            messages.error(request, "This task cannot be deleted.")
            return redirect(self.get_success_url())


class ViewTaskListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "tasks.view_task"
    login_url = "sign-in"

    model = Task
    template_name = "show-task.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return Task.objects.select_related("project").order_by("-created_at")


class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "tasks.view_task"
    login_url = "sign-in"
    model = Task
    template_name = "show-task-details.html"
    context_object_name = "task"
    pk_url_kwarg = "task_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Task.STATUS_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        task = cast(Task, self.get_object())
        selected_status = request.POST.get("task_status")
        task.status = selected_status
        task.save()
        return redirect("task-details", getattr(task, "id"))


@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect("manager-dashboard")
    elif is_employee(request.user):
        return redirect("user-dashboard")
    elif is_admin(request.user):
        return redirect("admin-dashboard")

    return redirect("no-permission")
