# Activity Monitoring System

## Overview

The Activity Monitoring system provides comprehensive tracking and analysis of all user actions and IP addresses accessing the application. It helps administrators identify suspicious behavior, manage IP addresses, and maintain security.

## Features

### 1. Activity Logging
- **Real-time Request Tracking**: Every HTTP request is automatically logged
- **User Identification**: Links activities to authenticated users
- **IP Address Tracking**: Captures and tracks IP addresses (supports proxies via X-Forwarded-For)
- **Detailed Metrics**: Records endpoint, method, status code, user agent, and timestamps

### 2. Suspicious Activity Detection

The system automatically flags suspicious activities including:
- **404 Errors**: Requests to non-existent endpoints
- **Server Errors**: 500-level HTTP status codes
- **Path Traversal**: Attempts using `../` patterns
- **File Type Attacks**: Requests for `.php`, `.asp`, `.jsp` files
- **Common Attack Patterns**: 
  - SQL injection attempts (`SELECT`, `UNION`)
  - XSS attempts (`<script`)
  - WordPress/phpMyAdmin access attempts
  - Attempts to access `.env` or `.git` files

### 3. IP Management
- **IP Tracking**: Monitors all IP addresses with request statistics
- **User-IP Mapping**: Associates users with multiple IP addresses
- **Blocking**: Block/unblock IP addresses with optional reasons
- **Automatic Blocking**: Blocked IPs receive 403 Forbidden responses

### 4. Admin Interface

Access at: `/admin/activity`

#### Three Main Tabs:

**Activity Logs Tab**
- View all logged activities with pagination
- Filter by:
  - User ID
  - Status code
  - Date range
  - Search (IP, endpoint, username)
- Click IP addresses to view all activities from that IP
- One-click IP blocking

**IP Addresses Tab**
- View all tracked IPs with statistics
- Shows:
  - Number of associated users
  - Total requests
  - Suspicious activity count
  - First/last seen timestamps
- Filter by blocked status or suspicious count
- Block/unblock with one click

**Suspicious Activity Tab**
- View only flagged suspicious activities
- Quick access to block problematic IPs
- Detailed information about each suspicious request

## API Endpoints

### Activity Logs

```
GET /api/activity/logs
```
List all activities with optional filters:
- `offset`, `limit`: Pagination
- `user_id`: Filter by user
- `ip_address`: Filter by IP
- `is_suspicious`: Filter suspicious activities
- `start_date`, `end_date`: Date range filter
- `search`: Search in endpoint, IP, or username
- `status_code`: Filter by HTTP status

```
GET /api/activity/logs/suspicious
```
Get only suspicious activities

```
GET /api/activity/logs/user/{user_id}
```
Get all activities for a specific user, including their IP addresses

```
GET /api/activity/logs/ip/{ip_address}
```
Get all activities from a specific IP, including users who used it

### IP Management

```
GET /api/activity/ip-addresses
```
List all tracked IP addresses with stats:
- `offset`, `limit`: Pagination
- `is_blocked`: Filter by blocked status
- `search`: Search IP addresses
- `min_suspicious_count`: Filter by suspicious activity count

```
POST /api/activity/ip-addresses/{ip_address}/block
```
Block an IP address
- Query param `reason`: Optional reason for blocking

```
POST /api/activity/ip-addresses/{ip_address}/unblock
```
Unblock an IP address

```
GET /api/activity/ip-addresses/{ip_address}
```
Get detailed information about a specific IP

## Database Schema

### activity_logs
Stores all HTTP request activities
- `id`: Primary key
- `user_id`: Foreign key to users (nullable for guests)
- `ip_address`: Client IP address
- `endpoint`: Request endpoint
- `method`: HTTP method (GET, POST, etc.)
- `status_code`: HTTP status code
- `user_agent`: Client user agent string
- `action_type`: Categorized action type
- `details`: Additional details
- `is_suspicious`: Boolean flag for suspicious activity
- `created_at`: Timestamp

**Indexes**: user_id, ip_address, created_at, is_suspicious

### ip_addresses
Tracks IP addresses and their status
- `id`: Primary key
- `ip_address`: Unique IP address
- `is_blocked`: Boolean block status
- `block_reason`: Reason for blocking
- `blocked_at`: Timestamp when blocked
- `first_seen`: First request timestamp
- `last_seen`: Most recent request timestamp
- `request_count`: Total number of requests
- `suspicious_count`: Number of suspicious activities

