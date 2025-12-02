"""
Flask Backend for Smart Health Management System
Provides REST API for symptom analysis and recommendations
With SQLite database, authentication, and input validation
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
import sys

# Add the backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Symptom, Remedy, DietPlan, SymptomRecord, VitalRecord, Reminder, init_db
from recommendation_engine import get_recommendation_engine
from validators import (
    Validator, ValidationError, validate_json_request,
    handle_validation_error, rate_limit
)

# Initialize Flask app
app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'data', 'health.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
CORS(app, supports_credentials=True)
init_db(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required'}), 401
    return redirect(url_for('login_page'))


# Initialize recommendation engine
engine = get_recommendation_engine()


# ==================== Authentication API Routes ====================

@app.route('/api/auth/register', methods=['POST'])
@handle_validation_error
@rate_limit(max_requests=10, window_seconds=60)
def register():
    """Register a new user"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate inputs
    username = Validator.validate_username(data.get('username'))
    email = Validator.validate_email(data.get('email'))
    password = Validator.validate_password(data.get('password'))
    first_name = Validator.validate_name(data.get('first_name'), 'first_name')
    last_name = Validator.validate_name(data.get('last_name'), 'last_name')

    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Create user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
@handle_validation_error
@rate_limit(max_requests=20, window_seconds=60)
def login():
    """Login user"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username_or_email = Validator.sanitize_string(data.get('username', ''))
    password = data.get('password', '')

    if not username_or_email or not password:
        return jsonify({'error': 'Username/email and password are required'}), 400

    # Find user by username or email
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403

    login_user(user, remember=True)

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict()
    })


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    return jsonify({'authenticated': False})


@app.route('/api/auth/update', methods=['PUT'])
@login_required
@handle_validation_error
def update_profile():
    """Update user profile"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'first_name' in data:
        current_user.first_name = Validator.validate_name(data['first_name'], 'first_name')

    if 'last_name' in data:
        current_user.last_name = Validator.validate_name(data['last_name'], 'last_name')

    if 'gender' in data:
        gender = Validator.sanitize_string(data['gender'], 10)
        if gender and gender.lower() in ['male', 'female', 'other']:
            current_user.gender = gender.lower()

    if 'date_of_birth' in data:
        dob = Validator.validate_datetime(data['date_of_birth'], 'date_of_birth')
        if dob:
            current_user.date_of_birth = dob.date()

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile updated',
        'user': current_user.to_dict()
    })


# ==================== Symptom API Routes ====================

@app.route('/api/autocomplete', methods=['GET'])
@rate_limit(max_requests=100, window_seconds=60)
def autocomplete():
    """Get symptom suggestions for autocomplete"""
    prefix = Validator.sanitize_string(request.args.get('prefix', ''), 50)
    max_results = Validator.validate_integer(
        request.args.get('max', 10),
        min_val=1, max_val=50,
        field_name='max'
    ) or 10

    if not prefix:
        return jsonify({'suggestions': []})

    suggestions = engine.autocomplete_symptoms(prefix, max_results)
    return jsonify({'suggestions': suggestions})


@app.route('/api/symptoms', methods=['GET'])
@rate_limit(max_requests=50, window_seconds=60)
def get_all_symptoms():
    """Get all available symptoms"""
    symptoms = engine.get_all_symptoms()
    return jsonify({'symptoms': sorted(symptoms)})


