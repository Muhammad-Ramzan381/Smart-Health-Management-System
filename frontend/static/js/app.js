/**
 * Smart Health Management System - Main JavaScript
 * Handles symptom input, autocomplete, and recommendations
 */

// API Base URL
const API_BASE = '/api';

// State Management
const state = {
    selectedSymptoms: [],
    severity: 5,
    recommendations: null,
    isLoading: false
};

// DOM Elements
let symptomInput, autocompleteList, symptomsContainer, severitySlider, severityValue;
let remediesContainer, dietPlansContainer, relatedSymptomsContainer;
let analyzeBtn, clearBtn, resultsSection;

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    setupEventListeners();
    loadAllSymptoms();
});

function initializeElements() {
    symptomInput = document.getElementById('symptom-input');
    autocompleteList = document.getElementById('autocomplete-list');
    symptomsContainer = document.getElementById('selected-symptoms');
    severitySlider = document.getElementById('severity-slider');
    severityValue = document.getElementById('severity-value');
    remediesContainer = document.getElementById('remedies-container');
    dietPlansContainer = document.getElementById('diet-plans-container');
    relatedSymptomsContainer = document.getElementById('related-symptoms');
    analyzeBtn = document.getElementById('analyze-btn');
    clearBtn = document.getElementById('clear-btn');
    resultsSection = document.getElementById('results-section');
}

function setupEventListeners() {
    // Symptom Input
    if (symptomInput) {
        symptomInput.addEventListener('input', handleSymptomInput);
        symptomInput.addEventListener('keydown', handleInputKeydown);
        symptomInput.addEventListener('focus', () => {
            if (symptomInput.value.length >= 1) {
                fetchAutocomplete(symptomInput.value);
            }
        });
    }

    // Severity Slider
    if (severitySlider) {
        severitySlider.addEventListener('input', handleSeverityChange);
    }

    // Buttons
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeSymptoms);
    }
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAll);
    }

    // Close autocomplete on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.autocomplete-container')) {
            hideAutocomplete();
        }
    });

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.nav');
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', () => {
            nav.classList.toggle('show');
        });
    }
}

// ==================== Autocomplete ====================
let autocompleteTimeout;
let highlightedIndex = -1;

function handleSymptomInput(e) {
    const value = e.target.value.trim();

    clearTimeout(autocompleteTimeout);

    if (value.length < 1) {
        hideAutocomplete();
        return;
    }

    autocompleteTimeout = setTimeout(() => {
        fetchAutocomplete(value);
    }, 200);
}

async function fetchAutocomplete(prefix) {
    try {
        const response = await fetch(`${API_BASE}/autocomplete?prefix=${encodeURIComponent(prefix)}&max=8`);
        const data = await response.json();

        if (data.suggestions && data.suggestions.length > 0) {
            showAutocomplete(data.suggestions);
        } else {
            hideAutocomplete();
        }
    } catch (error) {
        console.error('Autocomplete error:', error);
        hideAutocomplete();
    }
}

function showAutocomplete(suggestions) {
    if (!autocompleteList) return;

    // Filter out already selected symptoms
    const filtered = suggestions.filter(s => !state.selectedSymptoms.includes(s.toLowerCase()));

    if (filtered.length === 0) {
        hideAutocomplete();
        return;
    }

    autocompleteList.innerHTML = filtered.map((symptom, index) => `
        <div class="autocomplete-item" data-symptom="${symptom}" data-index="${index}">
            ${capitalizeFirst(symptom)}
        </div>
    `).join('');

    // Add click handlers
    autocompleteList.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
            addSymptom(item.dataset.symptom);
            symptomInput.value = '';
            hideAutocomplete();
        });
    });

    autocompleteList.classList.add('show');
    highlightedIndex = -1;
}

function hideAutocomplete() {
    if (autocompleteList) {
        autocompleteList.classList.remove('show');
        highlightedIndex = -1;
    }
}

function handleInputKeydown(e) {
    const items = autocompleteList?.querySelectorAll('.autocomplete-item') || [];

    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            highlightedIndex = Math.min(highlightedIndex + 1, items.length - 1);
            updateHighlight(items);
            break;
        case 'ArrowUp':
            e.preventDefault();
            highlightedIndex = Math.max(highlightedIndex - 1, -1);
            updateHighlight(items);
            break;
        case 'Enter':
            e.preventDefault();
            if (highlightedIndex >= 0 && items[highlightedIndex]) {
                addSymptom(items[highlightedIndex].dataset.symptom);
                symptomInput.value = '';
                hideAutocomplete();
            } else if (symptomInput.value.trim()) {
                addSymptom(symptomInput.value.trim());
                symptomInput.value = '';
                hideAutocomplete();
            }
            break;
        case 'Escape':
            hideAutocomplete();
            break;
    }
}

