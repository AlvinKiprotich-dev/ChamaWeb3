from django.contrib import admin
from .models import ChamaGroup, GroupMembership, Contribution, Payout, Transaction


@admin.register(ChamaGroup)
class ChamaGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'contribution_amount', 'contribution_frequency', 'max_members', 
                   'total_members', 'status', 'created_by', 'created_at')
    list_filter = ('contribution_frequency', 'status', 'created_at')
    search_fields = ('name', 'description', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at', 'contract_address')
    
    def total_members(self, obj):
        return obj.members.count()
    total_members.short_description = 'Total Members'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'payout_position', 'has_received_payout', 
                   'role', 'joined_at')
    list_filter = ('has_received_payout', 'joined_at', 'group__name', 'role')
    search_fields = ('user__email', 'group__name')
    readonly_fields = ('joined_at',)


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('member', 'group', 'amount', 'status', 'transaction_hash', 'contribution_date')
    list_filter = ('status', 'contribution_date', 'group__name')
    search_fields = ('member__email', 'group__name', 'transaction_hash')
    readonly_fields = ('contribution_date', 'block_number', 'gas_used')


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('group', 'recipient', 'amount', 'scheduled_date', 'processed_at', 
                   'status', 'transaction_hash')
    list_filter = ('status', 'scheduled_date', 'processed_at', 'group__name')
    search_fields = ('recipient__email', 'group__name', 'transaction_hash')
    readonly_fields = ('block_number', 'gas_used')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'transaction_type', 'amount', 'status', 
                   'transaction_hash', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at', 'group__name')
    search_fields = ('user__email', 'group__name', 'transaction_hash')
    readonly_fields = ('created_at',)
