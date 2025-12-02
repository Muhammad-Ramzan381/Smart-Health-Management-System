"""
Input Validation and Sanitization for Smart Health Management System
Protects against XSS, SQL Injection, and other security threats
"""

import re
import html
from functools import wraps
from flask import request, jsonify


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class Validator:
    """Input validation utilities"""

    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
    NAME_PATTERN = re.compile(r'^[a-zA-Z\s\-]{1,50}$')

    # Dangerous patterns for XSS prevention
    XSS_PATTERNS = [
        re.compile(r'<script.*?>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'<iframe.*?>', re.IGNORECASE),
        re.compile(r'<object.*?>', re.IGNORECASE),
        re.compile(r'<embed.*?>', re.IGNORECASE),
        re.compile(r'<link.*?>', re.IGNORECASE),
        re.compile(r'expression\s*\(', re.IGNORECASE),
    ]

    @staticmethod
    def sanitize_string(value, max_length=500):
        """
        Sanitize a string input
        - Strip whitespace
        - HTML escape special characters
        - Limit length
        - Remove dangerous patterns
        """
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        # Strip and limit length
        value = value.strip()[:max_length]

        # HTML escape to prevent XSS
        value = html.escape(value)

        # Remove dangerous patterns
        for pattern in Validator.XSS_PATTERNS:
            value = pattern.sub('', value)

        return value

    @staticmethod
    def sanitize_html(value, max_length=5000):
        """
        Sanitize HTML content (for rich text fields)
        Removes potentially dangerous tags but keeps safe formatting
        """
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        value = value.strip()[:max_length]

        # Remove dangerous tags
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'link', 'style', 'meta']
        for tag in dangerous_tags:
            value = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', value, flags=re.IGNORECASE | re.DOTALL)
            value = re.sub(f'<{tag}[^>]*/>', '', value, flags=re.IGNORECASE)

        # Remove event handlers
        value = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
        value = re.sub(r'\s+on\w+\s*=\s*\S+', '', value, flags=re.IGNORECASE)

        # Remove javascript: URLs
        value = re.sub(r'javascript:[^"\']*', '', value, flags=re.IGNORECASE)

        return value

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            raise ValidationError("Email is required", "email")

        email = email.strip().lower()

        if len(email) > 120:
            raise ValidationError("Email is too long (max 120 characters)", "email")

        if not Validator.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format", "email")

        return email

    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username:
            raise ValidationError("Username is required", "username")

        username = username.strip()

        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters", "username")

        if len(username) > 30:
            raise ValidationError("Username is too long (max 30 characters)", "username")

        if not Validator.USERNAME_PATTERN.match(username):
            raise ValidationError("Username can only contain letters, numbers, and underscores", "username")

        return username

    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            raise ValidationError("Password is required", "password")

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters", "password")

        if len(password) > 128:
            raise ValidationError("Password is too long (max 128 characters)", "password")

        # Check for at least one lowercase, uppercase, digit
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter", "password")

        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter", "password")

        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit", "password")

        return password

    @staticmethod
    def validate_name(name, field_name="name"):
        """Validate a name field (first name, last name, etc.)"""
        if not name:
            return None

        name = name.strip()

        if len(name) > 50:
            raise ValidationError(f"{field_name} is too long (max 50 characters)", field_name)

        if not Validator.NAME_PATTERN.match(name):
            raise ValidationError(f"{field_name} can only contain letters, spaces, and hyphens", field_name)

        return name

    @staticmethod
    def validate_integer(value, min_val=None, max_val=None, field_name="value"):
        """Validate and convert to integer"""
        if value is None:
            return None

        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer", field_name)

        if min_val is not None and value < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}", field_name)

        if max_val is not None and value > max_val:
            raise ValidationError(f"{field_name} must be at most {max_val}", field_name)

        return value

    @staticmethod
    def validate_float(value, min_val=None, max_val=None, field_name="value"):
        """Validate and convert to float"""
        if value is None:
            return None

        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number", field_name)

        if min_val is not None and value < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}", field_name)

        if max_val is not None and value > max_val:
            raise ValidationError(f"{field_name} must be at most {max_val}", field_name)

        return value

    @staticmethod
    def validate_severity(severity):
        """Validate severity level (1-10)"""
        return Validator.validate_integer(severity, min_val=1, max_val=10, field_name="severity")

    @staticmethod
    def validate_symptoms(symptoms):
        """Validate symptoms list"""
        if not symptoms:
            raise ValidationError("At least one symptom is required", "symptoms")

        if not isinstance(symptoms, list):
            raise ValidationError("Symptoms must be a list", "symptoms")

        if len(symptoms) > 20:
            raise ValidationError("Maximum 20 symptoms allowed", "symptoms")

        sanitized = []
        for symptom in symptoms:
            if symptom:
                sanitized_symptom = Validator.sanitize_string(symptom, max_length=100)
                if sanitized_symptom:
                    sanitized.append(sanitized_symptom.lower())

        if not sanitized:
            raise ValidationError("At least one valid symptom is required", "symptoms")

        return list(set(sanitized))  # Remove duplicates

    @staticmethod
    def validate_datetime(value, field_name="datetime"):
        """Validate and parse datetime string"""
        from datetime import datetime as dt

        if not value:
            return None

        # Try common formats
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
        ]

        for fmt in formats:
            try:
                return dt.strptime(value, fmt)
            except ValueError:
                continue

        # Try ISO format
        try:
            return dt.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            pass

        raise ValidationError(f"Invalid {field_name} format", field_name)

    @staticmethod
    def validate_reminder_type(reminder_type):
        """Validate reminder type"""
        valid_types = ['general', 'diet', 'remedy', 'checkup', 'medication', 'exercise']

        if not reminder_type:
            return 'general'

        reminder_type = reminder_type.lower().strip()

        if reminder_type not in valid_types:
            raise ValidationError(f"Invalid reminder type. Must be one of: {', '.join(valid_types)}", "reminder_type")

        return reminder_type

    @staticmethod
    def validate_priority(priority):
        """Validate priority (1-10, lower = more urgent)"""
        if priority is None:
            return 5
        return Validator.validate_integer(priority, min_val=1, max_val=10, field_name="priority")


