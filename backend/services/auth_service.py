"""
Authentication service for user login and registration.
Handles password hashing, JWT token generation, and user validation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import JWTError, jwt
from database import db
from config import settings
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling user authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        # Ensure password is bytes and within bcrypt limits
        password_bytes = password.encode('utf-8')[:72]  # bcrypt limit is 72 bytes
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Ensure password is bytes and within bcrypt limits
            password_bytes = plain_password.encode('utf-8')[:72]
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password"""
        try:
            # Get user from database
            user = db.get_user_by_username(username)
            if not user:
                return None
            
            # Verify password
            if not AuthService.verify_password(password, user["password_hash"]):
                return None
            
            # Return user data without password hash
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"],
                "updated_at": user["updated_at"]
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def register_user(username: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Register a new user"""
        try:
            # Check if username already exists
            if db.get_user_by_username(username):
                return None
            
            # Check if email already exists
            if db.get_user_by_email(email):
                return None
            
            # Hash password
            password_hash = AuthService.hash_password(password)
            
            # Create user
            user = db.create_user(username, email, password_hash)
            if not user:
                return None
            
            # Return user data without password hash
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"],
                "updated_at": user["updated_at"]
            }
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return None
    
    @staticmethod
    def get_current_user(token: str) -> Optional[Dict[str, Any]]:
        """Get current user from JWT token"""
        try:
            payload = AuthService.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            return db.get_user_by_id(user_id)
            
        except Exception as e:
            logger.error(f"Get current user error: {e}")
            return None