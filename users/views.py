from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import User, EmailVerificationToken
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)
from .utils import create_verification_token, send_verification_email, resend_verification_email


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        print(f"Registration request received: {request.data}")
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        user = serializer.save()
        print(f"User created successfully: {user.email}")
        
        # Create and send verification email
        token = create_verification_token(user)
        email_sent = send_verification_email(user, token)
        print(f"Verification email sent: {email_sent}")
        
        # Return response without JWT tokens (user needs to verify email first)
        return Response({
            'user': UserProfileSerializer(user).data,
            'message': 'Registration successful. Please check your email to verify your account.',
            'email_sent': email_sent
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        print(f"Login request received: {request.data}")
        serializer = UserLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"Login validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        user = serializer.validated_data['user']
        print(f"User authenticated: {user.email}, verified: {user.is_verified}")
        
        # Check if user is verified
        if not user.is_verified:
            return Response({
                'error': 'Email not verified. Please check your email and verify your account.',
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_403_FORBIDDEN)
          # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """
    Verify user email with token
    """
    token_str = request.GET.get('token')
    if not token_str:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = get_object_or_404(EmailVerificationToken, token=token_str)
        
        if token.is_used:
            return Response({'error': 'Token has already been used'}, status=status.HTTP_400_BAD_REQUEST)
        
        if token.is_expired():
            return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the user
        user = token.user
        user.is_verified = True
        user.save()
        
        # Mark token as used
        token.is_used = True
        token.save()
        
        # Generate JWT tokens for automatic login
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Email verified successfully',
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
        
    except EmailVerificationToken.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_verification_email(request):
    """
    Resend verification email
    """
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        if user.is_verified:
            return Response({'error': 'User is already verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        success, message = resend_verification_email(user)
        
        if success:
            return Response({'message': message})
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
