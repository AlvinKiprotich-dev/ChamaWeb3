from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import User, EmailVerificationToken
import logging

logger = logging.getLogger(__name__)

def send_verification_email(user, token):
    """
    Send email verification email to user
    """
    try:
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={token.token}"
        
        subject = 'Verify your Chama account'
        
        # HTML email content
        html_message = f"""
        <html>
        <body>
            <h2>Welcome to Chama Platform!</h2>
            <p>Hi {user.first_name or user.username},</p>
            <p>Thank you for registering with Chama. Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email Address</a></p>
            <p>Or copy and paste this link in your browser:</p>
            <p>{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create this account, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The Chama Team</p>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Welcome to Chama Platform!
        
        Hi {user.first_name or user.username},
        
        Thank you for registering with Chama. Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The Chama Team
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False

def create_verification_token(user):
    """
    Create or get existing verification token for user
    """
    # Delete any existing unused tokens
    EmailVerificationToken.objects.filter(
        user=user, 
        is_used=False
    ).delete()
    
    # Create new token
    token = EmailVerificationToken.objects.create(user=user)
    return token

def resend_verification_email(user):
    """
    Resend verification email to user
    """
    if user.is_verified:
        return False, "User is already verified"
    
    token = create_verification_token(user)
    success = send_verification_email(user, token)
    
    if success:
        return True, "Verification email sent successfully"
    else:
        return False, "Failed to send verification email"
