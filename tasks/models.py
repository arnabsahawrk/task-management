from typing import TYPE_CHECKING, Optional
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail


from django.db import models


# Create your models here.
class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # task_set -> for foreignKey it set '.._set' something like that

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    ]
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(Employee)
    title = models.CharField(max_length=250)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    is_completed = models.BooleanField(default=False)
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
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="detail")
    priority = models.CharField(max_length=1, choices=PRIORITY_OPTIONS, default=LOW)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Details form Task {self.task.title}"


class Project(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    assigned_to = models.ManyToManyField(Employee)

    def __str__(self):
        return self.name


""" @receiver(post_save, sender=Task)
def notify_task_creation(sender, instance, created, **kwargs):
    print("sender ", sender)
    print("instance ", instance)
    print(kwargs)
    print(created)

    if created:
        instance.is_completed = True
        instance.save() """


""" @receiver(pre_save, sender=Task)
def notify_task_creation(sender, instance, **kwargs):
    print("sender ", sender)
    print("instance ", instance)
    print(kwargs)

    instance.is_completed = True """


@receiver(m2m_changed, sender=Task)
def notify_task_creation(sender, instance, created, **kwargs):
    if created:
        assigned_emails = [emp.email for emp in instance.assigned_to.all()]

        send_mail(
            "New Task Assigned",
            f"You have been assigned to the task: {instance.title}",
            "arnabsaha5199@gmail.com",
            assigned_emails,
            # fail_silently=False,
        )
