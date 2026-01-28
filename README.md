# Telegram Mini-App Tasker with Admin Panel

A comprehensive task management system with a Telegram bot interface, Telegram Mini-App, and web-based admin panel. Users can complete tasks (YouTube views, TikTok likes, subscriptions) and earn star rewards, while administrators manage users, tasks, and categories through a responsive web dashboard.

## Features

### User Features (Telegram Bot)
- 🤖 Interactive Telegram bot interface with inline keyboards
- 📋 Browse and complete available tasks organized by categories
- ⭐ Earn stars for task completion
- 📊 View comprehensive personal statistics and achievements
- 🎁 Daily bonus system with streak tracking
- 👥 Referral system - earn 50 stars per referred friend
- 🎯 Task types: YouTube, TikTok, Subscribe
- 📸 Screenshot verification for tasks
- 💬 Support ticket system
- ⚙️ Customizable notification preferences
- 🌐 Multi-language support (EN, RU, ES)

### Telegram Mini-App Features
- 🏠 **Home Screen**: 
  - Star balance display with real-time updates
  - Daily bonus claim with streak counter
  - Quick task access
  - Notification bell with alerts
- 📋 **Tasks Page**:
  - Category filters (YouTube, TikTok, Subscribe)
  - Task cards with rewards, time estimates, and completion status
  - Progress indicators
  - Interactive task browsing
- 👤 **Profile Page**:
  - Avatar and username display
  - Star history graph (last 7 days)
  - Achievement badges showcase
  - Referral section with shareable link
  - Detailed statistics (completed tasks, referrals, achievements)
- 🎁 **Rewards Page**:
  - Redeemable items catalog (gift cards, cash)
  - Withdrawal options (PayPal, Crypto, Bank Transfer)
  - Transaction history
  - Partner offers
- 📝 **Task Detail Page**:
  - Step-by-step instructions
  - Verification requirements
  - Timer for video watches
  - Completion button with proof submission
  - Related tasks suggestions

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
- 💰 **Withdrawals Management**:
  - Review and approve withdrawal requests
  - Transaction tracking
- 🔔 **Notifications System**:
  - Send targeted notifications
  - Broadcast messages to users
- 🎫 **Support Tickets**:
  - Manage user support requests
  - Respond to tickets
- 🎨 **Responsive Design**: Bootstrap 5 interface works on all devices
- 🔍 **Search & Filters**: Advanced search across all entities
- 📄 **Pagination**: Efficient data handling

## Technology Stack

