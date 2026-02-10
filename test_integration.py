#!/usr/bin/env python3
"""
Integration test for mini-app fixes
Tests:
1. Referral code generation
2. Support ticket creation
3. User data retrieval
"""

import asyncio
import aiosqlite
from app.services import user_service
from app.models import UserCreate, TicketCreate
from database.db import db

async def test_referral_code_generation():
    """Test referral code is generated and saved"""
    print("\n=== Testing Referral Code Generation ===")
    
    # Create a user with referral code
    user_data = UserCreate(
        telegram_id=999888777,
        username="testuser123",
        referral_code="REFTEST1",
        stars=50,
        status="active",
        role="user"
    )
    
    user_id = await user_service.create_user(user_data)
    print(f"✓ Created user with ID: {user_id}")
    
    # Fetch the user back
    user = await user_service.get_user(user_id)
    assert user is not None, "User should exist"
    assert user['referral_code'] == "REFTEST1", "Referral code should be saved"
    print(f"✓ Referral code verified: {user['referral_code']}")
    
    # Test ensure_referral_code for user without code
    # First create user without referral code (simulate old behavior)
    cursor = await db.execute(
        "INSERT INTO users (telegram_id, username, stars, status, role) VALUES (?, ?, ?, ?, ?)",
        (888777666, "olduser", 0, "active", "user")
    )
    old_user_id = cursor.lastrowid
    print(f"✓ Created old user without referral code: {old_user_id}")
    
    # Generate referral code for old user
    new_code = await user_service.ensure_referral_code(old_user_id, 888777666)
    print(f"✓ Generated referral code for old user: {new_code}")
    
    # Verify it was saved
    old_user = await user_service.get_user(old_user_id)
    assert old_user['referral_code'] == new_code, "Referral code should be saved"
    print(f"✓ Referral code saved and verified")
    
    # Clean up
    await db.execute("DELETE FROM users WHERE telegram_id IN (?, ?)", (999888777, 888777666))
    
    print("✅ Referral code generation test PASSED\n")


async def test_ticket_creation():
    """Test support ticket creation"""
    print("=== Testing Support Ticket Creation ===")
    
    # Create a test user first
    user_data = UserCreate(
        telegram_id=777666555,
        username="ticketuser",
        referral_code="TICKET01",
        stars=0,
        status="active",
        role="user"
    )
    user_id = await user_service.create_user(user_data)
    print(f"✓ Created test user: {user_id}")
    
    # Create a ticket
    ticket_query = """
        INSERT INTO tickets (user_id, subject, message, priority, status)
        VALUES (?, ?, ?, ?, 'open')
    """
    cursor = await db.execute(
        ticket_query,
        (user_id, "Test Issue", "This is a test ticket message", "medium")
    )
    ticket_id = cursor.lastrowid
    print(f"✓ Created ticket with ID: {ticket_id}")
    
    # Fetch the ticket
    ticket_row = await db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    assert ticket_row is not None, "Ticket should exist"
    assert ticket_row['subject'] == "Test Issue", "Ticket subject should match"
    assert ticket_row['user_id'] == user_id, "Ticket user_id should match"
    print(f"✓ Ticket verified: {ticket_row['subject']}")
    
    # Test filtering by user_id
    user_tickets = await db.fetch_all("SELECT * FROM tickets WHERE user_id = ?", (user_id,))
    assert len(user_tickets) >= 1, "Should find at least one ticket for user"
    print(f"✓ Found {len(user_tickets)} ticket(s) for user")
    
    # Clean up
    await db.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    print("✅ Support ticket creation test PASSED\n")


async def test_user_data_retrieval():
    """Test user data retrieval with all fields"""
    print("=== Testing User Data Retrieval ===")
    
    # Create user with all fields
    user_data = UserCreate(
        telegram_id=666555444,
        username="completeuser",
        referral_code="COMPLETE",
        stars=150,
        status="active",
        role="user"
    )
    user_id = await user_service.create_user(user_data)
    print(f"✓ Created user: {user_id}")
    
    # Retrieve by ID
    user = await user_service.get_user(user_id)
    assert user is not None, "User should exist"
    assert user['telegram_id'] == 666555444, "Telegram ID should match"
    assert user['username'] == "completeuser", "Username should match"
    assert user['referral_code'] == "COMPLETE", "Referral code should match"
    assert user['stars'] == 150, "Stars should match"
    print(f"✓ User retrieved by ID with all fields correct")
    
    # Retrieve by telegram_id
    user_by_tg = await user_service.get_user_by_telegram_id(666555444)
    assert user_by_tg is not None, "User should be found by telegram_id"
    assert user_by_tg['id'] == user_id, "Should be the same user"
    print(f"✓ User retrieved by telegram_id")
    
    # Search for user
    users = await user_service.get_users(search="completeuser", limit=10)
    assert len(users) >= 1, "Should find user in search"
    found_user = next((u for u in users if u['id'] == user_id), None)
    assert found_user is not None, "User should be in search results"
    print(f"✓ User found in search results")
    
    # Clean up
    await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    print("✅ User data retrieval test PASSED\n")


async def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*50)
    print("  MINI-APP FIXES INTEGRATION TESTS")
    print("="*50)
    
    try:
        await db.connect()
        print("✓ Database connected\n")
        
        await test_referral_code_generation()
        await test_ticket_creation()
        await test_user_data_retrieval()
        
        print("="*50)
        print("  ALL TESTS PASSED ✅")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await db.disconnect()
    
    return 0


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
