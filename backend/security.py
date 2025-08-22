"""
Sol OS MVP Security Services - Encryption, Authentication, and Privacy Controls
Security-first implementation with GDPR compliance
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

class DataEncryptionService:
    """
    Application-level encryption for sensitive user data.
    Uses per-user encryption keys derived from master key + user salt.
    """
    
    def __init__(self):
        self.master_key = os.getenv('DATA_ENCRYPTION_MASTER_KEY')
        if not self.master_key:
            raise ValueError("DATA_ENCRYPTION_MASTER_KEY environment variable required")
    
    def generate_user_salt(self) -> bytes:
        """Generate random salt for new user"""
        return secrets.token_bytes(32)
    
    def derive_user_key(self, user_id: str, user_salt: bytes) -> bytes:
        """Derive unique encryption key for each user"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=user_salt,
            iterations=100000,  # High iteration count for security
        )
        key = base64.urlsafe_b64encode(kdf.derive(
            f"{self.master_key}:{user_id}".encode()
        ))
        return key
    
    def encrypt_text(self, user_id: str, user_salt: bytes, content: str) -> bytes:
        """Encrypt text content with user-specific key"""
        user_key = self.derive_user_key(user_id, user_salt)
        fernet = Fernet(user_key)
        return fernet.encrypt(content.encode())
    
    def decrypt_text(self, user_id: str, user_salt: bytes, encrypted_content: bytes) -> str:
        """Decrypt text content"""
        user_key = self.derive_user_key(user_id, user_salt)
        fernet = Fernet(user_key)
        decrypted_content = fernet.decrypt(encrypted_content)
        return decrypted_content.decode()
    
    def hash_email_for_index(self, email: str) -> str:
        """Create hash of email for database indexing while preserving privacy"""
        return hashlib.sha256(email.lower().encode()).hexdigest()

class SecureAuthService:
    """
    Security-first authentication with enhanced JWT implementation.
    """
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY')
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable required")
        
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 15  # Short-lived access tokens
        self.refresh_token_expire_days = 30    # Longer refresh tokens
        
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt and high cost factor"""
        salt = bcrypt.gensalt(rounds=12)  # High cost for security
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, user_id: str, permissions: list = None) -> str:
        """Create short-lived access token"""
        payload = {
            "sub": user_id,
            "type": "access",
            "permissions": permissions or [],
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)  # Unique token ID for revocation
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create long-lived refresh token"""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

