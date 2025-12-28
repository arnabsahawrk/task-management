import random

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

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
from django.views.generic.base import ContextMixin
from django.views.generic import ListView, DetailView, UpdateView, CreateView


# create Based View reuse example
class Greetings(View):
    greetings = "Hello, Welcome to the Task Management System!"

    def get(self, request):
        return HttpResponse(self.greetings)


class HiGreetings(Greetings):
    greetings = "Hi, This is an extended Greeting from Task Management System!"


class HiHowGreetings(HiGreetings):
    greetings = (
        "Hi How are you? This is another extended Greeting from Task Management System!"
    )


def is_manager(user):
    if not user.is_authenticated:
        return False

    return user.groups.filter(name="Manager").exists()


def is_employee(user):
    if not user.is_authenticated:
        return False

    return user.groups.filter(name="Employee").exists()


@user_passes_test(is_manager, login_url="no-permission")
def manager_dashboard(request):

    # getting task count
    """total_tasks = tasks.count()
    pending_task = tasks.filter(status="PENDING").count()
    completed_tasks = tasks.filter(status="COMPLETED").count()
    in_progress_tasks = tasks.filter(status="IN_PROGRESS").count()"""

    counts = Task.objects.aggregate(
        total_tasks=Count("id"),
        pending_task=Count("id", filter=Q(status="PENDING")),
        completed_tasks=Count("id", filter=Q(status="COMPLETED")),
        in_progress_tasks=Count("id", filter=Q(status="IN_PROGRESS")),
    )

    type = request.GET.get("type")
    print(type)
    base_query = Task.objects.select_related("detail").prefetch_related("assigned_to")

    if type == "completed":
        tasks = base_query.filter(status="COMPLETED")
    elif type == "pending":
        tasks = base_query.filter(status="PENDING")
    elif type == "in-progress":
        tasks = base_query.filter(status="IN_PROGRESS")
    else:
        tasks = base_query.all()

    context = {"tasks": tasks, "counts": counts}

    return render(request, "dashboard/manager-dashboard.html", context)


@user_passes_test(is_employee, login_url="no-permission")
def employee_dashboard(request):
    return render(request, "dashboard/employee-dashboard.html")


@login_required
@permission_required("tasks.add_task", raise_exception=True)
def create_task(request):
    # Django From Data
    """employees = Employee.objects.all()
    form = TaskForm(employees=employees)

    if request.method == "POST":
        form = TaskForm(request.POST, employees=employees)
        if form.is_valid():
            # print(form.cleaned_data)
            data = form.cleaned_data
            title = data.get("title")
            description = data.get("description")
            due_date = data.get("due_date")
            assigned_to = data.get("assigned_to")

            task = Task.objects.create(
                title=title, description=description, due_date=due_date
            )

            # Assign employee to tasks
            if assigned_to:
                for emp_id in assigned_to:
                    employee = Employee.objects.get(id=emp_id)
                    task.assigned_to.add(employee)
                return HttpResponse("Task added successfully")"""

    # Django Model Form Data
    task_form = TaskModelForm()
    task_detail_form = TaskDetailModelForm()

    if request.method == "POST":
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

    context = {"task_form": task_form, "task_detail_form": task_detail_form}

    return render(request, "task-form.html", context=context)


"""# variable for list of decorators
create_decorators = [
    login_required,
    permission_required("tasks.add_task", raise_exception=True),
]


@method_decorator(
    create_decorators, name="dispatch"
)  # we're doing it on dispatch method because all request get/post will go through dispatch method"""


class CreateTaskView(ContextMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    """Class Based View Example for Create Task"""

    permission_required = "tasks.add_task"
    login_url = "sign-in"
    template_name = "task-form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_form"] = kwargs.get("task_form", TaskModelForm())
        context["task_detail_form"] = kwargs.get(
            "task_detail_form", TaskDetailModelForm()
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save(commit=False)
            task.save()

            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            context = self.get_context_data(
                task_form=task_form, task_detail_form=task_detail_form
            )
            return render(request, self.template_name, context=context)


# TODO
class CreateTaskCreateView(CreateView):
    pass


@login_required
@permission_required("tasks.change_task", raise_exception=True)
def update_task(request, id):
    task = Task.objects.get(id=id)

    task_form = TaskModelForm(instance=task)
    task_detail_form = TaskDetailModelForm(instance=task.detail)

    if request.method == "POST":
        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=task.detail
        )

        if task_form.is_valid() and task_detail_form.is_valid():

            task_form.save()
            task_detail_form.save()

            messages.success(request, "Task Updated Successfully")
            return redirect("update-task", id)

    context = {"task_form": task_form, "task_detail_form": task_detail_form}

    return render(request, "task-form.html", context=context)