@app.route('/api/analyze', methods=['POST'])
@handle_validation_error
@rate_limit(max_requests=30, window_seconds=60)
def analyze_symptoms():
    """
    Analyze symptoms and get recommendations

    Request body:
    {
        "symptoms": ["headache", "fever"],
        "severity": 5
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate inputs
    symptoms = Validator.validate_symptoms(data.get('symptoms', []))
    severity = Validator.validate_severity(data.get('severity', 5)) or 5

    recommendations = engine.get_recommendations(symptoms, severity)

    # Save to database if user is authenticated
    if current_user.is_authenticated:
        record = SymptomRecord(user_id=current_user.id, severity=severity)
        record.set_symptoms(symptoms)
        record.set_recommendations({
            'remedies_count': len(recommendations.get('remedies', [])),
            'diets_count': len(recommendations.get('diet_plans', []))
        })
        db.session.add(record)
        db.session.commit()

    return jsonify({
        'success': True,
        'input': {
            'symptoms': symptoms,
            'severity': severity
        },
        'recommendations': recommendations
    })


@app.route('/api/remedy/<remedy_name>', methods=['GET'])
@rate_limit(max_requests=50, window_seconds=60)
def get_remedy(remedy_name):
    """Get details of a specific remedy"""
    remedy_name = Validator.sanitize_string(remedy_name, 200)
    remedy = engine.get_remedy_details(remedy_name)

    if remedy:
        return jsonify({'success': True, 'remedy': remedy})
    return jsonify({'success': False, 'error': 'Remedy not found'}), 404


@app.route('/api/diet/<diet_name>', methods=['GET'])
@rate_limit(max_requests=50, window_seconds=60)
def get_diet(diet_name):
    """Get details of a specific diet plan"""
    diet_name = Validator.sanitize_string(diet_name, 200)
    diet = engine.get_diet_details(diet_name)

    if diet:
        return jsonify({'success': True, 'diet_plan': diet})
    return jsonify({'success': False, 'error': 'Diet plan not found'}), 404


@app.route('/api/remedies', methods=['GET'])
@rate_limit(max_requests=50, window_seconds=60)
def get_all_remedies():
    """Get all available remedies"""
    remedies = engine.get_all_remedies()
    return jsonify({'success': True, 'remedies': remedies})


@app.route('/api/diets', methods=['GET'])
@rate_limit(max_requests=50, window_seconds=60)
def get_all_diets():
    """Get all available diet plans"""
    diets = engine.get_all_diet_plans()
    return jsonify({'success': True, 'diet_plans': diets})


@app.route('/api/search/ingredient', methods=['GET'])
@rate_limit(max_requests=50, window_seconds=60)
def search_by_ingredient():
    """Search remedies by ingredient"""
    ingredient = Validator.sanitize_string(request.args.get('q', ''), 100)

    if not ingredient:
        return jsonify({'error': 'No ingredient specified'}), 400

    results = engine.search_by_ingredient(ingredient)
    return jsonify({'success': True, 'results': results})


@app.route('/api/search/food', methods=['GET'])
@rate_limit(max_requests=50, window_seconds=60)
def search_by_food():
    """Search diet plans by food"""
    food = Validator.sanitize_string(request.args.get('q', ''), 100)

    if not food:
        return jsonify({'error': 'No food specified'}), 400

    results = engine.search_by_food(food)
    return jsonify({'success': True, 'results': results})


# ==================== History API Routes ====================

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get symptom search history"""
    limit = Validator.validate_integer(
        request.args.get('limit', 10),
        min_val=1, max_val=100,
        field_name='limit'
    ) or 10

    # If authenticated, get from database
    if current_user.is_authenticated:
        records = SymptomRecord.query.filter_by(user_id=current_user.id)\
            .order_by(SymptomRecord.created_at.desc())\
            .limit(limit).all()

        history = [record.to_dict() for record in records]

        # Calculate frequency
        all_records = SymptomRecord.query.filter_by(user_id=current_user.id).all()
        frequency = {}
        for record in all_records:
            for symptom in record.get_symptoms():
                symptom_lower = symptom.lower()
                frequency[symptom_lower] = frequency.get(symptom_lower, 0) + 1

        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)

        return jsonify({
            'success': True,
            'history': history,
            'frequency': sorted_freq
        })

    # Otherwise use in-memory history from engine
    history = engine.get_symptom_history(limit)
    frequency = engine.get_symptom_frequency()

    return jsonify({
        'success': True,
        'history': history,
        'frequency': frequency
    })


# ==================== Vitals API Routes ====================

