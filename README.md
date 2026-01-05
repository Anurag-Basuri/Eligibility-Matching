# 🧪 Clinical Trial Eligibility Matching

A privacy-preserving NLP-based system for matching patients to clinical trials based on eligibility criteria.

## 📋 Overview

This application uses machine learning to predict whether a patient is eligible for a clinical trial based on:

-   Patient demographics (age, gender)
-   Medical conditions
-   Trial eligibility criteria (age range, required/excluded conditions)

### Key Features

-   **Privacy-preserving**: Patient names and identifying information are anonymized before processing
-   **Explainable AI**: Provides human-readable explanations for eligibility decisions
-   **Balanced synthetic data generation**: Creates realistic patient-trial pairs for training
-   **Interactive UI**: Streamlit-based web interface for real-time predictions

---

## 🗂️ Project Structure

```
clinical-trial-matching/
├── data/
│   ├── patients/          # Patient JSON files
│   ├── trials/            # Trial JSON files
│   └── pairs/             # Patient-Trial pair files with labels
├── models/
│   ├── tfidf.pkl          # Trained TF-IDF vectorizer
│   └── classifier.pkl     # Trained classifier model
├── src/
│   ├── app/
│   │   └── streamlit_app.py    # Streamlit web interface
│   ├── features/
│   │   └── tfidf_vectorizer.py # TF-IDF feature extraction
│   ├── models/
│   │   └── train_classifier.py # Model training logic
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── text_cleaner.py     # Text cleaning utilities
│   │   └── tokenizer.py        # spaCy-based tokenization
│   ├── privacy/
│   │   └── anonymizer.py       # PII anonymization
│   └── utils/
│       ├── json_loader.py      # Data loading utilities
│       ├── balancer.py         # Dataset balancing
│       └── synthetic_data_generator.py  # Synthetic data generation
├── run.py                  # Basic feature extraction script
├── run_pipeline.py         # Full training pipeline
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone and Setup Environment

```powershell
# Clone the repository
git clone <repository-url>
cd clinical-trial-matching

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Generate Synthetic Data

```powershell
python .\src\utils\synthetic_data_generator.py
```

This creates:

-   Patient files in `data/patients/`
-   Pair files in `data/pairs/`
-   Balanced dataset with ~50% eligible, ~50% not eligible

### 3. Train the Model

```powershell
python .\run_pipeline.py
```

This will:

-   Load and preprocess data
-   Balance the dataset
-   Train TF-IDF vectorizer
-   Train and evaluate classifiers (Logistic Regression, Naive Bayes)
-   Save the best model to `models/`

### 4. Run the Web Application

```powershell
streamlit run .\src\app\streamlit_app.py
```

Open http://localhost:8501 in your browser.

---

## 📊 Data Schemas

### Patient (`data/patients/*.json`)

```json
{
	"patient_id": "P_BAL_00001",
	"raw_text": "Patient is a 45-year-old female with type 2 diabetes and hypertension.",
	"metadata": {
		"age": 45,
		"gender": "female",
		"conditions": ["type 2 diabetes", "hypertension"],
		"negated_conditions": ["cancer"],
		"source": "balanced_global_v1"
	}
}
```

### Trial (`data/trials/*.json`)

```json
{
	"trial_id": "T001",
	"eligibility_text": "Eligible patients are adults aged 18-65 with type 2 diabetes...",
	"criteria": {
		"min_age": 18,
		"max_age": 65,
		"required_conditions": ["type 2 diabetes"],
		"excluded_conditions": ["cardiovascular disease", "cancer"]
	}
}
```

### Pair (`data/pairs/*.json`)

```json
{
	"pair_id": "P_BAL_00001_T001",
	"patient_id": "P_BAL_00001",
	"trial_id": "T001",
	"label": 1,
	"reason": "Age 45 within [18-65]; has required: type 2 diabetes; none of excluded conditions present"
}
```

---

## 🔬 Eligibility Logic

A patient is **Eligible** (`label = 1`) if ALL of the following are true:

1. **Age**: `min_age ≤ patient_age ≤ max_age`
2. **Required conditions**: Patient has ALL conditions listed in `required_conditions`
3. **Excluded conditions**: Patient has NONE of the conditions listed in `excluded_conditions`

If any condition fails → **Not Eligible** (`label = 0`)

---

## 🛠️ Dependencies

| Package        | Purpose                            |
| -------------- | ---------------------------------- |
| `scikit-learn` | ML models, TF-IDF vectorization    |
| `spacy`        | NLP tokenization and lemmatization |
| `streamlit`    | Web application interface          |
| `numpy`        | Numerical operations               |
| `scipy`        | Sparse matrix support              |

### requirements.txt

```
scikit-learn>=1.0
spacy>=3.0
streamlit>=1.20
numpy>=1.20
scipy>=1.7
```

---

## 📈 Model Performance

The pipeline trains two classifiers and selects the best based on F1-score:

| Model               | Accuracy | Precision | Recall | F1-Score |
| ------------------- | -------- | --------- | ------ | -------- |
| Logistic Regression | ~0.85    | ~0.84     | ~0.86  | ~0.85    |
| Naive Bayes         | ~0.82    | ~0.81     | ~0.83  | ~0.82    |

_Results may vary based on generated data._

---

## 🔒 Privacy Features

-   **Name anonymization**: Patient names replaced with `PATIENT_NAME`
-   **Age anonymization**: Age patterns replaced with `AGE` token
-   **No PII storage**: Raw identifying information is never stored in models

---

## 🧪 Usage Examples

### Command Line

```powershell
# Generate 200 synthetic patients
python .\src\utils\synthetic_data_generator.py

# Retrain models after data changes
python .\run_pipeline.py

# Run web app
streamlit run .\src\app\streamlit_app.py
```

### Programmatic Usage

```python
from src.utils.json_loader import load_all_data
from src.privacy.anonymizer import anonymize
from src.preprocessing import preprocess

# Load data
patients, trials, pairs = load_all_data()

# Anonymize text
anon_text = anonymize(patient["raw_text"])

# Preprocess for model
processed = preprocess(anon_text + " " + trial["eligibility_text"])
```

---

## 🐛 Troubleshooting

| Issue                                          | Solution                                                           |
| ---------------------------------------------- | ------------------------------------------------------------------ |
| `ModuleNotFoundError: No module named 'src'`   | Run from project root: `streamlit run .\src\app\streamlit_app.py`  |
| `X has N features, but model expects M`        | Re-run `python .\run_pipeline.py` to retrain models                |
| `ModuleNotFoundError: No module named 'spacy'` | Run `pip install spacy && python -m spacy download en_core_web_sm` |
| Pylance `reportMissingModuleSource` warning    | Select correct Python interpreter in VS Code                       |

---

## 📝 Development

### Code Formatting

```powershell
# Python (Black)
python -m black .

# JSON (Prettier)
npx prettier --write .\data\**\*.json
```

### Adding New Trials

1. Create `data/trials/T0XX.json` following the schema
2. Regenerate pairs: `python .\src\utils\synthetic_data_generator.py`
3. Retrain models: `python .\run_pipeline.py`

---

## 📄 License

This project is for educational and research purposes.

---

## 👥 Contributors

-   Clinical Trial Matching Team

---

## 🔮 Future Enhancements

-   [ ] Add BERT-based embeddings for better semantic understanding
-   [ ] Support for more complex eligibility criteria (lab values, medications)
-   [ ] Multi-trial ranking for a single patient
-   [ ] REST API endpoint for integration
-   [ ] Docker containerization
