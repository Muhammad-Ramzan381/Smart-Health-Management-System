# Smart Health Management System

A web-based health management platform that provides personalized **diet plans** and **home remedies** based on user symptoms. Built as a Data Structures project demonstrating practical applications of Hash Tables, Binary Search Trees, Tries, Graphs, and Queues.

## Group Members

| Name | Roll No. |
|------|----------|
| M. Arslan Nasir | 2k24-BSAI-26 |
| Mirza M. Dawood | 2k24-BSAI-31 |
| M. Ramzan | 2k24-BSAI-21 |
| Abdul Rehman | 2k24-BSAI-27 |

**Instructor:** Mr. Hassnain Yousaf Khan

## Features

### Core Features
- **Symptom Analysis** - Enter symptoms and get personalized recommendations
- **Home Remedies** - Natural remedies with ingredients and preparation steps
- **Diet Plans** - Comprehensive meal plans tailored to health conditions
- **Heart Rate Monitor** - Measure heart rate using your phone camera (PPG algorithm)
- **Health History** - Track your symptom searches and vitals over time

### Data Structures Used
| Data Structure | Application |
|----------------|-------------|
| **Hash Table** | O(1) symptom-to-remedy lookup |
| **Trie** | Autocomplete suggestions for symptoms |
| **Binary Search Tree** | Sorted recommendations by effectiveness |
| **Graph** | Mapping relationships between symptoms, remedies, and diets |
| **Queue** | Managing symptom history and reminders |

## Project Structure

```
DSA Project/
├── backend/
│   ├── data_structures/
│   │   ├── __init__.py
│   │   ├── hash_table.py      # Hash Table implementation
│   │   ├── trie.py            # Trie for autocomplete
│   │   ├── bst.py             # Binary Search Tree
│   │   ├── graph.py           # Graph for relationships
│   │   └── queue.py           # Queue implementations
│   ├── data/
│   │   └── health_data.json   # Symptoms, remedies, diet plans database
│   ├── app.py                 # Flask application
│   └── recommendation_engine.py  # Core recommendation logic
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Main stylesheet
│   │   └── js/
│   │       ├── app.js         # Main JavaScript
│   │       └── vitals.js      # Heart rate monitor
│   └── templates/
│       ├── index.html         # Home page
│       ├── remedies.html      # Remedies library
│       ├── diet_plans.html    # Diet plans library
│       ├── vitals.html        # Heart rate monitor
│       └── history.html       # Health history
├── requirements.txt           # Python dependencies
├── run.py                     # Application entry point
└── README.md
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone/Download the project**
   ```bash
   cd "d:/Study/DSA Project"
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## Usage

### Symptom Analysis
1. Go to the home page
2. Type symptoms in the search box (autocomplete will suggest)
3. Add multiple symptoms by pressing Enter or clicking suggestions
4. Adjust severity level using the slider
5. Click "Analyze Symptoms" to get recommendations

### Heart Rate Monitor
1. Go to the Vitals page
2. Click "Start Measurement"
3. Place your finger over the camera
4. Hold still for 15 seconds
5. View your heart rate result

### Browse Remedies & Diet Plans
- Use the Remedies and Diet Plans pages to browse all available recommendations
- Search by name, symptom, ingredient, or food

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/autocomplete` | GET | Get symptom suggestions |
| `/api/symptoms` | GET | Get all symptoms |
| `/api/analyze` | POST | Analyze symptoms and get recommendations |
| `/api/remedies` | GET | Get all home remedies |
| `/api/diets` | GET | Get all diet plans |
| `/api/history` | GET | Get search history |
| `/api/vitals` | POST | Record vital signs |

## Technologies Used

- **Backend:** Python, Flask, Pandas
- **Frontend:** HTML5, CSS3, JavaScript
- **Data Storage:** JSON
- **Charts:** Chart.js
- **Icons:** Emoji-based

## Disclaimer

⚠️ **This system provides general health information only and is for educational purposes. It does not provide medical diagnosis or treatment advice. Always consult qualified healthcare professionals for medical concerns.**

## License

This project is created for educational purposes as part of the Data Structures course.

---

*Data Structures (Pr) – Group B Project Lab*
