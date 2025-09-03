from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("account/", views.UserViewSet, basename="account")

urlpatterns = [
    path('register/', views.register_form_view, name='register'),  # ← HTML form
    path('login/', views.login_form_view, name='login'), 

    path("api/", include(router.urls)),
    path("api/register/", views.RegisterView.as_view(), name="register"),
    path("api/login/", views.LoginView.as_view(), name="login"),
    path("api/logout/", views.LogoutView.as_view(), name="logout"),
]
