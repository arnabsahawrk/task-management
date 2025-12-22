from typing import TYPE_CHECKING

from django import forms

from tasks.models import Task, TaskDetail


# Django Form
class TaskForm(forms.Form):
    title = forms.CharField(max_length=250)
    description = forms.CharField(
        widget=forms.Textarea, label="Task Description", max_length=250
    )
    due_date = forms.DateField(widget=forms.SelectDateWidget, label="Due Date")
    assigned_to = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=[], label="Assigned To"
    )

    def __init__(self, *args, **kwargs):
        print(args, kwargs)
        employees = kwargs.pop("employees", [])
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].choices = [(emp.id, emp.name) for emp in employees]


class StyledFormMixin:
    """
    A reusable mixin that applies modern Tailwind styling
    to all Django form fields automatically.
    """

    if TYPE_CHECKING:
        fields: dict[str, forms.Field]

    # Base styles applied to most inputs
    base_input_classes = (
        "w-full px-4 py-3 rounded-xl border-2 border-gray-300 "
        "bg-white shadow-sm transition duration-200 "
        "focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
    )

    textarea_classes = (
        "w-full px-4 py-3 rounded-xl border-2 border-gray-300 "
        "bg-white shadow-sm resize-none transition duration-200 "
        "focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
    )

    select_classes = (
        "w-full px-4 py-3 rounded-xl border-2 border-gray-300 "
        "bg-white shadow-sm transition duration-200 "
        "focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
    )

    checkbox_group_classes = "space-y-3"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

    def apply_styled_widgets(self):
        for name, field in self.fields.items():
            widget = field.widget
            label = field.label or name.replace("_", " ").title()

            # Text-like fields
            if isinstance(
                widget,
                (
                    forms.TextInput,
                    forms.EmailInput,
                    forms.PasswordInput,
                    forms.NumberInput,
                ),
            ):
                widget.attrs.update(
                    {
                        "class": self.base_input_classes,
                        "placeholder": f"Enter {label}",
                    }
                )

            # Textarea
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update(
                    {
                        "class": self.textarea_classes,
                        "placeholder": f"Enter {label}",
                        "rows": 5,
                    }
                )

            # Dropdowns, Select, Date widgets
            elif isinstance(
                widget,
                (
                    forms.Select,
                    forms.SelectDateWidget,
                    forms.DateInput,
                    forms.TimeInput,
                ),
            ):
                widget.attrs.update(
                    {
                        "class": self.select_classes,
                    }
                )

            # Checkboxes (Multiple)
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs.update({"class": self.checkbox_group_classes})

            # Single Checkbox
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.update(
                    {
                        "class": "h-5 w-5 text-rose-600 focus:ring-rose-500 "
                        "rounded-md border-gray-300"
                    }
                )

            # Fallback for unknown widgets
            else:
                widget.attrs.update({"class": self.base_input_classes})


# Django Model Form
class TaskModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        # fields = "__all__"
        # exclude = ["project", "is_completed", "created_at", "updated_at"]
        fields = ["title", "description", "due_date", "assigned_to"]
        widgets = {
            "due_date": forms.SelectDateWidget,
            "assigned_to": forms.CheckboxSelectMultiple,
        }

        # Manual Widget
        """widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus-ring-rose-500",
                    "placeholder": "Enter a descriptive task title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm resize-none focus:outline-none focus:border-rose-500 focus-ring-rose-500",
                    "placeholder": "Enter task description...",
                }
            ),
            "due_date": forms.SelectDateWidget,
            "assigned_to": forms.CheckboxSelectMultiple,
        }"""

    # Widget using mixins
    """def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()"""


class TaskDetailModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TaskDetail
        fields = ["priority", "notes", "asset"]

    # Widget using mixins
    """def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()"""
