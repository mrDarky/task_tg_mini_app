# Telegram Mini-App Tasker with Admin Panel

A comprehensive task management system with a Telegram bot interface and web-based admin panel. Users can complete tasks (YouTube views, TikTok likes, subscriptions) and earn star rewards, while administrators manage users, tasks, and categories through a responsive web dashboard.

## Features

### User Features (Telegram Bot)
- 🤖 Interactive Telegram bot interface
- 📋 Browse and complete available tasks
- ⭐ Earn stars for task completion
- 📊 View personal statistics
- 🎯 Task types: YouTube, TikTok, Subscribe

### Admin Panel Features
- 📊 **Dashboard**: Real-time analytics and statistics
- 👥 **Users Management**:
  - View all users with search and filters
  - Ban/unban users
  - Adjust user stars
  - Bulk operations (ban, unban, adjust stars)
  - Role-based access control
- 📝 **Tasks Management**:
  - Create, edit, delete tasks
  - Quick edit functionality
  - Filter by type (YouTube, TikTok, Subscribe)
  - Filter by status (active, inactive)
  - Bulk operations (activate, deactivate)
- 📁 **Categories Management**:
  - Create nested categories and subcategories
  - Tree view display
  - Edit and delete categories
- 🎨 **Responsive Design**: Bootstrap 5 interface works on all devices
- 🔍 **Search & Filters**: Advanced search across all entities
- 📄 **Pagination**: Efficient data handling

## Technology Stack

- **Backend**: FastAPI 0.109.1 (Python async framework) - Security patched
- **Bot**: aiogram 3.x (Telegram Bot API)
- **Database**: SQLite with aiosqlite (async)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Form Handling**: python-multipart 0.0.22 - Security patched
- **Architecture**: RESTful API, Service Layer Pattern

## Project Structure

```
task_tg_mini_app/
├── app/
│   ├── models.py              # Pydantic models
│   ├── routers/               # API endpoints
│   │   ├── users.py
│   │   ├── tasks.py
│   │   ├── categories.py
│   │   └── analytics.py
│   ├── services/              # Business logic
│   │   ├── user_service.py
│   │   ├── task_service.py
│   │   ├── category_service.py
│   │   └── analytics_service.py
│   ├── templates/             # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── tasks.html
│   │   └── categories.html
│   └── static/                # Static assets
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── main.js
│           ├── users.js
│           ├── tasks.js
│           └── categories.js
├── bot/
│   └── bot.py                 # Telegram bot
├── config/
│   └── settings.py            # Configuration
├── database/
│   └── db.py                  # Database layer
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
└── README.md
```

## Installation

### Prerequisites
- Python 3.9 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/mrDarky/task_tg_mini_app.git
   cd task_tg_mini_app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your configuration:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   ADMIN_API_KEY=your_admin_api_key_here
   DATABASE_URL=sqlite:///./task_app.db
   ADMIN_USER_IDS=123456789,987654321
   ```

5. **Initialize the database**
   The database will be automatically created when you first run the application.

## Running the Application

### Option 1: Run Both Services Separately

**Terminal 1 - Start FastAPI Server:**
```bash
python main.py
```
The admin panel will be available at http://localhost:8000

**Terminal 2 - Start Telegram Bot:**
```bash
python -m bot.bot
```

### Option 2: Run with Uvicorn (FastAPI only)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

### Admin Panel

1. Open http://localhost:8000/admin in your browser
2. Navigate through the sections:
   - **Dashboard**: View system statistics
   - **Users**: Manage user accounts
   - **Tasks**: Create and manage tasks
   - **Categories**: Organize tasks into categories

### Telegram Bot

1. Start a chat with your bot on Telegram
2. Send `/start` to register
3. Use the interactive menu to:
   - View available tasks
   - Complete tasks
   - Check your stats
   - Get help

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key API Endpoints

**Users:**
- `GET /api/users` - List users with search/filters
- `GET /api/users/{id}` - Get user details
- `PUT /api/users/{id}` - Update user
- `POST /api/users/{id}/ban` - Ban user
- `POST /api/users/{id}/unban` - Unban user
- `POST /api/users/{id}/adjust-stars` - Adjust user stars
- `POST /api/users/bulk-update` - Bulk update users

**Tasks:**
- `GET /api/tasks` - List tasks with filters
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/bulk-update` - Bulk update tasks

**Categories:**
- `GET /api/categories` - List categories
- `GET /api/categories/tree/all` - Get category tree
- `POST /api/categories` - Create category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

**Analytics:**
- `GET /api/analytics/dashboard` - Get dashboard statistics

## Database Schema

### Users Table
- `id` - Primary key
- `telegram_id` - Unique Telegram user ID
- `username` - Telegram username
- `stars` - Earned stars count
- `status` - User status (active/banned)
- `role` - User role (user/admin)
- `created_at`, `updated_at` - Timestamps

### Tasks Table
- `id` - Primary key
- `title` - Task title
- `description` - Task description
- `type` - Task type (youtube/tiktok/subscribe)
- `url` - Task URL
- `reward` - Star reward amount
- `status` - Task status (active/inactive)
- `category_id` - Foreign key to categories
- `created_at`, `updated_at` - Timestamps

### Categories Table
- `id` - Primary key
- `name` - Category name
- `parent_id` - Self-referencing foreign key for nested categories
- `created_at` - Timestamp

### User_Tasks Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `task_id` - Foreign key to tasks
- `status` - Completion status
- `completed_at` - Completion timestamp
- `created_at` - Timestamp

## Security Features

- Role-based access control (RBAC)
- Admin user ID verification
- Status-based user restrictions (banned users)
- SQL injection prevention (parameterized queries)
- XSS protection in templates
- **All dependencies patched** - No known vulnerabilities
  - FastAPI 0.109.1 (patched ReDoS vulnerability)
  - python-multipart 0.0.22 (patched file write, DoS, and ReDoS vulnerabilities)

## Development

### Adding New Features

1. **New API Endpoint**: Add to `app/routers/`
2. **Business Logic**: Add to `app/services/`
3. **Database Queries**: Update `database/db.py` or services
4. **Frontend**: Update templates in `app/templates/` and JavaScript in `app/static/js/`

### Testing

```bash
# Install testing dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when test suite is created)
pytest
```

## Deployment

### Production Considerations

1. **Use PostgreSQL instead of SQLite** for better concurrency
2. **Set up reverse proxy** (nginx) for the web application
3. **Use process manager** (systemd, supervisor) for the bot
4. **Enable HTTPS** with SSL certificates
5. **Set strong API keys** in environment variables
6. **Configure CORS** if needed for cross-origin requests
7. **Set up monitoring** and logging
8. **Regular backups** of the database

### Environment Variables for Production

```env
BOT_TOKEN=your_production_bot_token
ADMIN_API_KEY=strong_random_api_key
DATABASE_URL=postgresql://user:password@localhost/taskapp
ADMIN_USER_IDS=comma_separated_telegram_ids
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Roadmap

- [ ] Add user authentication for admin panel
- [ ] Implement task approval workflow
- [ ] Add email notifications
- [ ] Create mobile app
- [ ] Add more task types
- [ ] Implement referral system
- [ ] Add payment integration for rewards
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Task scheduling and expiration