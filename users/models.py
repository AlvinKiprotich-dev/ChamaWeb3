from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    """
    Custom User model for Chama system
    """
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Administrator'),
    ]
    
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        unique=True,
        help_text="Phone number in international format"
    )
    is_verified = models.BooleanField(default=False)
    wallet_address = models.CharField(
        max_length=42,
        blank=True,
        null=True,
        help_text="User's Avalanche wallet address"
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Use email as the primary identifier for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.username})"
    
    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def has_wallet(self):
        """Check if user has a wallet address"""
        return bool(self.wallet_address)


class EmailVerificationToken(models.Model):
    """
    Email verification token model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verification_tokens'
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiration to 24 hours from now
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Verification token for {self.user.email}"
