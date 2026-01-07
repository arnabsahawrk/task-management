from django.urls import path

from tasks.views import (
    DeleteTaskView,
    EmployeeDashboardView,
    CreateTaskCreateView,
    TaskDetailView,
    ViewTaskListView,
    UpdateTaskUpdateView,
    ManagerDashboardView,
    dashboard,
)

urlpatterns = [
    path(
        "manager-dashboard/", ManagerDashboardView.as_view(), name="manager-dashboard"
    ),
    path("user-dashboard/", EmployeeDashboardView.as_view(), name="user-dashboard"),
    path("create-task/", CreateTaskCreateView.as_view(), name="create-task"),
    path("view-task/", ViewTaskListView.as_view(), name="view-task"),
    path("task/<int:task_id>/details/", TaskDetailView.as_view(), name="task-details"),
    path("update-task/<int:pk>/", UpdateTaskUpdateView.as_view(), name="update-task"),
    path("delete-task/<int:pk>/", DeleteTaskView.as_view(), name="delete-task"),
    path("dashboard/", dashboard, name="dashboard"),
]
