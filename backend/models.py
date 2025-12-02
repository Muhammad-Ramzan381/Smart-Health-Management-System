"""
Database Models for Smart Health Management System
Uses SQLAlchemy ORM with SQLite database
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    symptom_records = db.relationship('SymptomRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    vital_records = db.relationship('VitalRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Symptom(db.Model):
    """Symptom model"""
    __tablename__ = 'symptoms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    severity_min = db.Column(db.Integer, default=1)
    severity_max = db.Column(db.Integer, default=10)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    related_symptoms = db.relationship(
        'SymptomRelation',
        foreign_keys='SymptomRelation.symptom_id',
        backref='symptom',
        lazy='dynamic'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'severity_range': [self.severity_min, self.severity_max],
            'description': self.description
        }

    def __repr__(self):
        return f'<Symptom {self.name}>'


class SymptomRelation(db.Model):
    """Many-to-many relationship for related symptoms"""
    __tablename__ = 'symptom_relations'

    id = db.Column(db.Integer, primary_key=True)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptoms.id'), nullable=False)
    related_symptom_id = db.Column(db.Integer, db.ForeignKey('symptoms.id'), nullable=False)
    strength = db.Column(db.Float, default=1.0)  # Relationship strength

    related_symptom = db.relationship('Symptom', foreign_keys=[related_symptom_id])


class Remedy(db.Model):
    """Home remedy model"""
    __tablename__ = 'remedies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text)  # JSON string
    preparation = db.Column(db.Text)
    effectiveness = db.Column(db.Integer, default=5)
    time_to_effect = db.Column(db.String(50))
    safety_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Many-to-many with symptoms
    symptoms = db.relationship('RemedySymptom', backref='remedy', lazy='dynamic')

    def get_ingredients(self):
        """Get ingredients as list"""
        if self.ingredients:
            try:
                return json.loads(self.ingredients)
            except json.JSONDecodeError:
                return []
        return []

    def set_ingredients(self, ingredients_list):
        """Set ingredients from list"""
        self.ingredients = json.dumps(ingredients_list)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ingredients': self.get_ingredients(),
            'preparation': self.preparation,
            'effectiveness': self.effectiveness,
            'time_to_effect': self.time_to_effect,
            'safety_notes': self.safety_notes,
            'symptoms': [rs.symptom.name for rs in self.symptoms if rs.symptom]
        }

    def __repr__(self):
        return f'<Remedy {self.name}>'


class RemedySymptom(db.Model):
    """Association table for remedy-symptom relationship"""
    __tablename__ = 'remedy_symptoms'

    id = db.Column(db.Integer, primary_key=True)
    remedy_id = db.Column(db.Integer, db.ForeignKey('remedies.id'), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptoms.id'), nullable=False)
    effectiveness_for_symptom = db.Column(db.Integer, default=5)

    symptom = db.relationship('Symptom')


class DietPlan(db.Model):
    """Diet plan model"""
    __tablename__ = 'diet_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    foods_to_eat = db.Column(db.Text)  # JSON string
    foods_to_avoid = db.Column(db.Text)  # JSON string
    meal_suggestions = db.Column(db.Text)  # JSON string
    effectiveness = db.Column(db.Integer, default=5)
    duration = db.Column(db.String(50))
    daily_calories = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Many-to-many with symptoms
    symptoms = db.relationship('DietPlanSymptom', backref='diet_plan', lazy='dynamic')

    def get_foods_to_eat(self):
        if self.foods_to_eat:
            try:
                return json.loads(self.foods_to_eat)
            except json.JSONDecodeError:
                return []
        return []

    def set_foods_to_eat(self, foods_list):
        self.foods_to_eat = json.dumps(foods_list)

    def get_foods_to_avoid(self):
        if self.foods_to_avoid:
            try:
                return json.loads(self.foods_to_avoid)
            except json.JSONDecodeError:
                return []
        return []

    def set_foods_to_avoid(self, foods_list):
        self.foods_to_avoid = json.dumps(foods_list)

    def get_meal_suggestions(self):
        if self.meal_suggestions:
            try:
                return json.loads(self.meal_suggestions)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_meal_suggestions(self, meals_dict):
        self.meal_suggestions = json.dumps(meals_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'foods_to_eat': self.get_foods_to_eat(),
            'foods_to_avoid': self.get_foods_to_avoid(),
            'meal_suggestions': self.get_meal_suggestions(),
            'effectiveness': self.effectiveness,
            'duration': self.duration,
            'daily_calories': self.daily_calories,
            'symptoms': [ds.symptom.name for ds in self.symptoms if ds.symptom]
        }

    def __repr__(self):
        return f'<DietPlan {self.name}>'


class DietPlanSymptom(db.Model):
    """Association table for diet plan-symptom relationship"""
    __tablename__ = 'diet_plan_symptoms'

    id = db.Column(db.Integer, primary_key=True)
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plans.id'), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptoms.id'), nullable=False)
    effectiveness_for_symptom = db.Column(db.Integer, default=5)

    symptom = db.relationship('Symptom')


class SymptomRecord(db.Model):
    """User's symptom search/analysis history"""
    __tablename__ = 'symptom_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    symptoms = db.Column(db.Text, nullable=False)  # JSON string of symptom list
    severity = db.Column(db.Integer, default=5)
    recommendations = db.Column(db.Text)  # JSON string
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def get_symptoms(self):
        if self.symptoms:
            try:
                return json.loads(self.symptoms)
            except json.JSONDecodeError:
                return []
        return []

    def set_symptoms(self, symptoms_list):
        self.symptoms = json.dumps(symptoms_list)

    def get_recommendations(self):
        if self.recommendations:
            try:
                return json.loads(self.recommendations)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_recommendations(self, recommendations_dict):
        self.recommendations = json.dumps(recommendations_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'symptoms': self.get_symptoms(),
            'severity': self.severity,
            'recommendations': self.get_recommendations(),
            'notes': self.notes,
            'timestamp': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<SymptomRecord {self.id}>'


class VitalRecord(db.Model):
    """User's vital signs records"""
    __tablename__ = 'vital_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    heart_rate = db.Column(db.Integer)
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    oxygen_saturation = db.Column(db.Integer)
    weight = db.Column(db.Float)
    notes = db.Column(db.Text)
    measured_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'heart_rate': self.heart_rate,
            'blood_pressure': {
                'systolic': self.blood_pressure_systolic,
                'diastolic': self.blood_pressure_diastolic
            } if self.blood_pressure_systolic else None,
            'temperature': self.temperature,
            'oxygen_saturation': self.oxygen_saturation,
            'weight': self.weight,
            'notes': self.notes,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<VitalRecord {self.id}>'


class Reminder(db.Model):
    """User health reminders"""
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reminder_type = db.Column(db.String(50), default='general', index=True)  # diet, remedy, checkup, medication, general
    priority = db.Column(db.Integer, default=5)  # 1-10, lower = more urgent
    scheduled_time = db.Column(db.DateTime, nullable=False, index=True)
    repeat_type = db.Column(db.String(20))  # none, daily, weekly, monthly
    is_completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional references
    remedy_id = db.Column(db.Integer, db.ForeignKey('remedies.id'))
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plans.id'))

    remedy = db.relationship('Remedy')
    diet_plan = db.relationship('DietPlan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'reminder_type': self.reminder_type,
            'priority': self.priority,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'repeat_type': self.repeat_type,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_active': self.is_active,
            'remedy': self.remedy.to_dict() if self.remedy else None,
            'diet_plan': self.diet_plan.to_dict() if self.diet_plan else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Reminder {self.title}>'


def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
