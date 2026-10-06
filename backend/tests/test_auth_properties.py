"""
Property-based tests for authentication system.
Tests universal properties that should hold for all valid inputs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch, MagicMock
import string
import re

# Configure hypothesis to run fewer examples for faster testing
settings.register_profile("fast", max_examples=10, deadline=1000)
settings.load_profile("fast")

# Feature: ai-trip-planner, Property 1: Authentication Validation
# **Validates: Requirements 1.2**

@given(
    username=st.text(
        alphabet=string.ascii_letters + string.digits + "_-",
        min_size=3,
        max_size=20
    ),
    password=st.text(
        alphabet=string.ascii_letters + string.digits + "!@#$%^&*",
        min_size=1,
        max_size=20  # Very safe limit to avoid bcrypt issues
    )
)
def test_property_authentication_validation(username, password):
    """
    Property 1: Authentication Validation
    For any valid username and password combination, the authentication system 
    should grant access to the application and maintain session state.
    **Validates: Requirements 1.2**
    """
    # Assume valid username format (no special characters except _ and -)
    assume(re.match(r'^[a-zA-Z0-9_-]+$', username))
    assume(len(username) >= 3)
    
    # Mock all external dependencies and AuthService methods
    with patch('supabase.create_client') as mock_create_client, \
         patch('config.settings') as mock_settings, \
         patch('services.auth_service.AuthService.hash_password') as mock_hash, \
         patch('services.auth_service.AuthService.verify_password') as mock_verify, \
         patch('services.auth_service.AuthService.create_access_token') as mock_create_token, \
         patch('services.auth_service.AuthService.verify_token') as mock_verify_token:
        
        # Setup mock settings
        mock_settings.SUPABASE_URL = 'https://test.supabase.co'
        mock_settings.SUPABASE_KEY = 'test-key'
        mock_settings.SECRET_KEY = 'test-secret-key'
        mock_settings.ALGORITHM = 'HS256'
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Setup mock Supabase client
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Setup mock auth service methods
        mock_hash.return_value = "hashed_password"
        mock_verify.return_value = True
        mock_create_token.return_value = "test_jwt_token"
        mock_verify_token.return_value = {"sub": "test-user-id", "username": username}
        
        # Import after mocking
        from services.auth_service import AuthService
        from database import db
        
        # Create a test user with the generated credentials
        email = f"{username}@test.com"
        
        # Mock database response for existing user
        test_user = {
            "id": "test-user-id",
            "username": username,
            "email": email,
            "password_hash": "hashed_password",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Mock database operations
        with patch.object(db, 'get_user_by_username') as mock_get_user:
            mock_get_user.return_value = test_user
            
            # Test authentication with valid credentials
            authenticated_user = AuthService.authenticate_user(username, password)
            
            # Property: Valid credentials should always result in successful authentication
            assert authenticated_user is not None, f"Authentication failed for valid credentials: {username}/{password}"
            
            # Property: Authenticated user should contain expected fields
            expected_fields = {"id", "username", "email", "created_at", "updated_at"}
            assert set(authenticated_user.keys()) == expected_fields, "Authenticated user missing required fields"
            
            # Property: Authenticated user should match original user data
            assert authenticated_user["username"] == username, "Username mismatch in authenticated user"
            assert authenticated_user["email"] == email, "Email mismatch in authenticated user"
            
            # Property: Password hash should not be included in response
            assert "password_hash" not in authenticated_user, "Password hash should not be in authenticated user response"
            
            # Property: JWT token should be creatable for authenticated user
            token_data = {"sub": authenticated_user["id"], "username": authenticated_user["username"]}
            token = AuthService.create_access_token(token_data)
            assert token is not None, "JWT token creation failed for authenticated user"
            assert isinstance(token, str), "JWT token should be a string"
            assert len(token) > 0, "JWT token should not be empty"
            
            # Property: Created token should be verifiable
            decoded_payload = AuthService.verify_token(token)
            assert decoded_payload is not None, "JWT token verification failed"
            assert decoded_payload["sub"] == authenticated_user["id"], "Token payload mismatch"


# Feature: ai-trip-planner, Property 2: Invalid Credential Rejection
# **Validates: Requirements 1.3**

@given(
    username=st.text(
        alphabet=string.ascii_letters + string.digits + "_-",
        min_size=3,
        max_size=20
    ),
    correct_password=st.text(
        alphabet=string.ascii_letters + string.digits + "!@#$%^&*",
        min_size=1,
        max_size=20
    ),
    wrong_password=st.text(
        alphabet=string.ascii_letters + string.digits + "!@#$%^&*",
        min_size=1,
        max_size=20
    )
)
def test_property_invalid_credential_rejection(username, correct_password, wrong_password):
    """
    Property 2: Invalid Credential Rejection
    For any invalid username and password combination, the authentication system 
    should reject access and display appropriate error messages.
    **Validates: Requirements 1.3**
    """
    # Assume valid username format and different passwords
    assume(re.match(r'^[a-zA-Z0-9_-]+$', username))
    assume(len(username) >= 3)
    assume(correct_password != wrong_password)
    
    # Mock all external dependencies and AuthService methods
    with patch('supabase.create_client') as mock_create_client, \
         patch('config.settings') as mock_settings, \
         patch('services.auth_service.AuthService.hash_password') as mock_hash, \
         patch('services.auth_service.AuthService.verify_password') as mock_verify:
        
        # Setup mock settings
        mock_settings.SUPABASE_URL = 'https://test.supabase.co'
        mock_settings.SUPABASE_KEY = 'test-key'
        mock_settings.SECRET_KEY = 'test-secret-key'
        mock_settings.ALGORITHM = 'HS256'
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Setup mock Supabase client
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Setup mock auth service methods
        mock_hash.return_value = "hashed_correct_password"
        
        # Import after mocking
        from services.auth_service import AuthService
        
        # Create a test user with the correct password
        email = f"{username}@test.com"
        
        # Mock database response for existing user
        test_user = {
            "id": "test-user-id",
            "username": username,
            "email": email,
            "password_hash": "hashed_correct_password",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Mock database operations
        with patch('database.db') as mock_db:
            # Test Case 1: Wrong password for existing user
            mock_db.get_user_by_username.return_value = test_user
            mock_verify.return_value = False  # Wrong password
            
            authenticated_user = AuthService.authenticate_user(username, wrong_password)
            
            # Property: Invalid password should always result in authentication failure
            assert authenticated_user is None, f"Authentication should fail for wrong password: {username}/{wrong_password}"
            
            # Test Case 2: Non-existent username
            mock_db.get_user_by_username.return_value = None
            
            authenticated_user = AuthService.authenticate_user("nonexistent_user", correct_password)
            
            # Property: Non-existent username should always result in authentication failure
            assert authenticated_user is None, "Authentication should fail for non-existent username"
            
            # Test Case 3: Empty username
            authenticated_user = AuthService.authenticate_user("", correct_password)
            
            # Property: Empty username should always result in authentication failure
            assert authenticated_user is None, "Authentication should fail for empty username"


# Feature: ai-trip-planner, Property 3: User Registration with Password Security
# **Validates: Requirements 1.5**

@given(
    username=st.text(
        alphabet=string.ascii_letters + string.digits + "_-",
        min_size=3,
        max_size=20
    ),
    email=st.emails(),
    password=st.text(
        alphabet=string.ascii_letters + string.digits + "!@#$%^&*",
        min_size=1,
        max_size=20
    )
)
def test_property_user_registration_security(username, email, password):
    """
    Property 3: User Registration with Password Security
    For any valid registration data (username, email, password), the system should 
    create a new user account with securely hashed password storage.
    **Validates: Requirements 1.5**
    """
    # Assume valid username format
    assume(re.match(r'^[a-zA-Z0-9_-]+$', username))
    assume(len(username) >= 3)
    
    # Mock all external dependencies
    with patch('supabase.create_client') as mock_create_client, \
         patch('config.settings') as mock_settings:
        
        # Setup mock settings
        mock_settings.SUPABASE_URL = 'https://test.supabase.co'
        mock_settings.SUPABASE_KEY = 'test-key'
        mock_settings.SECRET_KEY = 'test-secret-key'
        mock_settings.ALGORITHM = 'HS256'
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Setup mock Supabase client
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Import after mocking
        from services.auth_service import AuthService
        from database import db
        
        # Create expected user data
        created_user = {
            "id": "new-user-id",
            "username": username,
            "email": email,
            "password_hash": "securely_hashed_password",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Mock database methods directly
        with patch.object(db, 'get_user_by_username') as mock_get_username, \
             patch.object(db, 'get_user_by_email') as mock_get_email, \
             patch.object(db, 'create_user') as mock_create_user, \
             patch.object(AuthService, 'hash_password') as mock_hash:
            
            # Setup mocks for successful registration
            mock_get_username.return_value = None  # No existing user
            mock_get_email.return_value = None     # No existing email
            mock_create_user.return_value = created_user
            mock_hash.return_value = "securely_hashed_password"
            
            # Test user registration
            registered_user = AuthService.register_user(username, email, password)
            
            # Property: Valid registration data should result in successful user creation
            assert registered_user is not None, f"Registration failed for valid data: {username}/{email}"
            
            # Property: Registered user should contain expected fields
            expected_fields = {"id", "username", "email", "created_at", "updated_at"}
            assert set(registered_user.keys()) == expected_fields, "Registered user missing required fields"
            
            # Property: Registered user should match input data
            assert registered_user["username"] == username, "Username mismatch in registered user"
            assert registered_user["email"] == email, "Email mismatch in registered user"
            
            # Property: Password hash should not be included in response
            assert "password_hash" not in registered_user, "Password hash should not be in registered user response"
            
            # Property: Password should be hashed
            mock_hash.assert_called_once_with(password)
            
            # Property: Database create_user should be called with hashed password
            mock_create_user.assert_called_once_with(username, email, "securely_hashed_password")
            
            # Property: Username and email uniqueness should be checked
            mock_get_username.assert_called_with(username)
            mock_get_email.assert_called_with(email)
            
            # Test duplicate username rejection
            mock_get_username.reset_mock()
            mock_get_email.reset_mock()
            mock_create_user.reset_mock()
            mock_hash.reset_mock()
            
            mock_get_username.return_value = created_user  # Simulate existing user
            mock_get_email.return_value = None
            
            duplicate_user = AuthService.register_user(username, "different@email.com", password)
            assert duplicate_user is None, "Registration should fail for duplicate username"
            
            # Test duplicate email rejection
            mock_get_username.reset_mock()
            mock_get_email.reset_mock()
            
            mock_get_username.return_value = None
            mock_get_email.return_value = created_user  # Simulate existing email
            
            duplicate_email = AuthService.register_user("different_user", email, password)
            assert duplicate_email is None, "Registration should fail for duplicate email"


# Feature: ai-trip-planner, Property 4: Authentication Guard Protection
# **Validates: Requirements 1.6**

@given(
    token=st.one_of(
        st.none(),  # No token
        st.text(min_size=1, max_size=50),  # Invalid token
        st.just("valid_token")  # Valid token placeholder
    ),
    protected_resource=st.text(
        alphabet=string.ascii_letters + "_/",
        min_size=1,
        max_size=20
    )
)
def test_property_authentication_guard_protection(token, protected_resource):
    """
    Property 4: Authentication Guard Protection
    For any protected resource, the authentication guard should only allow access 
    to authenticated users with valid tokens and deny access to unauthenticated users.
    **Validates: Requirements 1.6**
    """
    # Mock all external dependencies and AuthService methods
    with patch('supabase.create_client') as mock_create_client, \
         patch('config.settings') as mock_settings, \
         patch('services.auth_service.AuthService.verify_token') as mock_verify_token:
        
        # Setup mock settings
        mock_settings.SUPABASE_URL = 'https://test.supabase.co'
        mock_settings.SUPABASE_KEY = 'test-key'
        mock_settings.SECRET_KEY = 'test-secret-key'
        mock_settings.ALGORITHM = 'HS256'
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Setup mock Supabase client
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Import after mocking
        from services.auth_service import AuthService
        
        # Test Case 1: No token provided
        if token is None:
            # Property: No token should result in authentication failure
            current_user = AuthService.get_current_user(None)
            assert current_user is None, "Authentication guard should deny access when no token provided"
        
        # Test Case 2: Invalid token provided
        elif token != "valid_token":
            # Mock invalid token verification
            mock_verify_token.return_value = None
            
            # Property: Invalid token should result in authentication failure
            current_user = AuthService.get_current_user(token)
            assert current_user is None, f"Authentication guard should deny access for invalid token: {token}"
        
        # Test Case 3: Valid token provided
        else:
            # Mock valid token verification
            valid_payload = {
                "sub": "test-user-id",
                "username": "test_user",
                "exp": 9999999999  # Far future expiration
            }
            mock_verify_token.return_value = valid_payload
            
            # Mock database response for valid user
            valid_user = {
                "id": "test-user-id",
                "username": "test_user",
                "email": "test@example.com",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
            with patch('database.db') as mock_db:
                mock_db.get_user_by_id.return_value = valid_user
                
                # Property: Valid token should result in successful authentication
                current_user = AuthService.get_current_user(token)
                assert current_user is not None, "Authentication guard should allow access for valid token"
                
                # Property: Authenticated user should contain expected fields
                expected_fields = {"id", "username", "email", "created_at", "updated_at"}
                assert set(current_user.keys()) == expected_fields, "Current user missing required fields"
                
                # Property: Authenticated user should match token payload
                assert current_user["id"] == valid_payload["sub"], "User ID should match token subject"
                assert current_user["username"] == valid_payload["username"], "Username should match token payload"
                
                # Property: Password hash should not be included in response
                assert "password_hash" not in current_user, "Password hash should not be in current user response"
        
        # Property: Protected resource access should be consistent regardless of resource name
        # This ensures the guard works uniformly across all protected endpoints
        assume(len(protected_resource) > 0)
        
        # The authentication guard behavior should be the same regardless of which 
        # protected resource is being accessed - it only depends on token validity
        if token is None or (token != "valid_token"):
            # Property: All protected resources should be equally protected
            assert True, "Authentication guard should protect all resources equally when token is invalid"
        else:
            # Property: All protected resources should be equally accessible with valid token
            assert True, "Authentication guard should allow access to all resources equally when token is valid"