"""
Recommendation Engine for Smart Health Management System
Uses data structures to provide diet plans and home remedy recommendations
"""

import json
import os
from data_structures import (
    SymptomHashTable,
    SymptomTrie,
    RecommendationBST,
    HealthGraph,
    SymptomHistoryQueue
)


class RecommendationEngine:
    def __init__(self):
        # Initialize data structures
        self.symptom_hash = SymptomHashTable()
        self.symptom_trie = SymptomTrie()
        self.remedy_bst = RecommendationBST()
        self.diet_bst = RecommendationBST()
        self.health_graph = HealthGraph()
        self.symptom_history = SymptomHistoryQueue()

        # Store raw data
        self.symptoms_data = []
        self.remedies_data = []
        self.diet_plans_data = []

        # Load data on initialization
        self._load_data()

    def _load_data(self):
        """Load health data from JSON file"""
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'health_data.json')

        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.symptoms_data = data.get('symptoms', [])
            self.remedies_data = data.get('home_remedies', [])
            self.diet_plans_data = data.get('diet_plans', [])

            self._build_data_structures()
        except FileNotFoundError:
            print(f"Warning: Data file not found at {data_path}")
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in data file")

    def _build_data_structures(self):
        """Build all data structures from loaded data"""
        # Build symptom trie and hash table
        for symptom in self.symptoms_data:
            symptom_name = symptom['name'].lower()

            # Add to trie for autocomplete
            self.symptom_trie.insert_symptom(
                symptom_name,
                severity_range=symptom.get('severity_range'),
                category=symptom.get('category')
            )

            # Add to graph
            self.health_graph.add_symptom(symptom_name, symptom)

            # Link related symptoms
            for related in symptom.get('related_symptoms', []):
                self.health_graph.add_symptom(related.lower())
                self.health_graph.link_related_symptoms(symptom_name, related.lower())

        # Build remedy hash table and BST
        for remedy in self.remedies_data:
            remedy_name = remedy['name']

            # Add to BST sorted by effectiveness
            self.remedy_bst.add_recommendation(
                remedy.get('effectiveness', 5),
                remedy
            )

            # Add to graph and link to symptoms
            self.health_graph.add_remedy(remedy_name, remedy)

            for symptom in remedy.get('symptoms', []):
                symptom_lower = symptom.lower()
                # Add to hash table for O(1) lookup
                self.symptom_hash.add_remedy(symptom_lower, {
                    'type': 'remedy',
                    'data': remedy
                })
                # Add to graph
                self.health_graph.add_symptom(symptom_lower)
                self.health_graph.link_symptom_to_remedy(
                    symptom_lower,
                    remedy_name,
                    effectiveness=remedy.get('effectiveness', 5)
                )

        # Build diet plan BST
        for diet in self.diet_plans_data:
            diet_name = diet['name']

            # Add to BST sorted by effectiveness
            self.diet_bst.add_recommendation(
                diet.get('effectiveness', 5),
                diet
            )

            # Add to graph and link to symptoms
            self.health_graph.add_diet_plan(diet_name, diet)

            for symptom in diet.get('symptoms', []):
                symptom_lower = symptom.lower()
                # Add to hash table
                self.symptom_hash.add_remedy(symptom_lower, {
                    'type': 'diet',
                    'data': diet
                })
                # Add to graph
                self.health_graph.add_symptom(symptom_lower)
                self.health_graph.link_symptom_to_diet(
                    symptom_lower,
                    diet_name,
                    effectiveness=diet.get('effectiveness', 5)
                )

    def autocomplete_symptoms(self, prefix, max_results=10):
        """Get symptom suggestions based on prefix"""
        return self.symptom_trie.autocomplete(prefix, max_results)

    def get_recommendations(self, symptoms, severity=5):
        """
        Get diet plans and home remedies for given symptoms

        Args:
            symptoms: List of symptom strings
            severity: Severity level (1-10)

        Returns:
            Dictionary with remedies and diet plans
        """
        symptoms_lower = [s.lower().strip() for s in symptoms if s.strip()]

        if not symptoms_lower:
            return {
                'remedies': [],
                'diet_plans': [],
                'related_symptoms': []
            }

        # Use graph to get comprehensive recommendations
        graph_recommendations = self.health_graph.get_recommendations_for_symptoms(symptoms_lower)

        # Also use hash table for quick lookup
        hash_remedies = {}
        hash_diets = {}

        for symptom in symptoms_lower:
            results = self.symptom_hash.get_remedies(symptom)
            for item in results:
                if item['type'] == 'remedy':
                    name = item['data']['name']
                    if name not in hash_remedies:
                        hash_remedies[name] = {
                            'data': item['data'],
                            'match_count': 0
                        }
                    hash_remedies[name]['match_count'] += 1
                elif item['type'] == 'diet':
                    name = item['data']['name']
                    if name not in hash_diets:
                        hash_diets[name] = {
                            'data': item['data'],
                            'match_count': 0
                        }
                    hash_diets[name]['match_count'] += 1

        # Combine and rank remedies
        remedies = []
        seen_remedies = set()

        # Add from graph first (already sorted by effectiveness and matches)
        for r in graph_recommendations.get('remedies', []):
            if r['name'] not in seen_remedies:
                remedy_data = r['data'] if r['data'] else self._find_remedy_by_name(r['name'])
                if remedy_data:
                    remedies.append({
                        **remedy_data,
                        'match_count': r['matches'],
                        'relevance_score': r['score']
                    })
                    seen_remedies.add(r['name'])

        # Add any from hash table that might have been missed
        for name, info in hash_remedies.items():
            if name not in seen_remedies:
                remedies.append({
                    **info['data'],
                    'match_count': info['match_count'],
                    'relevance_score': info['data'].get('effectiveness', 5) * info['match_count']
                })

        # Sort remedies by match count then effectiveness
        remedies.sort(key=lambda x: (x['match_count'], x.get('effectiveness', 5)), reverse=True)

        # Combine and rank diet plans
        diet_plans = []
        seen_diets = set()

        for d in graph_recommendations.get('diet_plans', []):
            if d['name'] not in seen_diets:
                diet_data = d['data'] if d['data'] else self._find_diet_by_name(d['name'])
                if diet_data:
                    diet_plans.append({
                        **diet_data,
                        'match_count': d['matches'],
                        'relevance_score': d['score']
                    })
                    seen_diets.add(d['name'])

        for name, info in hash_diets.items():
            if name not in seen_diets:
                diet_plans.append({
                    **info['data'],
                    'match_count': info['match_count'],
                    'relevance_score': info['data'].get('effectiveness', 5) * info['match_count']
                })

        diet_plans.sort(key=lambda x: (x['match_count'], x.get('effectiveness', 5)), reverse=True)

        # Get related symptoms
        related_symptoms = set()
        for symptom in symptoms_lower:
            related = self.health_graph.get_related_symptoms(symptom)
            for r in related:
                if r['symptom'] not in symptoms_lower:
                    related_symptoms.add(r['symptom'])

        # Record in history
        self.symptom_history.add_symptom_record(
            symptoms_lower,
            severity,
            {
                'remedies_count': len(remedies),
                'diets_count': len(diet_plans)
            }
        )

        return {
            'remedies': remedies[:10],  # Top 10 remedies
            'diet_plans': diet_plans[:5],  # Top 5 diet plans
            'related_symptoms': list(related_symptoms)[:10]
        }

    def _find_remedy_by_name(self, name):
        """Find remedy data by name"""
        for remedy in self.remedies_data:
            if remedy['name'].lower() == name.lower():
                return remedy
        return None

    def _find_diet_by_name(self, name):
        """Find diet plan data by name"""
        for diet in self.diet_plans_data:
            if diet['name'].lower() == name.lower():
                return diet
        return None

    def get_all_symptoms(self):
        """Get all available symptoms"""
        return self.symptom_trie.get_all_words()

    def get_symptom_history(self, limit=10):
        """Get recent symptom search history"""
        return self.symptom_history.get_history(limit)

    def get_symptom_frequency(self):
        """Get frequency of searched symptoms"""
        return self.symptom_history.get_symptom_frequency()

    def get_remedy_details(self, remedy_name):
        """Get detailed information about a specific remedy"""
        return self._find_remedy_by_name(remedy_name)

    def get_diet_details(self, diet_name):
        """Get detailed information about a specific diet plan"""
        return self._find_diet_by_name(diet_name)

    def get_all_remedies(self):
        """Get all remedies sorted by effectiveness"""
        return self.remedy_bst.get_all_sorted()

    def get_all_diet_plans(self):
        """Get all diet plans sorted by effectiveness"""
        return self.diet_bst.get_all_sorted()

    def search_by_ingredient(self, ingredient):
        """Search remedies by ingredient"""
        results = []
        ingredient_lower = ingredient.lower()

        for remedy in self.remedies_data:
            ingredients = remedy.get('ingredients', [])
            for ing in ingredients:
                if ingredient_lower in ing.lower():
                    results.append(remedy)
                    break

        return results

    def search_by_food(self, food):
        """Search diet plans by food"""
        results = []
        food_lower = food.lower()

        for diet in self.diet_plans_data:
            foods_to_eat = diet.get('foods_to_eat', [])
            for f in foods_to_eat:
                if food_lower in f.lower():
                    results.append(diet)
                    break

        return results


# Singleton instance
_engine_instance = None


def get_recommendation_engine():
    """Get or create the recommendation engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RecommendationEngine()
    return _engine_instance
