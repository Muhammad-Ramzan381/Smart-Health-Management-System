"""
Smart Health Management System
Run this file to start the application

Usage: python run.py
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("   SMART HEALTH MANAGEMENT SYSTEM")
    print("   Data Structures Project - Group B")
    print("=" * 60)
    print("\n[+] Features:")
    print("   - Symptom Analysis with Autocomplete (Trie)")
    print("   - Home Remedies Recommendations (Hash Table)")
    print("   - Diet Plans Recommendations (BST)")
    print("   - Health Relationship Mapping (Graph)")
    print("   - Heart Rate Monitoring (PPG Algorithm)")
    print("   - Symptom History Tracking (Queue)")
    print("   - User Authentication (Flask-Login)")
    print("   - Database Persistence (SQLite)")
    print("   - Health Reminders System")
    print("\n" + "=" * 60)
    print("[*] Starting server...")
    print("[*] Open your browser and go to: http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
