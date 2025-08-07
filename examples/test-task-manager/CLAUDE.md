# CLAUDE.md - Test Task Manager

## Project Overview

Test Task Manager is a simple, maintainable web application for personal task management with user authentication. Built with Flask and SQLite, it demonstrates clean web application architecture following KISS > SOLID > DRY principles.

## Technology Stack & Rationale

### Backend
- **Flask 3.0+**: Minimal, well-documented web framework
- **SQLite**: Zero-configuration database, perfect for simple applications
- **Flask-Login**: Session-based authentication
- **Flask-WTF**: Form handling with CSRF protection
- **Werkzeug**: Built-in password hashing and security utilities

### Frontend
- **Jinja2**: Template engine (built into Flask)
- **Bootstrap 5**: Responsive CSS framework
- **Vanilla JavaScript**: Minimal client-side scripting
- **Bootstrap Icons**: Consistent iconography

### Development Tools
- **Python 3.11+**: Modern Python features
- **uv**: Fast Python package manager
- **pytest**: Testing framework
- **ruff**: Linting and formatting

## Architecture Principles

### KISS > SOLID > DRY
- **Keep It Simple**: Choose simple solutions over complex ones
- **Minimal Abstractions**: Avoid over-engineering
- **Direct Implementation**: Clear, straightforward code paths
- **Essential Features Only**: Focus on core functionality

### Application Structure
```
test_task_manager/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── forms.py              # WTForms form classes
│   ├── auth/                 # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── main/                 # Main application blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── templates/            # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   └── main/
│   └── static/               # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/               # Database migrations (if using Flask-Migrate)
├── tests/                    # Test suite
├── config.py                 # Configuration settings
├── run.py                    # Application entry point
└── requirements.txt          # Dependencies
```

## Development Guidelines

### Code Style
- **PEP 8 Compliance**: Follow Python style guidelines
- **Type Hints**: Use built-in types (`list`, `dict`, not `List`, `Dict`)
- **Docstrings**: Document classes and complex functions only
- **Variable Names**: Clear, descriptive names

### Database Design
- **Simple Schema**: Minimal tables with clear relationships
- **SQLite Defaults**: Use SQLite built-in features (AUTOINCREMENT, TIMESTAMP)
- **Foreign Keys**: Enforce referential integrity
- **Indexing**: Add indexes only when performance requires them

### Security Practices
- **Password Hashing**: Use Werkzeug's built-in bcrypt
- **Session Security**: Secure session cookies with appropriate flags
- **CSRF Protection**: Use Flask-WTF for all forms
- **Input Validation**: Server-side validation for all user inputs
- **SQL Injection Prevention**: Use parameterized queries

### Error Handling
```python
# Preferred error handling pattern
try:
    # Database operation
    db.session.commit()
    flash('Task created successfully.', 'success')
    return redirect(url_for('main.dashboard'))
except Exception as e:
    db.session.rollback()
    flash('An error occurred. Please try again.', 'error')
    return redirect(url_for('main.dashboard'))
```

## Configuration Management

### Environment-Based Configuration
```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
```

### Required Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

## Database Models

### User Model
```python
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    tasks = db.relationship('Task', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### Task Model
```python
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Form Design

### Simple Form Classes
```python
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, BooleanField
from wtforms.validators import DataRequired, Length

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    due_date = DateField('Due Date')
    is_completed = BooleanField('Completed')
```

## Common Commands

### Development Setup
```bash
# Create project directory
mkdir test-task-manager
cd test-task-manager

# Initialize uv project
uv init
uv add flask flask-login flask-wtf

# Setup development environment
uv sync --dev
```

### Database Operations
```bash
# Initialize database
uv run python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Run development server
uv run python run.py
```

### Testing
```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app
```

### Code Quality
```bash
# Lint and format
uv run ruff check .
uv run ruff format .
```

## Deployment Guidelines

### Production Checklist
- [ ] Set `SECRET_KEY` environment variable
- [ ] Configure production database
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS
- [ ] Configure proper logging
- [ ] Set up regular database backups

### Simple Production Setup
```bash
# Install production dependencies
uv sync --no-dev

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY="your-production-secret-key"

# Run with Gunicorn
uv run gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

## Testing Strategy

### Unit Tests
```python
def test_user_password_hashing():
    user = User(email='test@example.com')
    user.set_password('testpassword')
    assert user.check_password('testpassword')
    assert not user.check_password('wrongpassword')
```

### Integration Tests
```python
def test_create_task_logged_in(client, auth):
    auth.login()
    response = client.post('/create', data={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    assert response.status_code == 302  # Redirect after creation
```

## Common Workflows

### Adding New Features
1. **Design**: Keep features simple and focused
2. **Model**: Add database models if needed
3. **Forms**: Create form classes with validation
4. **Routes**: Implement view functions
5. **Templates**: Create minimal, clean templates
6. **Tests**: Add tests for core functionality

### Database Changes
1. **Backup**: Always backup before schema changes
2. **Migration**: Use simple SQL for schema updates
3. **Testing**: Test migrations on development data
4. **Documentation**: Update model documentation

## Security Considerations

### Authentication
- Use Flask-Login for session management
- Implement proper logout functionality
- Hash passwords with Werkzeug's built-in functions
- Use secure session cookies

### Data Protection
- Validate all user inputs
- Use parameterized queries
- Implement CSRF protection
- Sanitize user-generated content

### Production Security
- Use HTTPS in production
- Set secure cookie flags
- Configure proper CORS if needed
- Regular security updates

## Performance Considerations

### Database Optimization
- Use indexes on frequently queried columns
- Implement pagination for large result sets
- Use database-level constraints
- Monitor query performance

### Frontend Optimization
- Minimize CSS and JavaScript
- Use CDN for Bootstrap and icons
- Implement basic caching headers
- Optimize images

## Troubleshooting

### Common Issues
- **Database locked**: Check for unclosed transactions
- **Session issues**: Verify SECRET_KEY is set
- **Import errors**: Check PYTHONPATH and virtual environment
- **Form validation**: Ensure CSRF tokens are included

### Development Issues
- **Port conflicts**: Use `flask run -p 5001` for different port
- **Database schema**: Delete `app.db` and recreate for clean start
- **Dependencies**: Use `uv sync` to ensure all packages installed

## Maintenance Guidelines

### Regular Maintenance
- Update dependencies monthly
- Review and update security practices
- Monitor application logs
- Backup database regularly

### Code Quality
- Run linting before commits
- Keep functions small and focused
- Use meaningful commit messages
- Document breaking changes