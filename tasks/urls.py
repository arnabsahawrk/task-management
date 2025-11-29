from django.urls import path

from tasks.views import (
    create_task,
    delete_task,
    manager_dashboard,
    update_task,
    user_dashboard,
    view_task,
)

urlpatterns = [
    path("manager-dashboard/", manager_dashboard, name="manager-dashboard"),
    path("user-dashboard/", user_dashboard, name="user-dashboard"),
    path("create-task/", create_task, name="create-task"),
    path("view-task/", view_task, name="view-task"),
    path("update-task/<int:id>/", update_task, name="update-task"),
    path("delete-task/<int:id>/", delete_task, name="delete-task"),
]
