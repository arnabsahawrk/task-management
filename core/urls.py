from django.urls import path

from core.views import home, no_permission


urlpatterns = [
    path("", home, name="home"),
    path("no-permission/", no_permission, name="no-permission"),
]
