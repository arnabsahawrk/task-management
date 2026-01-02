from users.views import (
    CustomLoginView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetView,
    ProfileView,
    admin_dashboard,
    assign_role,
    create_group,
    group_list,
    # sign_in,
    # sign_out,
    sign_up,
    activate_user,
    CustomPasswordChangeView,
)
from django.urls import path
from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeDoneView,
)


urlpatterns = [
    path("sign-up/", sign_up, name="sign-up"),
    # path("sign-in/", sign_in, name="sign-in"),
    path("sign-in/", CustomLoginView.as_view(), name="sign-in"),
    path("sign-out/", LogoutView.as_view(), name="sign-out"),
    path("activate/<int:user_id>/<str:token>/", activate_user),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),
    path("admin/<int:user_id>/assign-role/", assign_role, name="assign-role"),
    path("admin/create-group/", create_group, name="create-group"),
    path("admin/group-list/", group_list, name="group-list"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "password-change/",
        CustomPasswordChangeView.as_view(),
        name="password-change",
    ),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(
            template_name="accounts/password-change-done.html"
        ),
        name="password_change_done",
    ),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password-reset"),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
