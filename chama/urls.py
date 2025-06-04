from django.urls import path
from .views import (
    ChamaGroupListCreateView,
    ChamaGroupDetailView,
    JoinGroupView,
    LeaveGroupView,
    UserGroupsView,
    GroupMembersView,
    MakeContributionView,
    UserContributionsView,
    GroupContributionsView,
    GroupPayoutsView,
    UserTransactionsView,
    GroupStatsView,
    dashboard_stats
)

app_name = 'chama'

urlpatterns = [
    # Group management
    path('groups/', ChamaGroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', ChamaGroupDetailView.as_view(), name='group-detail'),
    path('groups/join/', JoinGroupView.as_view(), name='join-group'),
    path('groups/<int:group_id>/leave/', LeaveGroupView.as_view(), name='leave-group'),
    path('groups/<int:group_id>/members/', GroupMembersView.as_view(), name='group-members'),
    path('groups/<int:group_id>/stats/', GroupStatsView.as_view(), name='group-stats'),
    
    # User groups
    path('my-groups/', UserGroupsView.as_view(), name='user-groups'),
    
    # Contributions
    path('contributions/', UserContributionsView.as_view(), name='user-contributions'),
    path('contributions/make/', MakeContributionView.as_view(), name='make-contribution'),
    path('groups/<int:group_id>/contributions/', GroupContributionsView.as_view(), name='group-contributions'),
    
    # Payouts
    path('groups/<int:group_id>/payouts/', GroupPayoutsView.as_view(), name='group-payouts'),
    
    # Transactions
    path('transactions/', UserTransactionsView.as_view(), name='user-transactions'),
    
    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
]