function updateHighlight(items) {
    items.forEach((item, index) => {
        item.classList.toggle('highlighted', index === highlightedIndex);
    });
}

// ==================== Symptom Management ====================
function addSymptom(symptom) {
    const normalized = symptom.toLowerCase().trim();

    if (!normalized || state.selectedSymptoms.includes(normalized)) {
        return;
    }

    state.selectedSymptoms.push(normalized);
    renderSelectedSymptoms();
    updateAnalyzeButton();
}

function removeSymptom(symptom) {
    state.selectedSymptoms = state.selectedSymptoms.filter(s => s !== symptom);
    renderSelectedSymptoms();
    updateAnalyzeButton();
}

function renderSelectedSymptoms() {
    if (!symptomsContainer) return;

    if (state.selectedSymptoms.length === 0) {
        symptomsContainer.innerHTML = '<p class="text-center" style="color: var(--text-light);">No symptoms selected</p>';
        return;
    }

    symptomsContainer.innerHTML = state.selectedSymptoms.map(symptom => `
        <span class="tag tag-primary">
            ${capitalizeFirst(symptom)}
            <button class="tag-remove" onclick="removeSymptom('${symptom}')">&times;</button>
        </span>
    `).join('');
}

function updateAnalyzeButton() {
    if (analyzeBtn) {
        analyzeBtn.disabled = state.selectedSymptoms.length === 0;
    }
}

// ==================== Severity ====================
function handleSeverityChange(e) {
    state.severity = parseInt(e.target.value);
    if (severityValue) {
        severityValue.textContent = state.severity;
        updateSeverityColor();
    }
}

function updateSeverityColor() {
    if (!severityValue) return;

    if (state.severity <= 3) {
        severityValue.style.color = 'var(--success-color)';
    } else if (state.severity <= 6) {
        severityValue.style.color = 'var(--warning-color)';
    } else {
        severityValue.style.color = 'var(--danger-color)';
    }
}

// ==================== Analysis & Recommendations ====================
async function analyzeSymptoms() {
    if (state.selectedSymptoms.length === 0) {
        showAlert('Please select at least one symptom', 'warning');
        return;
    }

    setLoading(true);

    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symptoms: state.selectedSymptoms,
                severity: state.severity
            })
        });

        const data = await response.json();

        if (data.success) {
            state.recommendations = data.recommendations;
            renderRecommendations();
            showResultsSection();
        } else {
            showAlert(data.error || 'Analysis failed', 'danger');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showAlert('Failed to analyze symptoms. Please try again.', 'danger');
    } finally {
        setLoading(false);
    }
}

function renderRecommendations() {
    renderRemedies();
    renderDietPlans();
    renderRelatedSymptoms();
}