**Indexes**: (ip_address, is_blocked)

### user_ip_mappings
Maps users to IP addresses (many-to-many)
- `id`: Primary key
- `user_id`: Foreign key to users
- `ip_address`: IP address used by user
- `first_seen`: First time user used this IP
- `last_seen`: Last time user used this IP
- `request_count`: Number of requests from user on this IP

**Indexes**: user_id, ip_address
**Unique constraint**: (user_id, ip_address)

## Implementation Details

### Middleware (ActivityLoggingMiddleware)

The middleware intercepts all HTTP requests:
1. Extracts client IP (supports X-Forwarded-For, X-Real-IP headers)
2. Checks if IP is blocked (returns 403 if blocked)
3. Processes the request
4. Determines if activity is suspicious
5. Logs activity to database
6. Updates IP tracking statistics
7. Updates user-IP mappings for authenticated users

### Excluded Endpoints
To reduce noise, these endpoints are not logged:
- `/static/*` - Static assets
- `/health` - Health check
- `/docs*`, `/redoc*`, `/openapi.json` - API documentation

### Suspicious Activity Patterns

The system uses regex patterns to detect suspicious URLs:
```python
SUSPICIOUS_PATTERNS = [
    r'\.\./',           # Path traversal
    r'\.php$',          # PHP files
    r'\.asp$',          # ASP files
    r'\.jsp$',          # JSP files
    r'/admin/config',   # Config access
    r'/wp-admin',       # WordPress
    r'/phpmyadmin',     # phpMyAdmin
    r'<script',         # XSS
    r'SELECT.*FROM',    # SQL injection
    r'UNION.*SELECT',   # SQL injection
    r'/\.env',          # Env file access
    r'/\.git',          # Git access
]
```

## Usage Examples

### Block an IP via API
```bash
curl -X POST "http://localhost:8000/api/activity/ip-addresses/192.168.1.100/block?reason=Suspicious+activity" \
  -H "Cookie: admin_session=YOUR_SESSION_TOKEN"
```

### Get Suspicious Activities
```bash
curl "http://localhost:8000/api/activity/logs/suspicious?limit=10" \
  -H "Cookie: admin_session=YOUR_SESSION_TOKEN"
```

### Search Activities
```bash
curl "http://localhost:8000/api/activity/logs?search=admin&limit=10" \
  -H "Cookie: admin_session=YOUR_SESSION_TOKEN"
```

### Filter by Date Range
```bash
curl "http://localhost:8000/api/activity/logs?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Cookie: admin_session=YOUR_SESSION_TOKEN"
```

## Security Considerations

1. **IP Blocking**: Blocked IPs receive immediate 403 responses, preventing further access
2. **Pattern Detection**: Multiple attack patterns are detected automatically
3. **Guest Tracking**: Even unauthenticated users are tracked by IP
4. **Admin Access**: All activity monitoring features require admin authentication
5. **Proxy Support**: Properly handles X-Forwarded-For headers from load balancers

## Performance

- **Database Indexes**: Optimized queries with indexes on key fields
- **Pagination**: All list endpoints support pagination (default 50 items)
- **Efficient Logging**: Middleware uses async operations to minimize impact
- **Query Optimization**: Uses JOIN operations to reduce database round trips

## Monitoring Best Practices

1. **Regular Review**: Check suspicious activities daily
2. **IP Blocking**: Block IPs showing attack patterns
3. **User Analysis**: Review activities of users with multiple IPs
4. **Trend Analysis**: Monitor request patterns and status codes
5. **False Positives**: Review blocked IPs periodically to avoid blocking legitimate users

## Troubleshooting

### Activity Not Logging
- Check if middleware is registered in `main.py`
- Verify database tables exist
- Check if endpoint is in excluded list

### IP Not Detected Correctly
- Verify reverse proxy configuration
- Check X-Forwarded-For or X-Real-IP headers
- Test with `curl -H "X-Forwarded-For: test-ip"`

### Performance Issues
- Reduce log retention period
- Add more indexes if needed
- Consider moving to PostgreSQL for high traffic

## Future Enhancements

Potential improvements:
- Geolocation lookup for IP addresses
- Automated blocking based on suspicious activity thresholds
- Email alerts for critical security events
- Export logs to CSV/JSON
- Integration with external threat intelligence feeds
- Machine learning for anomaly detection