@app.route('/api/vitals', methods=['POST'])
@handle_validation_error
@rate_limit(max_requests=30, window_seconds=60)
def record_vitals():
    """Record vital signs measurement"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    heart_rate = Validator.validate_integer(
        data.get('heart_rate'),
        min_val=30, max_val=250,
        field_name='heart_rate'
    )

    notes = Validator.sanitize_string(data.get('notes', ''), 500)

    # Parse timestamp if provided
    measured_at = None
    if data.get('timestamp'):
        measured_at = Validator.validate_datetime(data['timestamp'], 'timestamp')

    # Save to database if authenticated
    if current_user.is_authenticated:
        vital = VitalRecord(
            user_id=current_user.id,
            heart_rate=heart_rate,
            notes=notes,
            measured_at=measured_at or datetime.utcnow()
        )
        db.session.add(vital)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Vitals recorded',
            'data': vital.to_dict()
        })

    # Return without saving if not authenticated
    return jsonify({
        'success': True,
        'message': 'Vitals recorded (not saved - login required)',
        'data': {
            'heart_rate': heart_rate,
            'timestamp': (measured_at or datetime.utcnow()).isoformat(),
            'notes': notes
        }
    })


@app.route('/api/vitals', methods=['GET'])
@login_required
def get_vitals():
    """Get vital signs history"""
    limit = Validator.validate_integer(
        request.args.get('limit', 50),
        min_val=1, max_val=500,
        field_name='limit'
    ) or 50

    records = VitalRecord.query.filter_by(user_id=current_user.id)\
        .order_by(VitalRecord.measured_at.desc())\
        .limit(limit).all()

    return jsonify({
        'success': True,
        'vitals': [record.to_dict() for record in records]
    })


# ==================== Reminder API Routes ====================

@app.route('/api/reminders', methods=['GET'])
@login_required
def get_reminders():
    """Get user's reminders"""
    show_completed = request.args.get('completed', 'false').lower() == 'true'

    query = Reminder.query.filter_by(user_id=current_user.id, is_active=True)

    if not show_completed:
        query = query.filter_by(is_completed=False)

    reminders = query.order_by(Reminder.scheduled_time.asc()).all()

    return jsonify({
        'success': True,
        'reminders': [r.to_dict() for r in reminders]
    })