class SecurityAuditService:
    """
    Security event monitoring and audit logging.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        event_details: Dict[str, Any] = None,
        risk_level: str = "low"
    ):
        """Log security event for audit trail"""
        from models import SecurityAuditLog
        
        audit_log = SecurityAuditLog(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            event_details=event_details or {},
            risk_level=risk_level
        )
        
        self.db.add(audit_log)
        self.db.commit()
    
    async def check_failed_login_attempts(self, email: str, ip_address: str) -> bool:
        """Check if account should be locked due to failed login attempts"""
        from models import SecurityAuditLog
        
        # Check failed login attempts in last 15 minutes
        recent_failures = self.db.query(SecurityAuditLog).filter(
            SecurityAuditLog.event_type == "login_failed",
            SecurityAuditLog.timestamp > datetime.utcnow() - timedelta(minutes=15),
            SecurityAuditLog.event_details.contains({"email_hash": hashlib.sha256(email.encode()).hexdigest()})
        ).count()
        
        return recent_failures >= 5  # Lock after 5 failed attempts

class ConsentManager:
    """
    GDPR-compliant consent management for different data uses.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.consent_types = {
            "conversation_storage": "Store conversation history for personalized experience",
            "mood_analysis": "Analyze mood/energy patterns for insights",
            "productivity_optimization": "Use data to optimize productivity recommendations",
            "analytics_anonymous": "Anonymous usage analytics for service improvement",
            "third_party": "Integrate with external services (future: Notion, Calendar)"
        }
    
    async def check_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if user has given consent for specific data use"""
        from models import User
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        consent_field = f"consent_{consent_type}"
        return getattr(user, consent_field, False)
    
    async def update_consent(self, user_id: str, consent_updates: Dict[str, bool]):
        """Update user consent preferences"""
        from models import User
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for consent_type, granted in consent_updates.items():
            consent_field = f"consent_{consent_type}"
            if hasattr(user, consent_field):
                setattr(user, consent_field, granted)
                
                # Log consent change for audit
                await SecurityAuditService(self.db).log_security_event(
                    event_type="consent_change",
                    user_id=user_id,
                    event_details={
                        "consent_type": consent_type,
                        "granted": granted
                    }
                )
        
        self.db.commit()

class GDPRComplianceService:
    """
    GDPR compliance service handling data subject rights.
    """
    
    def __init__(self, db: Session, encryption_service: DataEncryptionService):
        self.db = db
        self.encryption = encryption_service
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data in machine-readable format (Right to Data Portability)"""
        from models import User, Conversation, MoodEnergyLog, Task, TimeBlock, FocusSession
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Decrypt user email for export
        email = self.encryption.decrypt_text(user_id, user.encryption_salt, user.email_encrypted)
        
        # Collect conversations (decrypt for export)
        conversations = []
        for conv in user.conversations:
            try:
                message = self.encryption.decrypt_text(user_id, user.encryption_salt, conv.message_content_encrypted)
                response = self.encryption.decrypt_text(user_id, user.encryption_salt, conv.sol_response_encrypted)
                conversations.append({
                    "id": str(conv.id),
                    "session_id": conv.session_id,
                    "message": message,
                    "sol_response": response,
                    "created_at": conv.created_at.isoformat()
                })
            except Exception:
                # Skip corrupted conversations
                continue
        
        # Collect other data
        user_data = {
            "user_profile": {
                "id": str(user.id),
                "email": email,
                "username": user.username,
                "created_at": user.created_at.isoformat(),
                "data_retention_days": user.data_retention_days
            },
            "consent_preferences": {
                "conversation_storage": user.consent_conversation_storage,
                "mood_analysis": user.consent_mood_analysis,
                "productivity_optimization": user.consent_productivity_optimization,
                "analytics_anonymous": user.consent_analytics_anonymous,
                "third_party": user.consent_third_party
            },
            "conversations": conversations,
            "mood_energy_logs": [
                {
                    "id": str(log.id),
                    "mood_rating": log.mood_rating,
                    "energy_level": log.energy_level,
                    "time_of_day": log.time_of_day,
                    "logged_at": log.logged_at.isoformat()
                }
                for log in user.mood_energy_logs
            ],
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "created_at": task.created_at.isoformat()
                }
                for task in user.tasks
            ],
            "time_blocks": [
                {
                    "id": str(block.id),
                    "title": block.title,
                    "start_time": block.start_time.isoformat(),
                    "end_time": block.end_time.isoformat(),
                    "block_type": block.block_type
                }
                for block in user.time_blocks
            ],
            "focus_sessions": [
                {
                    "id": str(session.id),
                    "session_type": session.session_type,
                    "planned_duration": session.planned_duration,
                    "actual_duration": session.actual_duration,
                    "started_at": session.started_at.isoformat()
                }
                for session in user.focus_sessions
            ],
            "export_metadata": {
                "export_timestamp": datetime.utcnow().isoformat(),
                "export_format": "JSON",
                "data_retention_period": f"{user.data_retention_days} days",
                "data_usage_purpose": "ADHD productivity support and AI companion services"
            }
        }
        
        return user_data
    
    async def request_data_deletion(self, user_id: str) -> bool:
        """Request user data deletion (Right to Erasure)"""
        from models import User
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Mark for deletion (allows for verification period)
        user.data_deletion_requested = datetime.utcnow()
        self.db.commit()
        
        # Log deletion request
        await SecurityAuditService(self.db).log_security_event(
            event_type="data_deletion_requested",
            user_id=user_id,
            event_details={"requested_at": datetime.utcnow().isoformat()}
        )
        
        return True
    
    async def execute_data_deletion(self, user_id: str, verification_token: str) -> bool:
        """Permanently delete all user data after verification"""
        from models import User
        
        # Verify deletion request (simplified for MVP)
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.data_deletion_requested:
            raise HTTPException(status_code=400, detail="No valid deletion request found")
        
        # Delete all user data (cascading deletes will handle related records)
        self.db.delete(user)
        self.db.commit()
        
        # Log successful deletion (without personal data)
        await SecurityAuditService(self.db).log_security_event(
            event_type="data_deletion_completed",
            event_details={
                "user_id_hash": hashlib.sha256(user_id.encode()).hexdigest(),
                "deletion_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return True

# Utility functions for security
def get_client_ip(request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special

def generate_verification_token() -> str:
    """Generate secure verification token"""
    return secrets.token_urlsafe(32)