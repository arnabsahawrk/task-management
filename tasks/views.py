from django.http import HttpResponse

# from django.shortcuts import render


# Create your views here.
def home(request):
    return HttpResponse("Welcome to the task management system")


def contact(request):
    return HttpResponse("<h1 style='color: red'>This Is Contact Page</h1>")


def show_task(request):
    return HttpResponse("This is show task page")


def show_specific_task(request, id):
    print(id)
    print("Type: ", type(id))
    return HttpResponse(f"This is specific task page {id}")