update_decorators = [
    login_required,
    permission_required("tasks.change_task", raise_exception=True),
]


@method_decorator(update_decorators, name="dispatch")
class UpdateTaskView(View):
    template_name = "task-form.html"

    def get(self, request, *args, **kwargs):
        task = Task.objects.get(id=kwargs["id"])
        task_form = TaskModelForm(instance=task)
        task_detail_form = TaskDetailModelForm(instance=task.detail)

        context = {"task_form": task_form, "task_detail_form": task_detail_form}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        task = Task.objects.get(id=kwargs["id"])
        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=task.detail
        )

        if task_form.is_valid() and task_detail_form.is_valid():
            task_form.save()
            task_detail_form.save()

            messages.success(request, "Task Updated Successfully")
            return redirect("update-task", id=kwargs["id"])


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


@login_required
@permission_required("tasks.delete_task", raise_exception=True)
def delete_task(request, id):
    if request.method == "POST":
        task = Task.objects.get(id=id)
        task.delete()
        messages.success(request, "Task Deleted Successfully")
    else:
        messages.error(request, "Something went wrong")

    return redirect("manager-dashboard")


@login_required
@permission_required("tasks.view_task", raise_exception=True)
def view_task(request):
    # retrieve all data from database
    # tasks = Task.objects.all()

    # show the first data
    # task = Task.objects.first()

    # show the data id with 1
    # task = Task.objects.get(id=1)  // it raises error if the data doesn't exist and if there are multiple data

    # show the data that are in pending
    # tasks = Task.objects.filter(status="PENDING")

    # show the data which due_date is today
    # tasks = Task.objects.filter(due_date=date.today())

    # Show the tasks which priority is not low meaning only high and medium
    # tasks = TaskDetail.objects.exclude(priority="L")

    # show the tasks that contain word 'economic'
    # tasks = Task.objects.filter(title__icontains="economic")

    # show the tasks that are pending or in_progress
    # tasks = Task.objects.filter(Q(status="PENDING") | Q(status="IN_PROGRESS"))

    # select_related(foreign_key, one_to_one_field)
    """tasks = Task.objects.select_related("detail").all()
    tasks = TaskDetail.objects.select_related("task").all()
    Both way because of one_to_one_field relation
    """
    # tasks = Task.objects.select_related( "project").all()  - it can be used in one side because foreign_key relation

    # prefetch_related(reverse foreign_key, many_to_many_field)
    # projects = Project.objects.prefetch_related("task_set").all() - foreign key relation example

    # employees = Employee.objects.prefetch_related("task_set").all() - many to many relationship

    # Aggregation func
    # total_tasks = Task.objects.aggregate(total_tasks=Count("id"))

    projects = Project.objects.annotate(cnt=Count("task")).order_by("cnt")
    return render(request, "show-task.html", {"projects": projects})


class ViewTaskListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Class Based View Example for View Task"""

    permission_required = "tasks.view_task"
    login_url = "sign-in"
    template_name = "show-task.html"
    model = Project
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.annotate(cnt=Count("task")).order_by("cnt")


@login_required
@permission_required("tasks.view_task", raise_exception=True)
def task_details(request, task_id):
    task = Task.objects.select_related("detail").get(id=task_id)
    status_choices = Task.STATUS_CHOICES

    if request.method == "POST":
        selected_status = request.POST.get("task_status")
        task.status = selected_status
        task.save()
        return redirect("task-details", getattr(task, "id"))

    return render(
        request,
        "show-task-details.html",
        {"task": task, "status_choices": status_choices},
    )


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
        redirect("manager-dashboard")
    elif is_employee(request.user):
        redirect("user-dashboard")
    elif is_admin(request.user):
        return redirect("admin-dashboard")

    return redirect("no-permission")
