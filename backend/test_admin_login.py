#!/usr/bin/env python3
"""
Test admin login functionality.
"""

import os
from dotenv import load_dotenv
from services.auth_service import AuthService
from database import db

# Load environment variables
load_dotenv()

def test_admin_login():
    """Test admin login"""
    print("Testing admin login...")
    
    try:
        # Test getting admin user
        print("1. Testing database connection...")
        admin_user = db.get_user_by_username("admin")
        if admin_user:
            print(f"✓ Admin user found: {admin_user['username']} ({admin_user['email']})")
            print(f"  Password hash: {admin_user['password_hash'][:20]}...")
        else:
            print("✗ Admin user not found in database")
            return False
        
        # Test password verification
        print("2. Testing password verification...")
        test_password = "admin123"
        
        # Test the hash verification directly
        is_valid = AuthService.verify_password(test_password, admin_user['password_hash'])
        if is_valid:
            print("✓ Password verification successful")
        else:
            print("✗ Password verification failed")
            
            # Try to create a new hash and compare
            print("3. Testing hash generation...")
            new_hash = AuthService.hash_password(test_password)
            print(f"  New hash: {new_hash[:20]}...")
            
            # Test with new hash
            is_valid_new = AuthService.verify_password(test_password, new_hash)
            print(f"  New hash verification: {'✓' if is_valid_new else '✗'}")
            
            return False
        
        # Test full authentication
        print("3. Testing full authentication...")
        auth_result = AuthService.authenticate_user("admin", test_password)
        if auth_result:
            print("✓ Full authentication successful")
            print(f"  User ID: {auth_result['id']}")
            print(f"  Username: {auth_result['username']}")
            return True
        else:
            print("✗ Full authentication failed")
            return False
            
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin_login()
    exit(0 if success else 1)