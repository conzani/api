import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from_email = settings.SMTP_FROM_EMAIL
        self.smtp_from_name = settings.SMTP_FROM_NAME
        self.smtp_use_tls = settings.SMTP_USE_TLS

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email using SMTP."""
        # Check if SMTP is configured
        if not self.smtp_host or not self.smtp_user or not self.smtp_password:
            print(f"[DEV MODE] Email not sent - SMTP not configured")
            print(f"[DEV MODE] To: {to_email}")
            print(f"[DEV MODE] Subject: {subject}")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            message["To"] = to_email
            message["Subject"] = subject

            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Connect to SMTP server
            # Port 465 uses SSL (SMTP_SSL), Port 587 uses STARTTLS
            if self.smtp_port == 465:
                # Use SSL for port 465
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context, timeout=10) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)
            else:
                # Use STARTTLS for other ports (e.g., 587)
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    if self.smtp_use_tls:
                        server.starttls(timeout=10)
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)

            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_verification_email(
        self,
        to_email: str,
        verification_code: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send a verification email with a 6-digit code."""
        subject = "Verify Your Email Address"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0066cc;">Email Verification</h2>
                <p>Hello{f' {user_name}' if user_name else ''},</p>
                <p>Thank you for registering with {settings.APP_NAME}. Please use the following verification code to verify your email address:</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #0066cc;">
                        {verification_code}
                    </span>
                </div>
                
                <p>This code will expire in {settings.VERIFICATION_CODE_EXPIRE_MINUTES} minutes.</p>
                <p>If you did not request this verification, please ignore this email.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated email from {settings.APP_NAME}. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Email Verification
        
        Hello{f' {user_name}' if user_name else ''},
        
        Thank you for registering with {settings.APP_NAME}. Please use the following verification code to verify your email address:
        
        Verification Code: {verification_code}
        
        This code will expire in {settings.VERIFICATION_CODE_EXPIRE_MINUTES} minutes.
        
        If you did not request this verification, please ignore this email.
        
        ---
        This is an automated email from {settings.APP_NAME}. Please do not reply.
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_password_reset_email(
        self,
        to_email: str,
        reset_code: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send a password reset email with a 6-digit code."""
        subject = "Password Reset Request"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #cc6600;">Password Reset</h2>
                <p>Hello{f' {user_name}' if user_name else ''},</p>
                <p>We received a request to reset your password for {settings.APP_NAME}. Please use the following code to reset your password:</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #cc6600;">
                        {reset_code}
                    </span>
                </div>
                
                <p>This code will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours.</p>
                <p>If you did not request this password reset, please ignore this email and your password will remain unchanged.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated email from {settings.APP_NAME}. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset
        
        Hello{f' {user_name}' if user_name else ''},
        
        We received a request to reset your password for {settings.APP_NAME}. Please use the following code to reset your password:
        
        Reset Code: {reset_code}
        
        This code will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours.
        
        If you did not request this password reset, please ignore this email and your password will remain unchanged.
        
        ---
        This is an automated email from {settings.APP_NAME}. Please do not reply.
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_invitation_email(
        self,
        to_email: str,
        business_name: str,
        role_name: str,
        invitation_code: str,
        inviter_name: Optional[str] = None,
    ) -> bool:
        """Send a business invitation email."""
        subject = f"Invitation to join {business_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #009933;">You're Invited!</h2>
                <p>Hello,</p>
                <p>{f'{inviter_name} has' if inviter_name else 'You have'} invited you to join <strong>{business_name}</strong> on {settings.APP_NAME} as a <strong>{role_name}</strong>.</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #009933;">
                        {invitation_code}
                    </span>
                </div>
                
                <p>Use this invitation code to accept the invitation and join the team.</p>
                <p>This invitation will expire in 7 days.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated email from {settings.APP_NAME}. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        You're Invited!
        
        Hello,
        
        {f'{inviter_name} has' if inviter_name else 'You have'} invited you to join {business_name} on {settings.APP_NAME} as a {role_name}.
        
        Invitation Code: {invitation_code}
        
        Use this invitation code to accept the invitation and join the team.
        This invitation will expire in 7 days.
        
        ---
        This is an automated email from {settings.APP_NAME}. Please do not reply.
        """

        return self.send_email(to_email, subject, html_content, text_content)


# Global email service instance
email_service = EmailService()
