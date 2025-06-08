from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'wallet_address', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Try to find user by email
            try:
                user_obj = User.objects.get(email=email)
                print(f"Found user: {user_obj.username}, email: {user_obj.email}")
                
                # Authenticate using username (Django's default)
                authenticated_user = authenticate(username=user_obj.username, password=password)
                print(f"Authentication result: {authenticated_user}")
                
                if not authenticated_user:
                    print("Authentication failed - checking password manually")
                    # Let's also check if the password is correct
                    if user_obj.check_password(password):
                        print("Password is correct, but authenticate() failed")
                        authenticated_user = user_obj
                    else:
                        print("Password is incorrect")
                        
            except User.DoesNotExist:
                print(f"User with email {email} does not exist")
                authenticated_user = None
                
            if not authenticated_user:
                raise serializers.ValidationError('Invalid credentials')
            if not authenticated_user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = authenticated_user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'wallet_address', 'date_joined', 'is_verified')
        read_only_fields = ('id', 'username', 'date_joined', 'is_verified')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'wallet_address')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
