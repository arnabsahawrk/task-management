# from django.http import HttpResponse
from django.shortcuts import render

# from tasks.forms import TaskForm
# from tasks.models import Employee, Task
from tasks.forms import TaskModelForm


# Create your views here.
def manager_dashboard(request):
    return render(request, "dashboard/manager-dashboard.html")


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
    form = TaskModelForm()

    if request.method == "POST":
        form = TaskModelForm(request.POST)

        if form.is_valid():
            form.save()
            # return HttpResponse("Task added successfully")
            return render(
                request,
                "task-form.html",
                {"form": form, "message": "Task added successfully"},
            )

    context = {"form": form}
    return render(request, "task-form.html", context=context)
