from rest_framework import serializers
from django.db import transaction
from .models import ChamaGroup, GroupMembership, Contribution, Payout, Transaction
from users.serializers import UserProfileSerializer


class ChamaGroupSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)
    total_members = serializers.SerializerMethodField()
    current_contributions = serializers.SerializerMethodField()

    class Meta:
        model = ChamaGroup
        fields = ('id', 'name', 'description', 'contribution_amount', 'contribution_frequency',
                 'start_date', 'end_date', 'max_members', 'total_members', 'current_contributions',
                 'contract_address', 'status', 'created_by', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'contract_address')

    def get_total_members(self, obj):
        return obj.members.count()

    def get_current_contributions(self, obj):
        return obj.contributions.filter(status='confirmed').count()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    group = ChamaGroupSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        fields = ('id', 'user', 'group', 'payout_position', 'has_received_payout',
                 'role', 'joined_at')
        read_only_fields = ('id', 'user', 'group', 'joined_at')


class JoinGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()

    def validate_group_id(self, value):
        try:
            group = ChamaGroup.objects.get(id=value)
        except ChamaGroup.DoesNotExist:
            raise serializers.ValidationError("Group does not exist")
        
        if group.status != 'active':
            raise serializers.ValidationError("Group is not active")
        
        if group.members.count() >= group.max_members:
            raise serializers.ValidationError("Group is full")
        
        user = self.context['request'].user
        if group.members.filter(user=user).exists():
            raise serializers.ValidationError("You are already a member of this group")
        
        return value


class ContributionSerializer(serializers.ModelSerializer):
    member = UserProfileSerializer(read_only=True)
    group = ChamaGroupSerializer(read_only=True)

    class Meta:
        model = Contribution
        fields = ('id', 'member', 'group', 'amount', 'transaction_hash', 'status',
                 'block_number', 'gas_used', 'contribution_date')
        read_only_fields = ('id', 'member', 'group', 'transaction_hash', 'status',
                           'block_number', 'gas_used', 'contribution_date')


class MakeContributionSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=8)
    transaction_hash = serializers.CharField(max_length=66)

    def validate_group_id(self, value):
        try:
            group = ChamaGroup.objects.get(id=value)
        except ChamaGroup.DoesNotExist:
            raise serializers.ValidationError("Group does not exist")
        
        user = self.context['request'].user
        if not group.members.filter(user=user).exists():
            raise serializers.ValidationError("You are not a member of this group")
        
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class PayoutSerializer(serializers.ModelSerializer):
    recipient = UserProfileSerializer(read_only=True)
    group = ChamaGroupSerializer(read_only=True)

    class Meta:
        model = Payout
        fields = ('id', 'group', 'recipient', 'amount', 'scheduled_date', 'processed_at',
                 'transaction_hash', 'status', 'block_number', 'gas_used')
        read_only_fields = ('id', 'group', 'recipient', 'processed_at', 'transaction_hash',
                           'status', 'block_number', 'gas_used')


class TransactionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    group = ChamaGroupSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'group', 'transaction_type', 'amount', 'transaction_hash',
                 'block_number', 'gas_used', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'group', 'created_at')


class GroupStatsSerializer(serializers.Serializer):
    total_contributions = serializers.DecimalField(max_digits=18, decimal_places=8)
    total_members = serializers.IntegerField()
    completed_rounds = serializers.IntegerField()
    next_payout_date = serializers.DateTimeField()
    next_recipient = UserProfileSerializer()


class UserGroupsSerializer(serializers.ModelSerializer):
    group = ChamaGroupSerializer(read_only=True)
    contribution_status = serializers.SerializerMethodField()

    class Meta:
        model = GroupMembership
        fields = ('id', 'group', 'payout_position', 'has_received_payout',
                 'role', 'contribution_status', 'joined_at')

    def get_contribution_status(self, obj):
        # Check if user has contributed this round
        latest_payout = obj.group.payouts.filter(status='completed').order_by('-processed_at').first()
        if latest_payout:
            contributions_after_payout = obj.group.contributions.filter(
                member=obj.user,
                contribution_date__gt=latest_payout.processed_at,
                status='confirmed'
            ).exists()
        else:
            contributions_after_payout = obj.group.contributions.filter(
                member=obj.user,
                status='confirmed'
            ).exists()
        
        return "contributed" if contributions_after_payout else "pending"