@app.route('/api/reminders', methods=['POST'])
@login_required
@handle_validation_error
@rate_limit(max_requests=30, window_seconds=60)
def create_reminder():
    """Create a new reminder"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    title = Validator.sanitize_string(data.get('title', ''), 200)
    message = Validator.sanitize_string(data.get('message', ''), 1000)

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    reminder_type = Validator.validate_reminder_type(data.get('reminder_type'))
    priority = Validator.validate_priority(data.get('priority'))

    scheduled_time = Validator.validate_datetime(
        data.get('scheduled_time'),
        'scheduled_time'
    )

    if not scheduled_time:
        return jsonify({'error': 'Scheduled time is required'}), 400

    repeat_type = data.get('repeat_type')
    if repeat_type and repeat_type not in ['none', 'daily', 'weekly', 'monthly']:
        repeat_type = 'none'

    reminder = Reminder(
        user_id=current_user.id,
        title=title,
        message=message,
        reminder_type=reminder_type,
        priority=priority,
        scheduled_time=scheduled_time,
        repeat_type=repeat_type
    )

    # Link to remedy or diet if provided
    if data.get('remedy_id'):
        reminder.remedy_id = data['remedy_id']
    if data.get('diet_plan_id'):
        reminder.diet_plan_id = data['diet_plan_id']

    db.session.add(reminder)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Reminder created',
        'reminder': reminder.to_dict()
    }), 201


@app.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
@login_required
@handle_validation_error
def update_reminder(reminder_id):
    """Update a reminder"""
    reminder = Reminder.query.filter_by(
        id=reminder_id,
        user_id=current_user.id
    ).first()

    if not reminder:
        return jsonify({'error': 'Reminder not found'}), 404

    data = request.get_json()

    if 'title' in data:
        reminder.title = Validator.sanitize_string(data['title'], 200)

    if 'message' in data:
        reminder.message = Validator.sanitize_string(data['message'], 1000)

    if 'reminder_type' in data:
        reminder.reminder_type = Validator.validate_reminder_type(data['reminder_type'])

    if 'priority' in data:
        reminder.priority = Validator.validate_priority(data['priority'])

    if 'scheduled_time' in data:
        reminder.scheduled_time = Validator.validate_datetime(
            data['scheduled_time'],
            'scheduled_time'
        )

    if 'is_completed' in data:
        reminder.is_completed = bool(data['is_completed'])
        if reminder.is_completed:
            reminder.completed_at = datetime.utcnow()

    if 'is_active' in data:
        reminder.is_active = bool(data['is_active'])

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Reminder updated',
        'reminder': reminder.to_dict()
    })


@app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
@login_required
def delete_reminder(reminder_id):
    """Delete a reminder"""
    reminder = Reminder.query.filter_by(
        id=reminder_id,
        user_id=current_user.id
    ).first()

    if not reminder:
        return jsonify({'error': 'Reminder not found'}), 404

    db.session.delete(reminder)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Reminder deleted'
    })


@app.route('/api/reminders/<int:reminder_id>/complete', methods=['POST'])
@login_required
def complete_reminder(reminder_id):
    """Mark reminder as completed"""
    reminder = Reminder.query.filter_by(
        id=reminder_id,
        user_id=current_user.id
    ).first()

    if not reminder:
        return jsonify({'error': 'Reminder not found'}), 404

    reminder.is_completed = True
    reminder.completed_at = datetime.utcnow()

    # Handle repeating reminders
    if reminder.repeat_type and reminder.repeat_type != 'none':
        # Create next occurrence
        next_time = reminder.scheduled_time
        if reminder.repeat_type == 'daily':
            next_time += timedelta(days=1)
        elif reminder.repeat_type == 'weekly':
            next_time += timedelta(weeks=1)
        elif reminder.repeat_type == 'monthly':
            next_time += timedelta(days=30)

        new_reminder = Reminder(
            user_id=current_user.id,
            title=reminder.title,
            message=reminder.message,
            reminder_type=reminder.reminder_type,
            priority=reminder.priority,
            scheduled_time=next_time,
            repeat_type=reminder.repeat_type,
            remedy_id=reminder.remedy_id,
            diet_plan_id=reminder.diet_plan_id
        )
        db.session.add(new_reminder)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Reminder completed'
    })


# ==================== Frontend Routes ====================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/remedies')
def remedies_page():
    """Serve the remedies page"""
    return render_template('remedies.html')


@app.route('/diet-plans')
def diet_plans_page():
    """Serve the diet plans page"""
    return render_template('diet_plans.html')


@app.route('/vitals')
def vitals_page():
    """Serve the vitals monitoring page"""
    return render_template('vitals.html')


@app.route('/history')
def history_page():
    """Serve the history page"""
    return render_template('history.html')


@app.route('/login')
def login_page():
    """Serve the login page"""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """Serve the registration page"""
    return render_template('register.html')


@app.route('/reminders')
@login_required
def reminders_page():
    """Serve the reminders page"""
    return render_template('reminders.html')


@app.route('/profile')
@login_required
def profile_page():
    """Serve the profile page"""
    return render_template('profile.html')


# ==================== Error Handlers ====================

@app.errorhandler(ValidationError)
def handle_validation_error_global(error):
    return jsonify({
        'error': error.message,
        'field': error.field
    }), 400


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('index.html')


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(429)
def rate_limit_error(error):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 60)
    print("Smart Health Management System")
    print("=" * 60)
    print(f"Loaded {len(engine.get_all_symptoms())} symptoms")
    print(f"Loaded {len(engine.get_all_remedies())} remedies")
    print(f"Loaded {len(engine.get_all_diet_plans())} diet plans")
    print("=" * 60)
    print("Features:")
    print("  - SQLite Database with persistence")
    print("  - User Authentication (register/login)")
    print("  - Input Validation & Sanitization")
    print("  - Rate Limiting")
    print("  - Health Reminders System")
    print("=" * 60)
    print("Starting server at http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
