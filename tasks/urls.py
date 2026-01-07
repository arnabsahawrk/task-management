from django.urls import path

from tasks.views import (
    DeleteTaskView,
    EmployeeDashboardView,
    HiHowGreetings,
    # create_task,
    # CreateTaskView,
    CreateTaskCreateView,
    TaskDetailView,
    ViewTaskListView,
    UpdateTaskUpdateView,
    dashboard,
    # delete_task,
    # manager_dashboard,
    ManagerDashboardView,
    # update_task,
    # employee_dashboard,
    # view_task,
    # task_details,
)

urlpatterns = [
    # path("manager-dashboard/", manager_dashboard, name="manager-dashboard"),
    path(
        "manager-dashboard/", ManagerDashboardView.as_view(), name="manager-dashboard"
    ),
    # path("user-dashboard/", employee_dashboard, name="user-dashboard"),
    path("user-dashboard/", EmployeeDashboardView.as_view(), name="user-dashboard"),
    # path("create-task/", create_task, name="create-task"),
    path("create-task/", CreateTaskCreateView.as_view(), name="create-task"),
    # path("view-task/", view_task, name="view-task"),
    path("view-task/", ViewTaskListView.as_view(), name="view-task"),
    # path("task/<int:task_id>/details/", task_details, name="task-details"),
    path("task/<int:task_id>/details/", TaskDetailView.as_view(), name="task-details"),
    path("update-task/<int:pk>/", UpdateTaskUpdateView.as_view(), name="update-task"),
    # path("delete-task/<int:id>/", delete_task, name="delete-task"),
    path("delete-task/<int:pk>/", DeleteTaskView.as_view(), name="delete-task"),
    path("dashboard/", dashboard, name="dashboard"),
    path(
        "greetings/",
        HiHowGreetings.as_view(greetings="Hello, this is from the greetings view"),
        name="greetings",
    ),
]
