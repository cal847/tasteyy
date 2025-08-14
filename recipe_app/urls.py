from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
def home(request):
    return JsonResponse({"message": "Welcome to recipe app APIs"})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),

    #user urls`
    path('api/', include('users.urls')),

    #admin urls
    path('api/admin/', include('admin.urls')),

    #recipes urls
    path('api/recipes/', include('recipes.urls')),
]

