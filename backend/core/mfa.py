"""
Multi-Factor Authentication (MFA) implementation
Supports TOTP, SMS, email, and biometric authentication methods
"""

import pyotp
import qrcode
import io
import base64
import secrets
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class MFAMethod(str, Enum):
    """Available MFA methods"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BIOMETRIC = "biometric"


class MFAStatus(str, Enum):
    """MFA verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class MFAManager:
    """Multi-Factor Authentication manager for enterprise security"""
    
    def __init__(self, settings):
        self.settings = settings
        self.pending_challenges: Dict[str, Dict] = {}
        self.user_mfa_configs: Dict[str, Dict] = {}  # In production, store in database
    
    async def setup_totp(self, user_id: str, user_email: str) -> Dict[str, Any]:
        """Setup TOTP authentication for user"""
        # Generate secret key
        secret = pyotp.random_base32()
        
        # Create TOTP instance
        totp = pyotp.TOTP(secret)
        
        # Generate provisioning URI for QR code
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=self.settings.app_name
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for frontend display
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Store user MFA config (in production, save to database)
        self.user_mfa_configs[user_id] = {
            "method": MFAMethod.TOTP,
            "secret": secret,
            "backup_codes": self._generate_backup_codes(),
            "setup_completed": False,
            "setup_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("TOTP setup initiated", user_id=user_id)
        
        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code_data}",
            "provisioning_uri": provisioning_uri,
            "backup_codes": self.user_mfa_configs[user_id]["backup_codes"]
        }
    
    async def verify_totp_setup(self, user_id: str, token: str) -> bool:
        """Verify TOTP setup with user-provided token"""
        if user_id not in self.user_mfa_configs:
            return False
        
        config = self.user_mfa_configs[user_id]
        if config["method"] != MFAMethod.TOTP:
            return False
        
        totp = pyotp.TOTP(config["secret"])
        is_valid = totp.verify(token, valid_window=1)
        
        if is_valid:
            # Mark setup as completed
            self.user_mfa_configs[user_id]["setup_completed"] = True
            logger.info("TOTP setup completed", user_id=user_id)
        else:
            logger.warning("TOTP setup verification failed", user_id=user_id)
        
        return is_valid
    
    async def initiate_mfa_challenge(self, user_id: str, method: MFAMethod, 
                                   contact_info: Optional[str] = None) -> Dict[str, Any]:
        """Initiate MFA challenge for user authentication"""
        challenge_id = secrets.token_hex(16)
        
        if method == MFAMethod.TOTP:
            return await self._initiate_totp_challenge(user_id, challenge_id)
        elif method == MFAMethod.SMS:
            return await self._initiate_sms_challenge(user_id, challenge_id, contact_info)
        elif method == MFAMethod.EMAIL:
            return await self._initiate_email_challenge(user_id, challenge_id, contact_info)
        elif method == MFAMethod.BIOMETRIC:
            return await self._initiate_biometric_challenge(user_id, challenge_id)
        else:
            raise ValueError(f"Unsupported MFA method: {method}")
    
    async def verify_mfa_challenge(self, challenge_id: str, response: str) -> Dict[str, Any]:
        """Verify MFA challenge response"""
        if challenge_id not in self.pending_challenges:
            return {"status": MFAStatus.FAILED, "message": "Invalid or expired challenge"}
        
        challenge = self.pending_challenges[challenge_id]
        
        # Check if challenge has expired
        if datetime.utcnow() > datetime.fromisoformat(challenge["expires_at"]):
            del self.pending_challenges[challenge_id]
            return {"status": MFAStatus.EXPIRED, "message": "Challenge expired"}
        
        method = challenge["method"]
        is_valid = False
        
        if method == MFAMethod.TOTP:
            is_valid = await self._verify_totp_response(challenge, response)
        elif method == MFAMethod.SMS:
            is_valid = await self._verify_sms_response(challenge, response)
        elif method == MFAMethod.EMAIL:
            is_valid = await self._verify_email_response(challenge, response)
        elif method == MFAMethod.BIOMETRIC:
            is_valid = await self._verify_biometric_response(challenge, response)
        
        # Clean up challenge
        del self.pending_challenges[challenge_id]
        
        if is_valid:
            logger.info("MFA challenge verified", user_id=challenge["user_id"], method=method)
            return {
                "status": MFAStatus.VERIFIED,
                "user_id": challenge["user_id"],
                "method": method
            }
        else:
            logger.warning("MFA challenge failed", user_id=challenge["user_id"], method=method)
            return {"status": MFAStatus.FAILED, "message": "Invalid verification code"}
    
    async def is_mfa_enabled(self, user_id: str) -> bool:
        """Check if MFA is enabled for user"""
        config = self.user_mfa_configs.get(user_id)
        return config is not None and config.get("setup_completed", False)
    
    async def get_user_mfa_methods(self, user_id: str) -> List[MFAMethod]:
        """Get available MFA methods for user"""
        if not await self.is_mfa_enabled(user_id):
            return []
        
        config = self.user_mfa_configs.get(user_id)
        if config:
            return [config["method"]]
        return []
    
    async def disable_mfa(self, user_id: str) -> bool:
        """Disable MFA for user"""
        if user_id in self.user_mfa_configs:
            del self.user_mfa_configs[user_id]
            logger.info("MFA disabled", user_id=user_id)
            return True
        return False
    
    def _generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    async def _initiate_totp_challenge(self, user_id: str, challenge_id: str) -> Dict[str, Any]:
        """Initiate TOTP challenge"""
        if user_id not in self.user_mfa_configs:
            raise ValueError("TOTP not configured for user")
        
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "method": MFAMethod.TOTP,
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.pending_challenges[challenge_id] = challenge
        
        return {
            "challenge_id": challenge_id,
            "method": MFAMethod.TOTP,
            "message": "Enter the 6-digit code from your authenticator app",
            "expires_in": 300  # 5 minutes
        }
    
    async def _initiate_sms_challenge(self, user_id: str, challenge_id: str, 
                                    phone_number: str) -> Dict[str, Any]:
        """Initiate SMS challenge"""
        # Generate 6-digit code
        code = f"{secrets.randbelow(900000) + 100000:06d}"
        
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "method": MFAMethod.SMS,
            "code": code,
            "phone_number": phone_number,
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.pending_challenges[challenge_id] = challenge
        
        # In production, integrate with SMS service (Twilio, AWS SNS, etc.)
        logger.info("SMS challenge initiated", user_id=user_id, phone=phone_number[:3] + "****")
        
        return {
            "challenge_id": challenge_id,
            "method": MFAMethod.SMS,
            "message": f"Verification code sent to {phone_number[:3]}****{phone_number[-2:]}",
            "expires_in": 300
        }
    
    async def _initiate_email_challenge(self, user_id: str, challenge_id: str, 
                                      email: str) -> Dict[str, Any]:
        """Initiate email challenge"""
        # Generate 6-digit code
        code = f"{secrets.randbelow(900000) + 100000:06d}"
        
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "method": MFAMethod.EMAIL,
            "code": code,
            "email": email,
            "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.pending_challenges[challenge_id] = challenge
        
        # In production, integrate with email service (SendGrid, AWS SES, etc.)
        logger.info("Email challenge initiated", user_id=user_id, email=email)
        
        return {
            "challenge_id": challenge_id,
            "method": MFAMethod.EMAIL,
            "message": f"Verification code sent to {email}",
            "expires_in": 600  # 10 minutes
        }
    
    async def _initiate_biometric_challenge(self, user_id: str, challenge_id: str) -> Dict[str, Any]:
        """Initiate biometric challenge"""
        # Generate challenge for biometric verification
        challenge_data = secrets.token_hex(32)
        
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "method": MFAMethod.BIOMETRIC,
            "challenge_data": challenge_data,
            "expires_at": (datetime.utcnow() + timedelta(minutes=2)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.pending_challenges[challenge_id] = challenge
        
        return {
            "challenge_id": challenge_id,
            "method": MFAMethod.BIOMETRIC,
            "challenge_data": challenge_data,
            "message": "Please provide biometric verification",
            "expires_in": 120  # 2 minutes
        }
    
    async def _verify_totp_response(self, challenge: Dict, response: str) -> bool:
        """Verify TOTP response"""
        user_id = challenge["user_id"]
        if user_id not in self.user_mfa_configs:
            return False
        
        config = self.user_mfa_configs[user_id]
        totp = pyotp.TOTP(config["secret"])
        
        # Check if it's a backup code
        if response.upper() in config.get("backup_codes", []):
            # Remove used backup code
            config["backup_codes"].remove(response.upper())
            return True
        
        # Verify TOTP token
        return totp.verify(response, valid_window=1)
    
    async def _verify_sms_response(self, challenge: Dict, response: str) -> bool:
        """Verify SMS response"""
        return challenge.get("code") == response
    
    async def _verify_email_response(self, challenge: Dict, response: str) -> bool:
        """Verify email response"""
        return challenge.get("code") == response
    
    async def _verify_biometric_response(self, challenge: Dict, response: str) -> bool:
        """Verify biometric response"""
        # In production, integrate with biometric verification service
        # This is a simplified implementation
        expected_response = challenge.get("challenge_data")
        return response == expected_response