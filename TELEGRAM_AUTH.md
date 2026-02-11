# Telegram Mini App Authentication Implementation

## Overview

This document describes the token-based authentication system implemented for the Telegram Mini App API. The system ensures that only legitimate Telegram users who open the mini app can access the API endpoints.

## Problem Statement

Previously, anyone could access the API endpoints (e.g., `/api/users`, `/api/tasks`) without authentication. This posed security risks as unauthorized users could:
- Access user data
- Manipulate task information
- Create fake withdrawals or tickets
- View sensitive information

## Solution

We implemented Telegram Web App authentication using the official `initData` validation mechanism provided by Telegram. This ensures that:
1. Only requests from the Telegram mini app are accepted
2. The data hasn't been tampered with
3. Each user can only access their own data
4. Authentication tokens expire after 24 hours

## How It Works

### 1. Frontend (Mini App)

When the mini app makes API requests, it includes the Telegram `initData` in the HTTP header:

```javascript
// app/static/miniapp/js/miniapp-common.js
const apiRequest = async function(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    // Add Telegram authentication if available
    if (tg && tg.initData) {
        headers['X-Telegram-Init-Data'] = tg.initData;
    }
    
    const response = await fetch(API_BASE + endpoint, {
        ...options,
        headers: headers
    });
    // ...
};
```

### 2. Backend Authentication

The backend validates the `initData` using HMAC-SHA256 signature verification:

```python
# app/telegram_auth.py
def validate_telegram_init_data(init_data: str) -> Dict[str, Any]:
    # 1. Parse the init_data string
    parsed_data = dict(parse_qsl(init_data))
    
    # 2. Extract and verify the hash
    received_hash = parsed_data.get('hash')
    data_to_check = {k: v for k, v in parsed_data.items() if k != 'hash'}
    
    # 3. Create data_check_string
    data_check_string = '\n'.join(
        f"{k}={v}" for k, v in sorted(data_to_check.items())
    )
    
    # 4. Compute secret key and hash
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
    
    # 5. Verify the hash matches
    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(status_code=401)
    
    # 6. Validate auth_date (24-hour expiry)
    auth_date = int(parsed_data['auth_date'])
    if current_time - auth_date > 86400:
        raise HTTPException(status_code=401)
    
    # 7. Return validated user data
    return user_data
```

### 3. API Route Protection

API routes use FastAPI dependencies to require authentication:

```python
# app/routers/users.py
@router.get("/{user_id}/tasks", response_model=list)
async def fetch_user_tasks(
    user_id: int,
    telegram_user: Dict[str, Any] = Depends(get_telegram_user)
):
    # Verify the authenticated user is requesting their own data
    user = await user_service.get_user(user_id)
    if user['telegram_id'] != telegram_user['telegram_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    tasks = await user_service.get_user_tasks(user_id)
    return tasks
```

## Protected Endpoints

The following endpoints now require Telegram authentication:

### User Data Endpoints
- `GET /api/users/{user_id}` - Get user profile
- `GET /api/users/{user_id}/tasks` - Get user's tasks
- `GET /api/users/{user_id}/daily-bonus` - Get daily bonus status
- `POST /api/users/{user_id}/claim-bonus` - Claim daily bonus
- `GET /api/users/{user_id}/referrals` - Get user's referrals
- `GET /api/users/{user_id}/achievements` - Get user's achievements

### Task Endpoints
- `GET /api/tasks` - List all available tasks
- `GET /api/tasks/{task_id}` - Get task details

### Category Endpoints
- `GET /api/categories` - List categories

### Withdrawal Endpoints
- `POST /api/withdrawals` - Create withdrawal request

### Ticket Endpoints
- `GET /api/tickets` - List support tickets
- `POST /api/tickets` - Create support ticket

## Access Control Model

### User-Specific Data
For endpoints that access user-specific data (profile, tasks, bonuses, etc.), the system:
1. Validates the Telegram authentication
2. Verifies the authenticated user's `telegram_id` matches the requested user's `telegram_id`
3. Returns 403 Forbidden if IDs don't match

### Public Data
Tasks and categories are considered public data visible to all authenticated users:
- Any authenticated Telegram user can view all tasks
- Any authenticated Telegram user can view all categories
- This is by design, as users need to browse available tasks to complete

## Security Features

### 1. HMAC-SHA256 Signature Verification
Uses the bot token to verify the authenticity of the `initData`. Ensures data comes from Telegram and hasn't been tampered with.

### 2. Replay Attack Prevention
Validates `auth_date` to ensure tokens are not older than 24 hours. Prevents reuse of old authentication tokens.

### 3. Access Control
Users can only access their own data. Prevents one user from accessing another user's profile, tasks, or bonuses.

### 4. Secure Token Transmission
The `initData` is sent via HTTPS (in production) and includes:
- User information
- Timestamp
- Cryptographic signature

## Testing

Comprehensive tests are provided in `test_telegram_auth.py`:

```bash
python test_telegram_auth.py
```

Tests cover:
- ✅ Valid initData validation
- ✅ Invalid hash rejection
- ✅ Missing hash rejection
- ✅ Empty initData rejection
- ✅ Tampered data rejection

## Error Responses

### 401 Unauthorized
Returned when:
- `X-Telegram-Init-Data` header is missing
- Hash verification fails
- Auth_date is expired (>24 hours old)
- initData format is invalid

### 403 Forbidden
Returned when:
- User tries to access another user's data
- User tries to perform actions on behalf of another user

### 503 Service Unavailable
Returned when:
- BOT_TOKEN is not configured

## Configuration

Required environment variables:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

The bot token is used to verify the HMAC signature of the initData.

## Migration Notes

### For Existing Users
- No changes required on the user side
- Authentication is transparent to users
- Works automatically when accessing the mini app through Telegram

### For Developers
- All mini app API calls must be made through the Telegram Web App
- Testing outside of Telegram requires generating valid initData
- Use the test helper functions in `test_telegram_auth.py` for testing

## Future Enhancements

Possible improvements:
1. Add rate limiting per user
2. Implement session caching to reduce validation overhead
3. Add admin override mechanism for debugging
4. Implement stricter auth_date validation (shorter window)

## References

- [Telegram Web App Documentation](https://core.telegram.org/bots/webapps)
- [Validating Data from Mini Apps](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)
- [HMAC-SHA256 Specification](https://tools.ietf.org/html/rfc2104)

## Support

For issues or questions:
1. Check the test suite for examples
2. Review the authentication code in `app/telegram_auth.py`
3. Verify BOT_TOKEN is correctly configured
4. Ensure requests include the `X-Telegram-Init-Data` header