def validate_json_request(required_fields=None, optional_fields=None):
    """
    Decorator to validate JSON request body

    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            data = request.get_json()

            if data is None:
                return jsonify({'error': 'Invalid JSON body'}), 400

            # Check required fields
            if required_fields:
                missing = [field for field in required_fields if field not in data or data[field] is None]
                if missing:
                    return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


def handle_validation_error(f):
    """Decorator to handle ValidationError exceptions"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({
                'error': e.message,
                'field': e.field
            }), 400
    return wrapper


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests = {}  # {ip: [(timestamp, endpoint), ...]}

    def is_rate_limited(self, ip, endpoint, max_requests=100, window_seconds=60):
        """
        Check if request should be rate limited

        Args:
            ip: Client IP address
            endpoint: API endpoint
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            True if rate limited, False otherwise
        """
        from datetime import datetime, timedelta

        key = f"{ip}:{endpoint}"
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)

        # Clean old entries
        if key in self.requests:
            self.requests[key] = [
                ts for ts in self.requests[key]
                if ts > cutoff
            ]
        else:
            self.requests[key] = []

        # Check rate limit
        if len(self.requests[key]) >= max_requests:
            return True

        # Add current request
        self.requests[key].append(now)
        return False

    def clear(self):
        """Clear all rate limit data"""
        self.requests = {}


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests=100, window_seconds=60):
    """
    Decorator for rate limiting endpoints

    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr or 'unknown'
            endpoint = request.endpoint or request.path

            if rate_limiter.is_rate_limited(ip, endpoint, max_requests, window_seconds):
                return jsonify({
                    'error': 'Rate limit exceeded. Please try again later.'
                }), 429

            return f(*args, **kwargs)
        return wrapper
    return decorator
