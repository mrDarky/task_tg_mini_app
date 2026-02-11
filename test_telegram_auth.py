#!/usr/bin/env python3
"""
Test Telegram Web App Authentication

This test verifies that the Telegram authentication system is working correctly.
"""

import asyncio
import hmac
import hashlib
import json
from urllib.parse import urlencode
from app.telegram_auth import validate_telegram_init_data
from config.settings import settings
from fastapi import HTTPException


def create_test_init_data(user_id: int = 123456789, username: str = "testuser", bot_token: str = None) -> str:
    """
    Create a valid Telegram initData string for testing
    
    Args:
        user_id: Telegram user ID
        username: Telegram username
        bot_token: Bot token to use (defaults to settings.bot_token)
        
    Returns:
        Valid initData string
    """
    if bot_token is None:
        bot_token = settings.bot_token
    
    # Create user data
    user_data = {
        'id': user_id,
        'username': username,
        'first_name': 'Test',
        'last_name': 'User',
        'language_code': 'en',
        'is_premium': False
    }
    
    # Create init data
    auth_date = '1234567890'
    data = {
        'user': json.dumps(user_data, separators=(',', ':')),
        'auth_date': auth_date,
        'hash': ''  # Will be calculated
    }
    
    # Create data_check_string
    data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()) if k != 'hash')
    
    # Calculate hash
    secret_key = hmac.new(
        key="WebAppData".encode(),
        msg=bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()
    
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    data['hash'] = computed_hash
    
    # Create URL-encoded init_data string
    return urlencode(data)


def test_valid_init_data():
    """Test validation with valid initData"""
    print("\n=== Testing Valid InitData ===")
    
    if not settings.bot_token:
        print("⚠️  BOT_TOKEN not set, skipping test")
        return
    
    # Create valid init data
    init_data = create_test_init_data(user_id=123456789, username="testuser")
    print(f"✓ Created valid initData")
    
    # Validate
    try:
        user_data = validate_telegram_init_data(init_data)
        print(f"✓ InitData validated successfully")
        print(f"  - User ID: {user_data['telegram_id']}")
        print(f"  - Username: {user_data['username']}")
        print(f"  - First name: {user_data['first_name']}")
        
        assert user_data['telegram_id'] == 123456789, "User ID should match"
        assert user_data['username'] == "testuser", "Username should match"
        assert user_data['first_name'] == "Test", "First name should match"
        
        print("✅ Valid initData test PASSED")
    except HTTPException as e:
        print(f"❌ Test FAILED: {e.detail}")
        raise


def test_invalid_hash():
    """Test validation with invalid hash"""
    print("\n=== Testing Invalid Hash ===")
    
    if not settings.bot_token:
        print("⚠️  BOT_TOKEN not set, skipping test")
        return
    
    # Create valid init data first
    init_data = create_test_init_data(user_id=123456789, username="testuser")
    
    # Tamper with the hash
    init_data = init_data.replace("hash=", "hash=invalid")
    print(f"✓ Created initData with invalid hash")
    
    # Try to validate - should fail
    try:
        user_data = validate_telegram_init_data(init_data)
        print(f"❌ Test FAILED: Validation should have failed")
        raise AssertionError("Validation should have failed with invalid hash")
    except HTTPException as e:
        if e.status_code == 401:
            print(f"✓ Validation correctly rejected invalid hash")
            print(f"  Error: {e.detail}")
            print("✅ Invalid hash test PASSED")
        else:
            print(f"❌ Test FAILED: Wrong error code {e.status_code}")
            raise


def test_missing_hash():
    """Test validation with missing hash"""
    print("\n=== Testing Missing Hash ===")
    
    # Create init data without hash
    user_data = {'id': 123456789, 'username': 'testuser'}
    init_data = f"user={json.dumps(user_data)}&auth_date=1234567890"
    print(f"✓ Created initData without hash")
    
    # Try to validate - should fail
    try:
        result = validate_telegram_init_data(init_data)
        print(f"❌ Test FAILED: Validation should have failed")
        raise AssertionError("Validation should have failed without hash")
    except HTTPException as e:
        if e.status_code == 401:
            print(f"✓ Validation correctly rejected missing hash")
            print(f"  Error: {e.detail}")
            print("✅ Missing hash test PASSED")
        else:
            print(f"❌ Test FAILED: Wrong error code {e.status_code}")
            raise


def test_empty_init_data():
    """Test validation with empty initData"""
    print("\n=== Testing Empty InitData ===")
    
    # Try to validate empty string
    try:
        result = validate_telegram_init_data("")
        print(f"❌ Test FAILED: Validation should have failed")
        raise AssertionError("Validation should have failed with empty initData")
    except HTTPException as e:
        if e.status_code == 401:
            print(f"✓ Validation correctly rejected empty initData")
            print(f"  Error: {e.detail}")
            print("✅ Empty initData test PASSED")
        else:
            print(f"❌ Test FAILED: Wrong error code {e.status_code}")
            raise


def test_tampered_user_data():
    """Test validation with tampered user data"""
    print("\n=== Testing Tampered User Data ===")
    
    if not settings.bot_token:
        print("⚠️  BOT_TOKEN not set, skipping test")
        return
    
    # Create valid init data
    init_data = create_test_init_data(user_id=123456789, username="testuser")
    
    # Tamper with the user data
    init_data = init_data.replace("testuser", "hacker")
    print(f"✓ Created initData with tampered user data")
    
    # Try to validate - should fail
    try:
        user_data = validate_telegram_init_data(init_data)
        print(f"❌ Test FAILED: Validation should have failed")
        raise AssertionError("Validation should have failed with tampered data")
    except HTTPException as e:
        if e.status_code == 401:
            print(f"✓ Validation correctly rejected tampered data")
            print(f"  Error: {e.detail}")
            print("✅ Tampered data test PASSED")
        else:
            print(f"❌ Test FAILED: Wrong error code {e.status_code}")
            raise


def run_all_tests():
    """Run all authentication tests"""
    print("\n" + "="*60)
    print("  TELEGRAM WEB APP AUTHENTICATION TESTS")
    print("="*60)
    
    try:
        test_valid_init_data()
        test_invalid_hash()
        test_missing_hash()
        test_empty_init_data()
        test_tampered_user_data()
        
        print("\n" + "="*60)
        print("  ALL AUTHENTICATION TESTS PASSED ✅")
        print("="*60 + "\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    exit_code = run_all_tests()
    sys.exit(exit_code)