function renderRemedies() {
    if (!remediesContainer || !state.recommendations) return;

    const remedies = state.recommendations.remedies || [];

    if (remedies.length === 0) {
        remediesContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <p>No home remedies found for these symptoms</p>
            </div>
        `;
        return;
    }

    remediesContainer.innerHTML = remedies.map((remedy, index) => `
        <div class="recommendation-card remedy">
            <div class="recommendation-header">
                <h3 class="recommendation-title">🌿 ${remedy.name}</h3>
                <span class="effectiveness-badge">
                    ⭐ ${remedy.effectiveness}/10
                </span>
            </div>
            <p class="recommendation-description">${remedy.description}</p>
            <button class="btn btn-sm btn-outline" onclick="toggleDetails('remedy-${index}')">
                View Details
            </button>
            <div id="remedy-${index}" class="recommendation-details">
                <div class="detail-section">
                    <h4 class="detail-title">📝 Ingredients</h4>
                    <ul class="detail-list">
                        ${remedy.ingredients.map(ing => `<li>${ing}</li>`).join('')}
                    </ul>
                </div>
                <div class="detail-section">
                    <h4 class="detail-title">👨‍🍳 Preparation</h4>
                    <p>${remedy.preparation}</p>
                </div>
                <div class="detail-section">
                    <h4 class="detail-title">⏱️ Time to Effect</h4>
                    <p>${remedy.time_to_effect}</p>
                </div>
                <div class="detail-section">
                    <h4 class="detail-title">⚠️ Safety Notes</h4>
                    <p>${remedy.safety_notes}</p>
                </div>
            </div>
        </div>
    `).join('');
}

function renderDietPlans() {
    if (!dietPlansContainer || !state.recommendations) return;

    const dietPlans = state.recommendations.diet_plans || [];

    if (dietPlans.length === 0) {
        dietPlansContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🥗</div>
                <p>No diet plans found for these symptoms</p>
            </div>
        `;
        return;
    }

    dietPlansContainer.innerHTML = dietPlans.map((diet, index) => `
        <div class="recommendation-card diet">
            <div class="recommendation-header">
                <h3 class="recommendation-title">🥗 ${diet.name}</h3>
                <span class="effectiveness-badge">
                    ⭐ ${diet.effectiveness}/10
                </span>
            </div>
            <p class="recommendation-description">${diet.description}</p>
            <button class="btn btn-sm btn-outline" onclick="toggleDetails('diet-${index}')">
                View Details
            </button>
            <div id="diet-${index}" class="recommendation-details">
                <div class="foods-grid">
                    <div class="foods-eat">
                        <h4 class="detail-title">✅ Foods to Eat</h4>
                        <ul class="detail-list">
                            ${diet.foods_to_eat.map(food => `<li>${food}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="foods-avoid">
                        <h4 class="detail-title">❌ Foods to Avoid</h4>
                        <ul class="detail-list">
                            ${diet.foods_to_avoid.map(food => `<li>${food}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="detail-section mt-2">
                    <h4 class="detail-title">🍽️ Meal Suggestions</h4>
                    <ul class="detail-list">
                        <li><strong>Breakfast:</strong> ${diet.meal_suggestions.breakfast}</li>
                        <li><strong>Lunch:</strong> ${diet.meal_suggestions.lunch}</li>
                        <li><strong>Dinner:</strong> ${diet.meal_suggestions.dinner}</li>
                        <li><strong>Snacks:</strong> ${diet.meal_suggestions.snacks}</li>
                    </ul>
                </div>
                <div class="detail-section">
                    <h4 class="detail-title">⏱️ Duration</h4>
                    <p>${diet.duration}</p>
                </div>
            </div>
        </div>
    `).join('');
}

function renderRelatedSymptoms() {
    if (!relatedSymptomsContainer || !state.recommendations) return;

    const related = state.recommendations.related_symptoms || [];

    if (related.length === 0) {
        relatedSymptomsContainer.innerHTML = '';
        return;
    }

    relatedSymptomsContainer.innerHTML = `
        <div class="card">
            <h3 class="card-title">🔗 Related Symptoms</h3>
            <p style="color: var(--text-light); margin-bottom: 1rem;">
                You might also want to check these related symptoms:
            </p>
            <div class="tags-container">
                ${related.map(symptom => `
                    <span class="tag tag-success" style="cursor: pointer;" onclick="addSymptom('${symptom}')">
                        + ${capitalizeFirst(symptom)}
                    </span>
                `).join('')}
            </div>
        </div>
    `;
}

function toggleDetails(id) {
    const details = document.getElementById(id);
    if (details) {
        details.classList.toggle('show');
    }
}

function showResultsSection() {
    if (resultsSection) {
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ==================== Utility Functions ====================
function clearAll() {
    state.selectedSymptoms = [];
    state.severity = 5;
    state.recommendations = null;

    if (symptomInput) symptomInput.value = '';
    if (severitySlider) severitySlider.value = 5;
    if (severityValue) {
        severityValue.textContent = '5';
        severityValue.style.color = 'var(--warning-color)';
    }

    renderSelectedSymptoms();
    updateAnalyzeButton();

    if (resultsSection) {
        resultsSection.classList.add('hidden');
    }

    hideAutocomplete();
}

function setLoading(loading) {
    state.isLoading = loading;

    if (analyzeBtn) {
        analyzeBtn.disabled = loading || state.selectedSymptoms.length === 0;
        analyzeBtn.innerHTML = loading
            ? '<span class="spinner" style="width: 20px; height: 20px;"></span> Analyzing...'
            : '🔍 Analyze Symptoms';
    }
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = message;

    // Insert at top of main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(alert, mainContent.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

async function loadAllSymptoms() {
    try {
        const response = await fetch(`${API_BASE}/symptoms`);
        const data = await response.json();
        console.log('Available symptoms:', data.symptoms?.length);
    } catch (error) {
        console.error('Failed to load symptoms:', error);
    }
}

// Make functions globally available
window.removeSymptom = removeSymptom;
window.addSymptom = addSymptom;
window.toggleDetails = toggleDetails;
