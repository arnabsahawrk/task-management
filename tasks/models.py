from typing import TYPE_CHECKING, Optional
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
"""class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # task_set -> for foreignKey it set '.._set' something like that

    def __str__(self) -> str:
        return self.name"""


class Task(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    ]
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    # assigned_to = models.ManyToManyField(Employee)
    assigned_to = models.ManyToManyField(User, related_name="task")
    title = models.CharField(max_length=250)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # taskdetail -> this name is auto set, can change the name via "related_name='details'"

    if TYPE_CHECKING:  # Pylance fix
        from .models import TaskDetail

        detail: Optional["TaskDetail"]

    def __str__(self) -> str:
        return self.title


class TaskDetail(models.Model):
    HIGH, MEDIUM, LOW = "H", "M", "L"
    PRIORITY_OPTIONS = ((HIGH, "High"), (MEDIUM, "Medium"), (LOW, "Low"))

    # std_id = models.CharField(max_length=200, primary_key=True)
    task = models.OneToOneField(
        Task, on_delete=models.DO_NOTHING, related_name="detail"
    )
    priority = models.CharField(max_length=1, choices=PRIORITY_OPTIONS, default=LOW)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Details form Task {self.task.title}"


class Project(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    # assigned_to = models.ManyToManyField(Employee)

    def __str__(self):
        return self.name
