from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Q, Max
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import ChamaGroup, GroupMembership, Contribution, Payout, Transaction
from .tasks import verify_blockchain_transaction
from .serializers import (
    ChamaGroupSerializer,
    GroupMembershipSerializer,
    JoinGroupSerializer,
    ContributionSerializer,
    MakeContributionSerializer,
    PayoutSerializer,
    TransactionSerializer,
    GroupStatsSerializer,
    UserGroupsSerializer
)


class ChamaGroupListCreateView(generics.ListCreateAPIView):
    serializer_class = ChamaGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ChamaGroup.objects.filter(status='active')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        return queryset


class ChamaGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChamaGroup.objects.all()
    serializer_class = ChamaGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChamaGroup.objects.filter(
            Q(created_by=self.request.user) | Q(members__user=self.request.user)
        ).distinct()


class JoinGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = JoinGroupSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        group = get_object_or_404(ChamaGroup, id=serializer.validated_data['group_id'])
          # Determine position in rotation
        last_position = group.members.aggregate(
            max_position=Max('position_in_rotation')
        )['max_position'] or 0
        
        membership = GroupMembership.objects.create(
            user=request.user,
            group=group,
            position_in_rotation=last_position + 1
        )
        
        return Response(
            GroupMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )


class LeaveGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        try:
            membership = GroupMembership.objects.get(user=request.user, group_id=group_id)
            
            # Check if user has received payout
            if membership.has_received_payout:
                return Response(
                    {'error': 'Cannot leave group after receiving payout'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check for pending contributions
            pending_contributions = membership.group.contributions.filter(
                user=request.user,
                is_confirmed=False
            ).exists()
            
            if pending_contributions:
                return Response(
                    {'error': 'Cannot leave group with pending contributions'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            membership.delete()
            return Response({'message': 'Successfully left the group'})
            
        except GroupMembership.DoesNotExist:
            return Response(
                {'error': 'You are not a member of this group'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserGroupsView(generics.ListAPIView):
    serializer_class = UserGroupsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GroupMembership.objects.filter(user=self.request.user).select_related('group')


class GroupMembersView(generics.ListAPIView):
    serializer_class = GroupMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        # Ensure user is a member of the group or is the creator
        group = get_object_or_404(ChamaGroup, id=group_id)
        if not (group.created_by == self.request.user or 
                group.members.filter(user=self.request.user).exists()):
            return GroupMembership.objects.none()
        
        return GroupMembership.objects.filter(group_id=group_id).select_related('user')


class MakeContributionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MakeContributionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        group = get_object_or_404(ChamaGroup, id=serializer.validated_data['group_id'])
          # Create contribution record
        contribution = Contribution.objects.create(
            user=request.user,
            group=group,
            amount=serializer.validated_data['amount'],
            transaction_hash=serializer.validated_data['transaction_hash']
        )
        
        # Verify transaction on blockchain asynchronously
        verify_blockchain_transaction.delay(contribution.id)
        
        return Response(
            ContributionSerializer(contribution).data,
            status=status.HTTP_201_CREATED
        )


class UserContributionsView(generics.ListAPIView):
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Contribution.objects.filter(user=self.request.user).select_related('group')
        group_id = self.request.query_params.get('group_id')
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        return queryset.order_by('-created_at')


class GroupContributionsView(generics.ListAPIView):
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        # Ensure user is a member of the group
        group = get_object_or_404(ChamaGroup, id=group_id)
        if not group.members.filter(user=self.request.user).exists():
            return Contribution.objects.none()
        
        return Contribution.objects.filter(group_id=group_id).select_related('user').order_by('-created_at')


class GroupPayoutsView(generics.ListAPIView):
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        # Ensure user is a member of the group
        group = get_object_or_404(ChamaGroup, id=group_id)
        if not group.members.filter(user=self.request.user).exists():
            return Payout.objects.none()
        
        return Payout.objects.filter(group_id=group_id).select_related('recipient').order_by('-scheduled_date')


class UserTransactionsView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related('group').order_by('-created_at')


class GroupStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(ChamaGroup, id=group_id)
        
        # Ensure user is a member or creator
        if not (group.created_by == request.user or 
                group.members.filter(user=request.user).exists()):
            return Response(
                {'error': 'You do not have access to this group'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculate stats
        total_contributions = group.contributions.filter(is_confirmed=True).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_members = group.members.count()
        completed_rounds = group.payouts.filter(is_completed=True).count()
        
        # Get next payout info
        next_payout = group.payouts.filter(is_completed=False).order_by('scheduled_date').first()
        next_payout_date = next_payout.scheduled_date if next_payout else None
        next_recipient = next_payout.recipient if next_payout else None
        
        stats_data = {
            'total_contributions': total_contributions,
            'total_members': total_members,
            'completed_rounds': completed_rounds,
            'next_payout_date': next_payout_date,
            'next_recipient': next_recipient
        }
        
        serializer = GroupStatsSerializer(stats_data)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get user's dashboard statistics"""
    user = request.user
    
    # User's groups
    user_groups = GroupMembership.objects.filter(user=user).count()
    
    # Total contributions made
    total_contributions = Contribution.objects.filter(
        user=user, is_confirmed=True
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Payouts received
    payouts_received = Payout.objects.filter(
        recipient=user, is_completed=True
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Pending payouts
    pending_payouts = Payout.objects.filter(
        recipient=user, is_completed=False
    ).count()
    
    return Response({
        'user_groups': user_groups,
        'total_contributions': total_contributions,
        'payouts_received': payouts_received,
        'pending_payouts': pending_payouts
    })
