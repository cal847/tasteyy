from rest_framework import viewsets, generics, status
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from rest_framework.decorators import action
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Register endpoint
    Allows registration+login
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """Logs in automatically after register by returning tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        #generate tokens
        refresh = RefreshToken.for_user(user)
        token_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                }
        return Response(
                {**token_data}, status=status.HTTP_201_CREATED
                )

class LoginView(generics.GenericAPIView):
    """Custom login view"""
    permission_classes = [AllowAny]


    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        #generate refresh tokens
        refresh = RefreshToken.for_user(user)
        token_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                }
        return Response(
                {**token_data}, status=status.HTTP_201_CREATED
                )

class LogoutView(APIView):
    """Logout endpoint"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Custom permissions per action"""
        if self.action == 'list':
            return [IsAdminUser()]
        elif self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
