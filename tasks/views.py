import random

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import redirect, render

from tasks.forms import TaskDetailModelForm, TaskModelForm
from tasks.models import Project, Task


# Create your views here.
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


def user_dashboard(request):
    return render(request, "dashboard/user-dashboard.html")


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
        task_detail_form = TaskDetailModelForm(request.POST)

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


def update_task(request, id):
    task = Task.objects.get(id=id)

    task_form = TaskModelForm(instance=task)
    task_detail_form = TaskDetailModelForm(instance=task.detail)

    if request.method == "POST":
        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = TaskDetailModelForm(request.POST, instance=task.detail)

        if task_form.is_valid() and task_detail_form.is_valid():

            task_form.save()
            task_detail_form.save()

            messages.success(request, "Task Updated Successfully")
            return redirect("update-task", id)

    context = {"task_form": task_form, "task_detail_form": task_detail_form}

    return render(request, "task-form.html", context=context)


def delete_task(request, id):
    if request.method == "POST":
        task = Task.objects.get(id=id)
        task.delete()
        messages.success(request, "Task Deleted Successfully")
        return redirect("manager-dashboard")
    else:
        messages.error(request, "Something went wrong")
        return redirect("manager-dashboard")


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
