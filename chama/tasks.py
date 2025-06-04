import logging
from datetime import datetime, timedelta
from decimal import Decimal
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from .models import ChamaGroup, GroupMembership, Contribution, Payout, Transaction
from .web3_utils import verify_contribution_transaction, send_payout_transaction, get_transaction_details

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def verify_blockchain_transaction(self, contribution_id):
    """Verify a contribution transaction on the blockchain"""
    try:
        contribution = Contribution.objects.get(id=contribution_id)
        
        if contribution.is_confirmed:
            logger.info(f"Contribution {contribution_id} already confirmed")
            return
        
        # Verify transaction on blockchain
        verification_result = verify_contribution_transaction(
            contribution.transaction_hash,
            contribution.amount,
            contribution.group.smart_contract_address or settings.CHAMA_CONTRACT_ADDRESS
        )
        
        if verification_result['is_valid']:
            # Update contribution as confirmed
            contribution.is_confirmed = True
            contribution.block_number = verification_result.get('block_number')
            contribution.gas_used = verification_result.get('gas_used')
            contribution.save()
            
            # Update user's total contributions
            membership = GroupMembership.objects.get(
                user=contribution.user, 
                group=contribution.group
            )
            membership.total_contributions += contribution.amount
            membership.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=contribution.user,
                group=contribution.group,
                transaction_type='CONTRIBUTION',
                amount=contribution.amount,
                transaction_hash=contribution.transaction_hash,
                block_number=verification_result.get('block_number'),
                gas_used=verification_result.get('gas_used'),
                status='CONFIRMED'
            )
            
            logger.info(f"Contribution {contribution_id} verified and confirmed")
            
            # Check if all members have contributed for this round
            check_round_completion.delay(contribution.group.id)
            
        else:
            logger.warning(f"Contribution {contribution_id} verification failed: {verification_result.get('errors')}")
            # Retry after some time
            raise Exception(f"Transaction verification failed: {verification_result.get('errors')}")
            
    except Contribution.DoesNotExist:
        logger.error(f"Contribution {contribution_id} not found")
    except Exception as exc:
        logger.error(f"Error verifying contribution {contribution_id}: {exc}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def check_round_completion(group_id):
    """Check if a contribution round is complete and schedule next payout"""
    try:
        group = ChamaGroup.objects.get(id=group_id)
        
        # Get all active members
        active_members = group.members.all()
        total_members = active_members.count()
        
        if total_members == 0:
            return
        
        # Check contributions for current round
        # Get last payout date or group start date
        last_payout = group.payouts.filter(is_completed=True).order_by('-actual_date').first()
        round_start_date = last_payout.actual_date if last_payout else group.start_date
        
        # Count confirmed contributions since last payout
        contributions_this_round = group.contributions.filter(
            created_at__gt=round_start_date,
            is_confirmed=True
        ).values('user').distinct().count()
        
        # If all members have contributed, schedule next payout
        if contributions_this_round >= total_members:
            schedule_next_payout.delay(group_id)
            
    except ChamaGroup.DoesNotExist:
        logger.error(f"Group {group_id} not found")
    except Exception as e:
        logger.error(f"Error checking round completion for group {group_id}: {e}")


@shared_task
def schedule_next_payout(group_id):
    """Schedule the next payout for a group"""
    try:
        with transaction.atomic():
            group = ChamaGroup.objects.get(id=group_id)
            
            # Get next recipient based on rotation
            last_payout = group.payouts.filter(is_completed=True).order_by('-actual_date').first()
            
            if last_payout:
                # Find next person in rotation
                next_position = (last_payout.recipient.groupmembership_set.get(group=group).position_in_rotation % 
                               group.members.count()) + 1
            else:
                # First payout goes to position 1
                next_position = 1
            
            # Get recipient
            try:
                recipient_membership = group.members.get(position_in_rotation=next_position)
                recipient = recipient_membership.user
            except GroupMembership.DoesNotExist:
                # Fallback to first available member
                recipient_membership = group.members.order_by('position_in_rotation').first()
                recipient = recipient_membership.user
              # Calculate payout amount (total contributions since last payout minus any fees)
            last_payout_date = last_payout.actual_date if last_payout else group.start_date
            total_amount = group.contributions.filter(
                created_at__gt=last_payout_date,
                is_confirmed=True
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # Create payout record
            payout = Payout.objects.create(
                group=group,
                recipient=recipient,
                amount=total_amount,
                scheduled_date=timezone.now() + timedelta(days=1)  # Schedule for next day
            )
            
            logger.info(f"Scheduled payout {payout.id} for group {group_id}")
            
            # Schedule the actual payout execution
            execute_payout.apply_async(
                args=[payout.id],
                eta=payout.scheduled_date
            )
            
            # Send notification
            send_payout_notification.delay(payout.id)
            
    except ChamaGroup.DoesNotExist:
        logger.error(f"Group {group_id} not found")
    except Exception as e:
        logger.error(f"Error scheduling payout for group {group_id}: {e}")


@shared_task(bind=True, max_retries=3)
def execute_payout(self, payout_id):
    """Execute a scheduled payout"""
    try:
        payout = Payout.objects.get(id=payout_id)
        
        if payout.is_completed:
            logger.info(f"Payout {payout_id} already completed")
            return
        
        # Send transaction to blockchain
        tx_hash = send_payout_transaction(
            payout.recipient.wallet_address,
            payout.amount
        )
        
        if tx_hash:
            # Update payout record
            payout.transaction_hash = tx_hash
            payout.actual_date = timezone.now()
            payout.save()
            
            # Verify transaction in background
            verify_payout_transaction.delay(payout_id)
            
            logger.info(f"Payout {payout_id} transaction sent: {tx_hash}")
        else:
            logger.error(f"Failed to send payout transaction for {payout_id}")
            # Retry
            raise Exception("Failed to send payout transaction")
            
    except Payout.DoesNotExist:
        logger.error(f"Payout {payout_id} not found")
    except Exception as exc:
        logger.error(f"Error executing payout {payout_id}: {exc}")
        # Retry the task
        raise self.retry(exc=exc, countdown=300 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=5)
def verify_payout_transaction(self, payout_id):
    """Verify a payout transaction on the blockchain"""
    try:
        payout = Payout.objects.get(id=payout_id)
        
        if not payout.transaction_hash:
            logger.error(f"Payout {payout_id} has no transaction hash")
            return
        
        # Get transaction details
        tx_details = get_transaction_details(payout.transaction_hash)
        
        if tx_details and tx_details.get('status') == 1:
            # Transaction successful
            payout.is_completed = True
            payout.block_number = tx_details.get('blockNumber')
            payout.gas_used = tx_details.get('gasUsed')
            payout.save()
            
            # Update recipient's payout status
            membership = GroupMembership.objects.get(
                user=payout.recipient,
                group=payout.group
            )
            membership.has_received_payout = True
            membership.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=payout.recipient,
                group=payout.group,
                transaction_type='PAYOUT',
                amount=payout.amount,
                transaction_hash=payout.transaction_hash,
                block_number=payout.block_number,
                gas_used=payout.gas_used,
                status='CONFIRMED'
            )
            
            logger.info(f"Payout {payout_id} verified and completed")
            
            # Send completion notification
            send_payout_completion_notification.delay(payout_id)
            
        elif tx_details:
            # Transaction failed
            logger.error(f"Payout transaction {payout.transaction_hash} failed")
            payout.is_completed = False
            payout.save()
        else:
            # Transaction not yet mined, retry
            logger.info(f"Payout transaction {payout.transaction_hash} not yet mined, retrying...")
            raise Exception("Transaction not yet mined")
            
    except Payout.DoesNotExist:
        logger.error(f"Payout {payout_id} not found")
    except Exception as exc:
        logger.error(f"Error verifying payout {payout_id}: {exc}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def send_payout_notification(payout_id):
    """Send notification about scheduled payout"""
    try:
        payout = Payout.objects.get(id=payout_id)
        
        # Send email notification
        if payout.recipient.email:
            send_mail(
                subject=f'Chama Payout Scheduled - {payout.group.name}',
                message=f'''
                Hello {payout.recipient.first_name},
                
                Your payout from "{payout.group.name}" has been scheduled.
                
                Amount: {payout.amount} AVAX
                Scheduled Date: {payout.scheduled_date}
                
                You will receive another notification once the payout is completed.
                
                Best regards,
                Chama Platform Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[payout.recipient.email],
                fail_silently=True
            )
        
        logger.info(f"Payout notification sent for {payout_id}")
        
    except Payout.DoesNotExist:
        logger.error(f"Payout {payout_id} not found")
    except Exception as e:
        logger.error(f"Error sending payout notification for {payout_id}: {e}")


@shared_task
def send_payout_completion_notification(payout_id):
    """Send notification about completed payout"""
    try:
        payout = Payout.objects.get(id=payout_id)
        
        # Send email notification
        if payout.recipient.email:
            send_mail(
                subject=f'Chama Payout Completed - {payout.group.name}',
                message=f'''
                Hello {payout.recipient.first_name},
                
                Your payout from "{payout.group.name}" has been completed successfully!
                
                Amount: {payout.amount} AVAX
                Transaction Hash: {payout.transaction_hash}
                Completed On: {payout.actual_date}
                
                You can view the transaction on the Avalanche explorer.
                
                Best regards,
                Chama Platform Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[payout.recipient.email],
                fail_silently=True
            )
        
        logger.info(f"Payout completion notification sent for {payout_id}")
        
    except Payout.DoesNotExist:
        logger.error(f"Payout {payout_id} not found")
    except Exception as e:
        logger.error(f"Error sending payout completion notification for {payout_id}: {e}")


@shared_task
def send_contribution_reminder():
    """Send reminders to users who haven't contributed in current round"""
    try:
        # Get all active groups
        active_groups = ChamaGroup.objects.filter(is_active=True)
        
        for group in active_groups:
            # Get last payout date
            last_payout = group.payouts.filter(is_completed=True).order_by('-actual_date').first()
            round_start_date = last_payout.actual_date if last_payout else group.start_date
            
            # Get members who haven't contributed this round
            contributed_users = group.contributions.filter(
                created_at__gt=round_start_date,
                is_confirmed=True
            ).values_list('user', flat=True)
            
            pending_members = group.members.exclude(user__in=contributed_users)
            
            for membership in pending_members:
                user = membership.user
                if user.email:
                    send_mail(
                        subject=f'Contribution Reminder - {group.name}',
                        message=f'''
                        Hello {user.first_name},
                        
                        This is a friendly reminder that your contribution to "{group.name}" is due.
                        
                        Contribution Amount: {group.contribution_amount} AVAX
                        
                        Please make your contribution to keep the group active.
                        
                        Best regards,
                        Chama Platform Team
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True
                    )
        
        logger.info("Contribution reminders sent")
        
    except Exception as e:
        logger.error(f"Error sending contribution reminders: {e}")


# Periodic task to clean up old unconfirmed contributions
@shared_task
def cleanup_unconfirmed_contributions():
    """Clean up old unconfirmed contributions"""
    try:
        # Delete contributions older than 24 hours that are not confirmed
        cutoff_date = timezone.now() - timedelta(hours=24)
        deleted_count = Contribution.objects.filter(
            created_at__lt=cutoff_date,
            is_confirmed=False
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} unconfirmed contributions")
        
    except Exception as e:
        logger.error(f"Error cleaning up unconfirmed contributions: {e}")
