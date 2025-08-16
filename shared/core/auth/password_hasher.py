"""
Password Hasher - Universal Knowledge Platform

This module provides secure password hashing and verification using bcrypt.
Features:
- Secure password hashing with salt
- Password verification
- Configurable work factor
- Password strength validation
- Secure random salt generation

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import re
import secrets
from typing import Optional
import bcrypt

import structlog

logger = structlog.get_logger(__name__)


class PasswordHasher:
    """
    Secure password hashing and verification utility.
    
    Uses bcrypt for secure password hashing with:
    - Automatic salt generation
    - Configurable work factor
    - Constant-time comparison
    - Protection against timing attacks
    """

    def __init__(self, work_factor: int = 12):
        """
        Initialize the password hasher.
        
        Args:
            work_factor: bcrypt work factor (default: 12, range: 4-31)
                        Higher values = more secure but slower
        """
        self.work_factor = max(4, min(31, work_factor))
        logger.info(f"Password hasher initialized with work factor: {self.work_factor}")

    def hash_password(self, password: str) -> str:
        """
        Hash a password securely.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
            
        Raises:
            ValueError: If password is empty or invalid
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string")

        # Validate password strength
        self._validate_password_strength(password)

        try:
            # Encode password to bytes
            password_bytes = password.encode('utf-8')
            
            # Generate salt and hash password
            salt = bcrypt.gensalt(rounds=self.work_factor)
            hashed = bcrypt.hashpw(password_bytes, salt)
            
            # Return as string
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError("Failed to hash password")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Hashed password to check against
            
        Returns:
            True if password matches, False otherwise
        """
        if not password or not hashed_password:
            return False

        try:
            # Encode both to bytes
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            
            # Verify password
            return bcrypt.checkpw(password_bytes, hashed_bytes)
            
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    def _validate_password_strength(self, password: str) -> None:
        """
        Validate password strength requirements.
        
        Args:
            password: Password to validate
            
        Raises:
            ValueError: If password doesn't meet strength requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(password) > 128:
            raise ValueError("Password must be no more than 128 characters long")

        # Check for common weak patterns
        if self._is_common_password(password):
            raise ValueError("Password is too common or weak")

        # Optional: Add more strength requirements
        # if not re.search(r'[A-Z]', password):
        #     raise ValueError("Password must contain at least one uppercase letter")
        # if not re.search(r'[a-z]', password):
        #     raise ValueError("Password must contain at least one lowercase letter")
        # if not re.search(r'\d', password):
        #     raise ValueError("Password must contain at least one digit")
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        #     raise ValueError("Password must contain at least one special character")

    def _is_common_password(self, password: str) -> bool:
        """
        Check if password is a common weak password.
        
        Args:
            password: Password to check
            
        Returns:
            True if password is common/weak, False otherwise
        """
        # Common weak passwords (in practice, this would be a much larger list)
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'hello', 'freedom', 'whatever',
            'qwerty123', 'trustno1', 'jordan', 'harley', 'ranger',
            'iwantu', 'jennifer', 'hunter', 'buster', 'soccer',
            'baseball', 'television', 'charlie', 'andrew', 'michelle',
            'love', 'sunshine', 'jessica', 'asshole', '696969',
            'amanda', 'apple', 'fuckme', 'tiger', 'shadow',
            'mother', 'monkey', 'master', 'jordan', 'harley',
            'ranger', 'iwantu', 'jennifer', 'hunter', 'buster',
            'soccer', 'baseball', 'television', 'charlie', 'andrew',
            'michelle', 'love', 'sunshine', 'jessica', 'asshole',
            '696969', 'amanda', 'apple', 'fuckme', 'tiger',
            'shadow', 'mother', 'monkey', 'master', 'jordan'
        }
        
        return password.lower() in common_passwords

    def generate_secure_password(self, length: int = 16) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Length of password to generate (default: 16)
            
        Returns:
            Secure random password string
        """
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")

        # Character sets
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?'

        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]

        # Fill remaining length with random characters
        all_chars = lowercase + uppercase + digits + symbols
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list)

    def get_password_strength_score(self, password: str) -> int:
        """
        Calculate password strength score (0-100).
        
        Args:
            password: Password to score
            
        Returns:
            Strength score from 0 to 100
        """
        if not password:
            return 0

        score = 0

        # Length bonus
        if len(password) >= 8:
            score += 10
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10

        # Character variety bonus
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10

        # Complexity bonus
        if len(set(password)) >= len(password) * 0.8:
            score += 10  # Good character variety

        # Penalty for common patterns
        if self._is_common_password(password):
            score -= 30

        # Penalty for sequential characters
        if re.search(r'(.)\1{2,}', password):
            score -= 10  # Repeated characters

        # Penalty for keyboard patterns
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', '123456']
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                score -= 20

        return max(0, min(100, score))

    def get_password_strength_label(self, password: str) -> str:
        """
        Get human-readable password strength label.
        
        Args:
            password: Password to evaluate
            
        Returns:
            Strength label: 'Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'
        """
        score = self.get_password_strength_score(password)
        
        if score < 20:
            return 'Very Weak'
        elif score < 40:
            return 'Weak'
        elif score < 60:
            return 'Fair'
        elif score < 80:
            return 'Good'
        elif score < 90:
            return 'Strong'
        else:
            return 'Very Strong'


# Global password hasher instance
_password_hasher: Optional[PasswordHasher] = None


def get_password_hasher() -> PasswordHasher:
    """Get the global password hasher instance."""
    global _password_hasher
    if _password_hasher is None:
        _password_hasher = PasswordHasher()
    return _password_hasher


# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password using the global password hasher."""
    return get_password_hasher().hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password using the global password hasher."""
    return get_password_hasher().verify_password(password, hashed_password)


def generate_secure_password(length: int = 16) -> str:
    """Generate a secure random password using the global password hasher."""
    return get_password_hasher().generate_secure_password(length)


def get_password_strength_score(password: str) -> int:
    """Get password strength score using the global password hasher."""
    return get_password_hasher().get_password_strength_score(password)


def get_password_strength_label(password: str) -> str:
    """Get password strength label using the global password hasher."""
    return get_password_hasher().get_password_strength_label(password)


# Export classes and functions
__all__ = [
    "PasswordHasher",
    "get_password_hasher",
    "hash_password",
    "verify_password",
    "generate_secure_password",
    "get_password_strength_score",
    "get_password_strength_label",
]
