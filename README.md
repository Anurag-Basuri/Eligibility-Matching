# 🧪 Clinical Trial Eligibility Matching

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A privacy-preserving NLP-based system for automatically matching patients to clinical trials based on eligibility criteria. Built with classical NLP techniques, machine learning classifiers, and an interactive Streamlit interface.

---

## 📋 Table of Contents

-   [Overview](#overview)
-   [Features](#features)
-   [Project Structure](#project-structure)
-   [Installation](#installation)
-   [Quick Start](#quick-start)
-   [Data Schemas](#data-schemas)
-   [Pipeline Details](#pipeline-details)
-   [Web Application](#web-application)
-   [Troubleshooting](#troubleshooting)
-   [Development](#development)
-   [Future Enhancements](#future-enhancements)

---

## Overview

Clinical trials define eligibility criteria in unstructured natural language. Manually matching patients to appropriate trials is time-consuming, error-prone, and not scalable. This system automates the process using:

-   **TF-IDF vectorization** for text representation
-   **Machine learning classifiers** (Logistic Regression, Naive Bayes)
-   **Rule-based explanations** for transparency
-   **Privacy preservation** through text anonymization

### Problem Solved

| Challenge                         | Solution                         |
| --------------------------------- | -------------------------------- |
| Unstructured eligibility criteria | NLP preprocessing + TF-IDF       |
| Manual matching errors            | ML-based classification          |
| Privacy concerns                  | Runtime anonymization            |
| Black-box predictions             | Explainable rule-based reasoning |

---

## Features

-   ✅ **Automatic eligibility prediction** — ML model predicts patient-trial compatibility
-   ✅ **Privacy-preserving** — Names and ages anonymized before processing
-   ✅ **Explainable AI** — Rule-based breakdown of eligibility decisions
-   ✅ **Balanced synthetic data** — Generator creates realistic patient-trial pairs
-   ✅ **Interactive UI** — Streamlit app for single match, batch analysis, and statistics
-   ✅ **Modular architecture** — Clean separation of concerns

---

## Project Structure

```
clinical-trial-matching/
├── data/
│   ├── patients/                 # Patient JSON files (P_BAL_*.json)
│   ├── trials/                   # Trial JSON files (T001.json - T010.json)
│   └── pairs/                    # Patient-Trial pairs with labels
├── models/                       # Trained models (gitignored)
│   ├── tfidf.pkl                 # TF-IDF vectorizer
│   └── classifier.pkl            # Best classifier model
├── src/
│   ├── app/
│   │   └── streamlit_app.py      # Web interface
│   ├── features/
│   │   └── tfidf_vectorizer.py   # TF-IDF wrapper class
│   ├── models/
│   │   └── train_classifier.py   # Model training & evaluation
│   ├── preprocessing/
│   │   ├── __init__.py           # Preprocessing pipeline
│   │   ├── text_cleaner.py       # Text normalization
│   │   └── tokenizer.py          # spaCy-based tokenization
│   ├── privacy/
│   │   └── anonymizer.py         # PII anonymization
│   └── utils/
│       ├── balancer.py           # Dataset balancing
│       ├── generate_pairs.py     # Pair generation utility
│       ├── json_loader.py        # Data loading functions
│       └── synthetic_data_generator.py  # Synthetic patient generator
├── docs/                         # Additional documentation
├── notebooks/                    # Jupyter notebooks for exploration
├── run.py                        # Basic feature extraction script
├── run_pipeline.py               # Full training pipeline
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
├── PROJECT_DOCUMENTATION.md      # Detailed project documentation
└── README.md                     # This file
```

---

## Installation

### Prerequisites

-   Python 3.11 or higher
-   pip package manager

### Setup

```powershell
# Clone the repository
git clone <repository-url>
cd clinical-trial-matching

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Windows PowerShell
# source .venv/bin/activate     # Linux/macOS

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### Verify Installation

```powershell
python -c "import sklearn; import spacy; import streamlit; print('All dependencies installed!')"
```

### Dependencies

See [requirements.txt](requirements.txt) for the full list. Key packages:

| Package      | Version | Purpose                            |
| ------------ | ------- | ---------------------------------- |
| scikit-learn | ≥1.0.0  | ML models, TF-IDF vectorization    |
| spacy        | ≥3.0.0  | NLP tokenization and lemmatization |
| streamlit    | ≥1.20.0 | Web application interface          |
| pandas       | ≥1.3.0  | Data manipulation                  |
| numpy        | ≥1.20.0 | Numerical operations               |
| scipy        | ≥1.7.0  | Sparse matrix support              |

---

## Quick Start

### 1. Generate Synthetic Data

```powershell
python .\src\utils\synthetic_data_generator.py
```

**Output:**

-   160 patient files in `data/patients/`
-   1600 pair files in `data/pairs/` (160 patients × 10 trials)
-   ~50% eligible, ~50% not eligible (balanced)

### 2. Train the Model

```powershell
python .\run_pipeline.py
```

**Output:**

```
========== CLINICAL TRIAL MATCHING PIPELINE ==========

🔹 Loading data...
Patients loaded : 160
Trials loaded   : 10
Pairs loaded    : 1600

🔹 Preparing training samples...
✅ Valid samples used : 1600

🔹 Balancing dataset at pair level...
Balanced samples: 800
Eligible ratio: 50.00%

🔹 Vectorizing text with TF-IDF...
✅ TF-IDF complete
Feature matrix shape: (800, 5000)
💾 TF-IDF vectorizer saved

🔹 Training and evaluating classifiers...

📊 MODEL: LOGISTIC_REGRESSION
Accuracy : 0.85
Precision: 0.84
Recall   : 0.86
F1-score : 0.85

📊 MODEL: NAIVE_BAYES
Accuracy : 0.82
...

💾 Best model saved: logistic_regression

========== PIPELINE COMPLETE ==========
```

### 3. Run the Web Application

```powershell
streamlit run .\src\app\streamlit_app.py
```

Open http://localhost:8501 in your browser.

---

## Data Schemas

### Patient (`data/patients/P_BAL_*.json`)

```json
{
	"patient_id": "P_BAL_001",
	"raw_text": "Patient is a 45-year-old female with type 2 diabetes and hypertension. No history of cancer.",
	"metadata": {
		"age": 45,
		"gender": "female",
		"conditions": ["type 2 diabetes", "hypertension"],
		"negated_conditions": ["cancer"],
		"source": "balanced_160_patients_v1"
	}
}
```

### Trial (`data/trials/T001.json`)

```json
{
	"trial_id": "T001",
	"eligibility_text": "Eligible patients are adults aged 18 to 65 diagnosed with type 2 diabetes and with no history of cardiovascular disease or cancer.",
	"criteria": {
		"min_age": 18,
		"max_age": 65,
		"required_conditions": ["type 2 diabetes"],
		"excluded_conditions": ["cardiovascular disease", "cancer"]
	}
}
```

### Pair (`data/pairs/P_BAL_001_T001.json`)

```json
{
	"pair_id": "P_BAL_001_T001",
	"patient_id": "P_BAL_001",
	"trial_id": "T001",
	"label": 1,
	"reason": "Controlled balanced generation"
}
```

---

## Pipeline Details

### Eligibility Logic

A patient is **Eligible** (`label = 1`) if ALL conditions are met:

| Rule                | Description                                                 |
| ------------------- | ----------------------------------------------------------- |
| Age Range           | `min_age ≤ patient_age ≤ max_age`                           |
| Required Conditions | Patient has ALL conditions in `required_conditions`         |
| Excluded Conditions | Patient has NONE of the conditions in `excluded_conditions` |

If any rule fails → **Not Eligible** (`label = 0`)

### Processing Pipeline

```
Patient Text + Trial Text
        │
        ▼
┌─────────────────────────┐
│  Privacy Anonymization  │  Names → PATIENT_NAME, Ages → AGE
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│   Text Preprocessing    │  Lowercase, clean, tokenize, lemmatize
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│   TF-IDF Vectorization  │  Unigrams + Bigrams, max 5000 features
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│   ML Classification     │  Logistic Regression / Naive Bayes
└───────────┬─────────────┘
            ▼
    Eligible / Not Eligible
```

### Available Trials (T001–T010)

| Trial | Required Condition       | Age Range | Excluded                              |
| ----- | ------------------------ | --------- | ------------------------------------- |
| T001  | type 2 diabetes          | 18-65     | cardiovascular disease, cancer        |
| T002  | hypertension             | 50-80     | stroke, myocardial infarction         |
| T003  | PCOS                     | 18-45     | pregnancy, cancer                     |
| T004  | osteoarthritis           | 60-80     | stroke, cancer                        |
| T005  | depression               | 18-55     | schizophrenia, bipolar disorder       |
| T006  | COPD                     | 40-75     | cancer, tuberculosis                  |
| T007  | asthma                   | 18-50     | chronic kidney disease, heart disease |
| T008  | obesity, type 2 diabetes | 30-65     | cardiovascular disease, liver disease |
| T009  | anxiety                  | 21-40     | epilepsy, HIV/AIDS                    |
| T010  | Parkinson's disease      | 55-85     | Alzheimer's disease, cancer           |

---

## Web Application

### Features

| Tab                | Description                                                         |
| ------------------ | ------------------------------------------------------------------- |
| **Single Match**   | Select patient + trial, get eligibility prediction with explanation |
| **Batch Analysis** | Check one patient against ALL trials at once                        |
| **Statistics**     | View age distribution, gender breakdown, top conditions             |

### Screenshots

The app provides:

-   Patient/Trial cards with formatted summaries
-   Rule-based AND ML predictions side by side
-   Confidence score with progress bar
-   Color-coded eligibility breakdown table
-   Agreement check between rule-based and ML predictions

---

## Troubleshooting

| Issue                                          | Solution                                                                                   |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `ModuleNotFoundError: No module named 'src'`   | Run Streamlit from project root: `streamlit run .\src\app\streamlit_app.py`                |
| `X has N features, but model expects M`        | Re-run `python .\run_pipeline.py` after regenerating data                                  |
| `ModuleNotFoundError: No module named 'spacy'` | Run `pip install -r requirements.txt && python -m spacy download en_core_web_sm`           |
| `No module named 'en_core_web_sm'`             | Run `python -m spacy download en_core_web_sm`                                              |
| Pylance `reportMissingModuleSource`            | Select correct Python interpreter in VS Code (Ctrl+Shift+P → "Python: Select Interpreter") |
| Empty patients/pairs folders                   | Run `python .\src\utils\synthetic_data_generator.py` first                                 |

---

## Development

### Code Formatting

```powershell
# Python (Black)
pip install black
python -m black .

# JSON (Prettier)
npx prettier --write .\data\**\*.json
```

### Running Tests

```powershell
pip install pytest
pytest
```

### Adding New Trials

1. Create `data/trials/T0XX.json` following the schema
2. Regenerate patients/pairs:
    ```powershell
    python .\src\utils\synthetic_data_generator.py
    ```
3. Retrain models:
    ```powershell
    python .\run_pipeline.py
    ```

### Project Files (Git-tracked)

| File/Folder        | Tracked | Description                    |
| ------------------ | ------- | ------------------------------ |
| `src/`             | ✅      | All source code                |
| `data/trials/`     | ✅      | Trial definitions              |
| `data/patients/`   | ✅      | Synthetic patients             |
| `data/pairs/`      | ✅      | Labeled pairs                  |
| `requirements.txt` | ✅      | Python dependencies            |
| `LICENSE`          | ✅      | MIT License                    |
| `models/`          | ❌      | Trained models (regeneratable) |
| `.venv/`           | ❌      | Virtual environment            |
| `__pycache__/`     | ❌      | Python cache                   |

---

## Future Enhancements

-   [ ] BERT/ClinicalBERT embeddings for better semantic understanding
-   [ ] Support for complex eligibility criteria (lab values, medications)
-   [ ] Multi-trial ranking for a single patient
-   [ ] REST API endpoint for system integration
-   [ ] Docker containerization
-   [ ] Differential privacy techniques
-   [ ] Multilingual support

---

## Technologies Used

| Category | Tools                |
| -------- | -------------------- |
| Language | Python 3.11+         |
| NLP      | spaCy, NLTK concepts |
| ML       | scikit-learn         |
| Web UI   | Streamlit            |
| Data     | Pandas, NumPy, JSON  |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## References

-   See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for detailed system design and module descriptions.
