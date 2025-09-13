from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register("me", views.UserViewSet, basename="me")

urlpatterns = [
    path('register/', views.register_form_view, name='register'),
    path('login/', views.login_form_view, name='login'),
    path('logout/', views.logout_form_view, name='logout'),
    path("account/", views.profile_view, name="profile_view"),
    path("upload-recipe/", views.upload_recipe, name="upload-recipe"),
    

    path("api/", include(router.urls)),
    path("api/register/", views.RegisterView.as_view(), name="api-register"),
    path("api/login/", views.LoginView.as_view(), name="api-login"),
    path("api/logout/", views.LogoutView.as_view(), name="api-logout"),
]
