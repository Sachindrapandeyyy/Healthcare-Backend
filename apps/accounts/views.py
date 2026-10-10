from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import extend_schema, inline_serializer
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new user with name, email, and password.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account with secure password hashing.",
        request=RegisterSerializer,
        responses={201: inline_serializer(
            name='RegisterResponse',
            fields={
                'message': serializers.CharField(),
                'user': UserSerializer()
            }
        )}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Log in a user and return JWT tokens (access & refresh).
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        summary="User Login (JWT Token)",
        description="Authenticates credentials and returns JWT access and refresh tokens.",
        request=LoginSerializer,
        responses={200: inline_serializer(
            name='LoginResponse',
            fields={
                'message': serializers.CharField(),
                'access': serializers.CharField(),
                'refresh': serializers.CharField(),
                'user': UserSerializer()
            }
        )}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        return Response({
            'message': 'Login successful',
            'access': validated['access'],
            'refresh': validated['refresh'],
            'user': UserSerializer(validated['user']).data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklists the provided refresh token for secure session revocation.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout & Blacklist Token",
        description="Revokes the refresh token to terminate session securely.",
        request=inline_serializer(
            name='LogoutRequest',
            fields={'refresh': serializers.CharField(help_text="JWT Refresh token")}
        ),
        responses={200: inline_serializer(
            name='LogoutResponse',
            fields={'message': serializers.CharField()}
        )}
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Logged out successfully. Token has been blacklisted.'},
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            return Response(
                {'error': 'Invalid or expired token.', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
