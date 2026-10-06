#!/usr/bin/env python3
"""
Update admin user password with new hash format.
"""

import os
from dotenv import load_dotenv
from services.auth_service import AuthService
from supabase import create_client

# Load environment variables
load_dotenv()

def update_admin_password():
    """Update admin password with new hash"""
    print("Updating admin password...")
    
    try:
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        client = create_client(supabase_url, supabase_key)
        
        # Generate new hash for admin123
        new_password = "admin123"
        new_hash = AuthService.hash_password(new_password)
        
        print(f"New hash generated: {new_hash[:20]}...")
        
        # Update admin user password
        result = client.table("users").update({
            "password_hash": new_hash
        }).eq("username", "admin").execute()
        
        if result.data:
            print("✓ Admin password updated successfully")
            
            # Test the new password
            print("Testing new password...")
            auth_result = AuthService.authenticate_user("admin", new_password)
            if auth_result:
                print("✓ Authentication test successful")
                return True
            else:
                print("✗ Authentication test failed")
                return False
        else:
            print("✗ Failed to update admin password")
            return False
            
    except Exception as e:
        print(f"✗ Error updating password: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_admin_password()
    exit(0 if success else 1)