from django.urls import path, include, reverse_lazy
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

router = DefaultRouter()
router.register("me", views.UserViewSet, basename="me")

urlpatterns = [
    path('register/', views.register_form_view, name='register'),
    path('login/', views.login_form_view, name='login'),
    path('logout/', views.logout_form_view, name='logout'),
    path("profile/", views.profile_view, name="profile_view"),

    # Password reset urls
    path('password_reset/', auth_views.PasswordResetView.as_view(
        success_url=reverse_lazy('accounts:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # API urls
    path("api/", include(router.urls)),
    path("api/register/", views.RegisterView.as_view(), name="api-register"),
    path("api/login/", views.LoginView.as_view(), name="api-login"),
    path("api/logout/", views.LogoutView.as_view(), name="api-logout"),
]
