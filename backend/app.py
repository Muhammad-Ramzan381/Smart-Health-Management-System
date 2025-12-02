"""
Flask Backend for Smart Health Management System
Provides REST API for symptom analysis and recommendations
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys

# Add the backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommendation_engine import get_recommendation_engine

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Initialize recommendation engine
engine = get_recommendation_engine()


# ==================== API Routes ====================

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    """Get symptom suggestions for autocomplete"""
    prefix = request.args.get('prefix', '')
    max_results = request.args.get('max', 10, type=int)

    if not prefix:
        return jsonify({'suggestions': []})

    suggestions = engine.autocomplete_symptoms(prefix, max_results)
    return jsonify({'suggestions': suggestions})


@app.route('/api/symptoms', methods=['GET'])
def get_all_symptoms():
    """Get all available symptoms"""
    symptoms = engine.get_all_symptoms()
    return jsonify({'symptoms': sorted(symptoms)})


@app.route('/api/analyze', methods=['POST'])
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

    symptoms = data.get('symptoms', [])
    severity = data.get('severity', 5)

    if not symptoms:
        return jsonify({'error': 'No symptoms provided'}), 400

    # Validate severity
    severity = max(1, min(10, int(severity)))

    recommendations = engine.get_recommendations(symptoms, severity)

    return jsonify({
        'success': True,
        'input': {
            'symptoms': symptoms,
            'severity': severity
        },
        'recommendations': recommendations
    })


@app.route('/api/remedy/<remedy_name>', methods=['GET'])
def get_remedy(remedy_name):
    """Get details of a specific remedy"""
    remedy = engine.get_remedy_details(remedy_name)

    if remedy:
        return jsonify({'success': True, 'remedy': remedy})
    return jsonify({'success': False, 'error': 'Remedy not found'}), 404


@app.route('/api/diet/<diet_name>', methods=['GET'])
def get_diet(diet_name):
    """Get details of a specific diet plan"""
    diet = engine.get_diet_details(diet_name)

    if diet:
        return jsonify({'success': True, 'diet_plan': diet})
    return jsonify({'success': False, 'error': 'Diet plan not found'}), 404


@app.route('/api/remedies', methods=['GET'])
def get_all_remedies():
    """Get all available remedies"""
    remedies = engine.get_all_remedies()
    return jsonify({'success': True, 'remedies': remedies})


@app.route('/api/diets', methods=['GET'])
def get_all_diets():
    """Get all available diet plans"""
    diets = engine.get_all_diet_plans()
    return jsonify({'success': True, 'diet_plans': diets})


@app.route('/api/search/ingredient', methods=['GET'])
def search_by_ingredient():
    """Search remedies by ingredient"""
    ingredient = request.args.get('q', '')

    if not ingredient:
        return jsonify({'error': 'No ingredient specified'}), 400

    results = engine.search_by_ingredient(ingredient)
    return jsonify({'success': True, 'results': results})


@app.route('/api/search/food', methods=['GET'])
def search_by_food():
    """Search diet plans by food"""
    food = request.args.get('q', '')

    if not food:
        return jsonify({'error': 'No food specified'}), 400

    results = engine.search_by_food(food)
    return jsonify({'success': True, 'results': results})


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get symptom search history"""
    limit = request.args.get('limit', 10, type=int)
    history = engine.get_symptom_history(limit)
    frequency = engine.get_symptom_frequency()

    return jsonify({
        'success': True,
        'history': history,
        'frequency': frequency
    })


@app.route('/api/vitals', methods=['POST'])
def record_vitals():
    """Record vital signs measurement"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Store vitals (in a real app, this would go to a database)
    vitals = {
        'heart_rate': data.get('heart_rate'),
        'timestamp': data.get('timestamp'),
        'notes': data.get('notes', '')
    }

    return jsonify({
        'success': True,
        'message': 'Vitals recorded',
        'data': vitals
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


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('index.html')


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 50)
    print("Smart Health Management System")
    print("=" * 50)
    print(f"Loaded {len(engine.get_all_symptoms())} symptoms")
    print(f"Loaded {len(engine.get_all_remedies())} remedies")
    print(f"Loaded {len(engine.get_all_diet_plans())} diet plans")
    print("=" * 50)
    print("Starting server at http://localhost:5000")
    print("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