- **Backend**: FastAPI 0.109.1 (Python async framework) - Security patched
- **Bot**: aiogram 3.x (Telegram Bot API)
- **Database**: SQLite with aiosqlite (async)
- **Frontend**: Bootstrap 5, Vanilla JavaScript, Telegram Web App SDK
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
   BOT_USERNAME=your_bot_username
   ADMIN_API_KEY=your_admin_api_key_here
   DATABASE_URL=sqlite:///./task_app.db
   ADMIN_USER_IDS=123456789,987654321
   WEB_APP_URL=http://localhost:8000
   ```

5. **Initialize the database**
   The database will be automatically created when you first run the application.

## Running the Application

### Option 1: Run All Services Together (Recommended)

Run all three components (Web App, Admin Panel, and Bot) with a single command:

**Using Python:**
```bash
python run.py
```

**Or using the shell script:**
```bash
./start.sh
```

This will start:
- 🌐 FastAPI Web App (Mini-App) at http://localhost:8000/miniapp
- 👨‍💼 Admin Panel at http://localhost:8000/admin
- 🤖 Telegram Bot (if BOT_TOKEN is configured)

The script provides:
- ✨ Real-time colored output from all services
- 📊 Process monitoring and health checks
- 🛑 Graceful shutdown with Ctrl+C
- 📍 Clear access points and service status

### Option 2: Run Services Individually

**Run only the Web App + Admin Panel:**
```bash
python run_app.py
```
Access at http://localhost:8000/admin and http://localhost:8000/miniapp

**Run only the Telegram Bot:**
```bash
python run_bot.py
```
Requires BOT_TOKEN to be set in .env

### Option 3: Run Services Separately (Manual)

**Terminal 1 - Start FastAPI Server:**
```bash
python main.py
```
The admin panel will be available at http://localhost:8000

**Terminal 2 - Start Telegram Bot:**
```bash
python -m bot.bot
```

### Option 4: Run with Uvicorn (FastAPI only, development)
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
2. Send `/start` to register and get your referral code
3. Available commands:
   - `/start` - Welcome message with referral system
   - `/tasks` - Browse tasks by category
   - `/profile` - View your profile, stats, and achievements
   - `/help` - Get help and support information
   - `/settings` - Manage notification preferences and language
4. Use the interactive menu to:
   - Open the Mini App for full experience
   - View and complete tasks
   - Claim daily bonuses
   - Check your stats and achievements
   - Share referral links
   - Get help and support

### Telegram Mini-App

1. Click "Open Mini App" button in the bot
2. Browse through the available pages:
   - **Home**: Quick overview, daily bonus, and stats
   - **Tasks**: Browse and complete tasks by category
   - **Profile**: View detailed statistics, achievements, and referral info
   - **Rewards**: Redeem stars for rewards or withdraw
3. Complete tasks:
   - Select a task from the tasks page
   - Follow the step-by-step instructions
   - Submit proof (screenshot for verification tasks)
   - Receive your star reward

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

### Core Tables

#### Users Table
- `id` - Primary key
- `telegram_id` - Unique Telegram user ID
- `username` - Telegram username
- `referral_code` - Unique referral code
- `stars` - Earned stars count
- `status` - User status (active/banned)
- `role` - User role (user/admin)
- `created_at`, `updated_at` - Timestamps

#### Tasks Table
- `id` - Primary key
- `title` - Task title
- `description` - Task description
- `type` - Task type (youtube/tiktok/subscribe)
- `url` - Task URL
- `reward` - Star reward amount
- `status` - Task status (active/inactive)
- `category_id` - Foreign key to categories
- `completion_limit` - Maximum completions allowed
- `created_at`, `updated_at` - Timestamps

#### Categories Table
- `id` - Primary key
- `name` - Category name
- `parent_id` - Self-referencing foreign key for nested categories
- `created_at` - Timestamp

#### User_Tasks Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `task_id` - Foreign key to tasks
- `status` - Completion status (pending/completed/rejected)
- `completed_at` - Completion timestamp
- `created_at` - Timestamp

### Feature Tables

#### Referrals Table
- `id` - Primary key
- `referrer_id` - User who referred
- `referred_id` - User who was referred
- `bonus_awarded` - Whether bonus was given
- `created_at` - Timestamp

#### Daily_Bonuses Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `bonus_amount` - Stars awarded
- `streak_count` - Consecutive days
- `claimed_at` - Timestamp

#### Achievements Table
- `id` - Primary key
- `name` - Achievement name
- `description` - Description
- `icon` - Icon/emoji
- `requirement_type` - Type of requirement
- `requirement_value` - Value to achieve
- `reward_stars` - Star reward
- `created_at` - Timestamp

#### User_Achievements Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `achievement_id` - Foreign key to achievements
- `earned_at` - Timestamp

#### User_Settings Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `language` - Preferred language
- `notifications_enabled` - All notifications toggle
- `task_notifications` - Task notifications toggle
- `reward_notifications` - Reward notifications toggle
- `updated_at` - Timestamp

#### Task_Submissions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `task_id` - Foreign key to tasks
- `submission_type` - Type (screenshot/other)
- `file_id` - Telegram file ID
- `file_path` - Local file path
- `status` - Review status (pending/approved/rejected)
- `admin_notes` - Admin review notes
- `submitted_at` - Submission timestamp
- `reviewed_at` - Review timestamp

#### Star_Transactions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `amount` - Transaction amount
- `type` - Transaction type (earned/spent/adjusted/bonus/refund)
- `reference_type` - Related entity type
- `reference_id` - Related entity ID
- `description` - Transaction description
- `admin_id` - Admin who made adjustment (if applicable)
- `created_at` - Timestamp

#### Withdrawals Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `amount` - Withdrawal amount
- `status` - Request status (pending/approved/rejected)
- `method` - Withdrawal method
- `details` - Payment details
- `admin_id` - Admin who processed
- `admin_notes` - Processing notes
- `created_at` - Request timestamp
- `processed_at` - Processing timestamp
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
BOT_USERNAME=your_bot_username
ADMIN_API_KEY=strong_random_api_key
DATABASE_URL=postgresql://user:password@localhost/taskapp
ADMIN_USER_IDS=comma_separated_telegram_ids
WEB_APP_URL=https://yourdomain.com
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

### Completed ✅
- [x] Telegram bot with core commands
- [x] Referral system
- [x] Daily bonus with streaks
- [x] Multi-language support
- [x] Task verification with screenshots
- [x] Telegram Mini-App interface
- [x] Achievements system
- [x] Notification preferences
- [x] Support ticket system

### Planned 🚧
- [ ] Add user authentication for admin panel
- [ ] Implement task approval workflow
- [ ] Add email notifications
- [ ] Create mobile app
- [ ] Add more task types (Instagram, Twitter, etc.)
- [ ] Add payment integration for rewards
- [ ] Advanced analytics and reporting
- [ ] Task scheduling and expiration
- [ ] Leaderboards and competitions
- [ ] Team challenges