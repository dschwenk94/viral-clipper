# Clippy Multi-User Implementation Guide

This guide explains how to set up and use the new multi-user version of Clippy.

> **🔒 Beta Access Required**: The multi-user version requires being added as an authorized tester in Google Cloud Console. Please contact [@dschwenk94](https://github.com/dschwenk94) to request access.

## 🚀 Quick Start

### 1. Prerequisites
- PostgreSQL 12+ installed and running
- Python 3.8+
- Google Cloud project with YouTube Data API v3 enabled
- OAuth 2.0 credentials (client_secrets.json)
- **Beta Access**: Your Google account must be added as a test user (contact [@dschwenk94](https://github.com/dschwenk94))

### 2. Setup

Run the automated setup script:
```bash
python setup_multiuser.py
```

Or manually:

#### Install dependencies:
```bash
pip install -r requirements_webapp.txt
pip install python-dotenv
```

#### Create PostgreSQL database:
```sql
CREATE USER clippy_user WITH PASSWORD 'your_password';
CREATE DATABASE clippy OWNER clippy_user;
```

#### Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials and secrets
```

#### Run migrations:
```bash
python migrations/001_initial_setup.py
```

### 3. Run the Application
```bash
python app_multiuser.py
```

Access at: http://localhost:5000

## 🔑 Authentication Flow

1. Users click "Sign in with Google" on the home page
2. They're redirected to Google OAuth consent screen
3. **Beta Only**: Only authorized test users can complete authentication
4. After authorization, they're redirected back to Clippy
5. Their tokens are encrypted and stored in the database
6. Each user can only see and manage their own clips

### Getting Beta Access

To use the multi-user version:
1. Contact [@dschwenk94](https://github.com/dschwenk94) with your Google email
2. Wait for confirmation that you've been added as a tester
3. You'll then be able to authenticate with Google

> **Note**: This restriction is temporary while the app is in development mode. Once published, anyone will be able to use it.

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `google_id`: Unique Google identifier
- `email`: User's email
- `name`: Display name
- `refresh_token`: Encrypted OAuth refresh token
- `access_token`: Encrypted OAuth access token
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp

### Upload History Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `video_id`: YouTube video ID
- `video_title`: Title of uploaded video
- `video_url`: YouTube URL
- `uploaded_at`: Upload timestamp

### User Sessions Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `session_token`: Unique session identifier
- `expires_at`: Session expiration
- `ip_address`: Client IP
- `user_agent`: Browser info

## 🔐 Security Features

1. **Token Encryption**: All OAuth tokens are encrypted using Fernet symmetric encryption
2. **Session Management**: 7-day sessions with secure random tokens
3. **User Isolation**: Users can only access their own jobs and uploads
4. **CSRF Protection**: State parameter validation in OAuth flow
5. **Environment Variables**: Sensitive configuration stored in .env

## 🔄 Migration from Single-User

### Option 1: Fresh Start
1. Keep the original single-user version as `app.py`
2. Run multi-user version as `app_multiuser.py`
3. Users start fresh with new accounts

### Option 2: Gradual Migration
1. Export any important data from single-user mode
2. Switch to multi-user mode
3. Users authenticate and start creating new clips

## 🔧 Development Tips

### Testing Locally
```bash
# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=True

# Run with debug
python app_multiuser.py
```

### Database Management
```bash
# Connect to database
psql -U clippy_user -d clippy

# View users
SELECT id, email, created_at FROM users;

# View recent uploads
SELECT u.email, h.video_title, h.uploaded_at 
FROM upload_history h 
JOIN users u ON h.user_id = u.id 
ORDER BY h.uploaded_at DESC 
LIMIT 10;
```

### Debugging Authentication
1. Check `.env` file has correct database credentials
2. Verify `client_secrets.json` exists and is valid
3. Check PostgreSQL is running: `pg_isready`
4. View logs for OAuth errors

## 📝 Environment Variables

Required in `.env`:
- `DB_HOST`: PostgreSQL host (default: localhost)
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `SECRET_KEY`: Flask session secret
- `TOKEN_ENCRYPTION_KEY`: Token encryption key

## 🚨 Common Issues

### "No encryption key provided"
- Set `TOKEN_ENCRYPTION_KEY` in .env file
- Use a strong random key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### "Database connection failed"
- Ensure PostgreSQL is running
- Check database credentials in .env
- Verify database exists and user has permissions

### "OAuth callback failed"
- Ensure redirect URI in Google Cloud Console matches your app URL
- Check `client_secrets.json` is correctly formatted
- Verify YouTube Data API v3 is enabled

## 🔄 WebSocket Events

The multi-user version uses user-specific rooms for real-time updates:
- Progress updates only go to the user who owns the job
- Upload progress is user-specific
- Multiple users can process clips simultaneously

## 📈 Scaling Considerations

For production deployment:
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up Redis for session storage
3. Use a connection pooler for PostgreSQL
4. Implement rate limiting per user
5. Set up proper logging and monitoring

## 🔒 Best Practices

1. **Never commit `.env` to version control**
2. Use strong passwords for database
3. Rotate encryption keys periodically
4. Monitor failed login attempts
5. Implement user quotas if needed
6. Regular database backups

## 📱 Future Enhancements

Potential improvements:
- User profiles and settings
- Clip sharing between users
- Team/organization accounts
- Usage analytics per user
- Subscription tiers
- API access for developers

---

For questions or issues, please refer to the main README.md or create an issue on GitHub.
