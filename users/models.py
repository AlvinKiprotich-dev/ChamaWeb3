from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

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
