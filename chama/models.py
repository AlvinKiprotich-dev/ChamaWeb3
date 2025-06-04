from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

User = get_user_model()

class ChamaGroup(models.Model):
    """
    Main Chama Group model
    """
    CHAMA_TYPES = [
        ('merry_go_round', 'Merry-Go-Round'),
        ('investment', 'Investment Group'),
        ('sacco', 'SACCO'),
    ]
    
    CHAMA_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    chama_type = models.CharField(max_length=20, choices=CHAMA_TYPES, default='merry_go_round')
    status = models.CharField(max_length=20, choices=CHAMA_STATUS, default='active')
    
    # Financial details
    contribution_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Monthly contribution amount in AVAX"
    )
    contribution_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        default='monthly'
    )
    
    # Group settings
    max_members = models.PositiveIntegerField(default=12)
    minimum_members = models.PositiveIntegerField(default=3)
    
    # Smart contract details
    contract_address = models.CharField(max_length=42, blank=True, null=True)
    contract_deployed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, through='GroupMembership', related_name='chama_groups')
    
    class Meta:
        db_table = 'chama_groups'
        verbose_name = 'Chama Group'
        verbose_name_plural = 'Chama Groups'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.get_chama_type_display()})"
    
    @property
    def total_pool(self):
        """Calculate total expected pool amount"""
        return self.contribution_amount * self.members.count()
    
    @property
    def current_members_count(self):
        """Get current number of active members"""
        return self.memberships.filter(status='active').count()
    
    def can_add_member(self):
        """Check if group can accept new members"""
        return self.current_members_count < self.max_members and self.status == 'active'


class GroupMembership(models.Model):
    """
    Through model for User-ChamaGroup relationship
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('treasurer', 'Treasurer'),
        ('secretary', 'Secretary'),
        ('member', 'Member'),
    ]
    
    MEMBERSHIP_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('left', 'Left Group'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    group = models.ForeignKey(ChamaGroup, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='active')
    
    # Payout order for merry-go-round
    payout_position = models.PositiveIntegerField(null=True, blank=True)
    has_received_payout = models.BooleanField(default=False)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'group_memberships'
        verbose_name = 'Group Membership'
        verbose_name_plural = 'Group Memberships'
        unique_together = ['user', 'group']
        ordering = ['payout_position', 'joined_at']
        
    def __str__(self):
        return f"{self.user.email} - {self.group.name} ({self.get_role_display()})"


class Contribution(models.Model):
    """
    Model for tracking individual contributions
    """
    CONTRIBUTION_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(ChamaGroup, on_delete=models.CASCADE, related_name='contributions')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    
    # Financial details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    expected_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Blockchain details
    transaction_hash = models.CharField(max_length=66, unique=True, null=True, blank=True)
    block_number = models.PositiveIntegerField(null=True, blank=True)
    gas_used = models.PositiveIntegerField(null=True, blank=True)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=CONTRIBUTION_STATUS, default='pending')
    contribution_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        db_table = 'contributions'
        verbose_name = 'Contribution'
        verbose_name_plural = 'Contributions'
        ordering = ['-contribution_date']
        
    def __str__(self):
        return f"{self.member.email} - {self.group.name} - {self.amount} AVAX"
    
    @property
    def is_late(self):
        """Check if contribution is late"""
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status == 'pending'
    
    @property
    def is_complete(self):
        """Check if full amount was contributed"""
        return self.amount >= self.expected_amount


class Payout(models.Model):
    """
    Model for tracking payouts in merry-go-round
    """
    PAYOUT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(ChamaGroup, on_delete=models.CASCADE, related_name='payouts')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_payouts')
    
    # Financial details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Blockchain details
    transaction_hash = models.CharField(max_length=66, unique=True, null=True, blank=True)
    block_number = models.PositiveIntegerField(null=True, blank=True)
    gas_used = models.PositiveIntegerField(null=True, blank=True)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=PAYOUT_STATUS, default='scheduled')
    scheduled_date = models.DateField()
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Round information
    round_number = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'payouts'
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'
        ordering = ['-scheduled_date']
        unique_together = ['group', 'round_number']
        
    def __str__(self):
        return f"Round {self.round_number} - {self.recipient.email} - {self.amount} AVAX"


class Transaction(models.Model):
    """
    Model for tracking all blockchain transactions
    """
    TRANSACTION_TYPES = [
        ('contribution', 'Contribution'),
        ('payout', 'Payout'),
        ('contract_deployment', 'Contract Deployment'),
        ('other', 'Other'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_hash = models.CharField(max_length=66, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Related objects
    group = models.ForeignKey(ChamaGroup, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    contribution = models.OneToOneField(Contribution, on_delete=models.CASCADE, null=True, blank=True)
    payout = models.OneToOneField(Payout, on_delete=models.CASCADE, null=True, blank=True)
    
    # Blockchain details
    from_address = models.CharField(max_length=42)
    to_address = models.CharField(max_length=42)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gas_price = models.BigIntegerField()
    gas_used = models.PositiveIntegerField(null=True, blank=True)
    block_number = models.PositiveIntegerField(null=True, blank=True)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.transaction_hash[:10]}..."
