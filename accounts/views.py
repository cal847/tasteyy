from rest_framework import viewsets, generics, status
from .serializers import UserSerializer, MyTokenObtainPairSerializer, LoginSerializer
from rest_framework.decorators import action
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib.auth import login, logout

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Register endpoint
    Allows registration+login
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    form = RegistrationForm

    def create(self, request, *args, **kwargs):
        """Logs in automatically after register by returning tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # generate tokens
        refresh = RefreshToken.for_user(user)
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        
        return Response(
            {**token_data},
            status=status.HTTP_201_CREATED)

def register_form_view(request):
    """
    Handle HTML form submission for browser users
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account was created.")
            return redirect('home')
    else:
        form = RegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

class LoginView(generics.GenericAPIView):
    """Custom login view"""

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # generate refresh tokens
        refresh = RefreshToken.for_user(user)
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response({**token_data}, status=status.HTTP_201_CREATED)

def login_form_view(request):
    """
    Handles login via HTML form for browser users
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")

                # Redirect to 'next' if exists, else home
                return redirect(request.GET.get("next", "home"))
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid input. Please check your credentials.")
    else:
        form = AuthenticationForm()
    
    return render(request, "accounts/login.html", {"form": form})

class LogoutView(APIView):
    """Logout endpoint"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            if not refresh_token:
                return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

def logout_form_view(request):
    """
    Handles logouts in template view
    """
    if request.user.is_authenticated:
        username=request.user.username
        logout(request)
        message = f"You've been logged out successfully!"
    else:
        message = f"Invalid request"
    
    return redirect('home')

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.IsAdmin:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    def get_permissions(self):
        """Custom permissions per action"""
        if self.action == "list":
            return [IsAdminUser()]
        elif self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]
