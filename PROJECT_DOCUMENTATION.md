# 📘 PROJECT DOCUMENTATION

## Clinical Trial Eligibility Matching using NLP with Privacy Preservation

## 1. Project Overview

### 1.1 Project Title

**Clinical Trial Eligibility Matching using Natural Language Processing with Privacy Preservation**

### 1.2 Problem Statement

Clinical trials define eligibility criteria in unstructured natural language text.
Similarly, patient medical records are often stored as free-text clinical notes.
Manually matching patients to appropriate clinical trials is:

- Time-consuming
- Error-prone
- Not scalable
- Highly dependent on human expertise

Additionally, clinical data contains sensitive personal information, making privacy preservation essential.

### 1.3 Objective

The objective of this project is to design and implement an NLP-based system that:

- Automatically matches patient clinical text with clinical trial eligibility criteria
- Determines eligibility using similarity and classification models
- Preserves patient privacy by anonymizing sensitive information
- Uses techniques aligned with the college NLP syllabus while integrating modern approaches

## 2. Scope of the Project

### In Scope

- Text-based eligibility matching
- Classical NLP + ML models
- Optional transformer-based enhancement
- Local processing (privacy-safe)
- Explainable outputs

### Out of Scope

- Real-time hospital integration
- Image-based medical data
- Federated learning (only theoretical mention)
- Live clinical deployment

## 3. Real-World Use Cases

This system can be used in:

- Hospitals for clinical trial recruitment
- Research institutions
- Pharmaceutical companies
- Medical research platforms
- Healthcare decision-support systems

## 4. System Architecture

### 4.1 High-Level Architecture

```
Patient Clinical Notes
        |
[ Privacy & Anonymization Module ]
        |
[ Text Preprocessing Module ]
        |
[ Feature Representation Module ]
        |
[ Similarity / Classification Engine ]
        |
[ Eligibility Decision Module ]
        |
Eligibility Score + Explanation
```

## 5. Detailed Module Description

### 5.1 Data Collection Module

#### 5.1.1 Type of Data Required

The system requires textual medical data only.

**A. Clinical Trial Eligibility Criteria (Text)**

Examples:

- "Patients aged 18–65 with Type 2 Diabetes"
- "No history of cardiovascular disease"
- "HbA1c > 7%"

**B. Patient Clinical Notes (Text)**

Examples:

- Diagnosis summaries
- Discharge notes
- Medical history descriptions

#### 5.1.2 Dataset Source

For ethical and legal reasons, the project uses:

- Synthetic clinical data (manually curated)
- Optional publicly available sample data
- No real patient-identifiable data

This ensures complete privacy compliance.

### 5.2 Privacy Preservation Module

#### 5.2.1 Why Privacy Is Needed

Clinical data contains:

- Names
- Dates
- Locations
- Identifiers
- Sensitive medical conditions

#### 5.2.2 Privacy Techniques Used

- Rule-based anonymization
- Named entity masking
- Replacement tokens

**Example:**

```
"John Doe, 54 years old, diagnosed with diabetes"
↓
"PATIENT_NAME, AGE, diagnosed with diabetes"
```

No raw sensitive text is stored or shared.

### 5.3 Text Preprocessing Module (Unit I)

This module prepares text for modeling.

**Techniques Used:**

- Lowercasing
- Tokenization
- Stopword removal
- Lemmatization
- Stemming (optional)
- Noise removal

This step reduces variability and improves model accuracy.

### 5.4 Feature Representation Module (Unit I & II)

This module converts text into numerical form.

**Methods Used:**

- TF-IDF Vectorization
- Vector Space Model representation

Each patient note and trial criterion is represented as a vector in high-dimensional space.

### 5.5 Similarity Matching Module (Unit II)

This module calculates similarity between:

- Patient vector
- Trial eligibility vector

**Technique:**

- Cosine similarity

**Output:**

- Similarity score between 0 and 1
- Higher similarity indicates higher eligibility likelihood.

### 5.6 Classification Module (Unit IV)

Instead of relying only on similarity, a classification model is used.

**Models Used:**

- Logistic Regression
- Naive Bayes (baseline)

**Input:**

- TF-IDF vectors
- Similarity scores

**Output:**

- Eligible / Not Eligible
- Probability score

### 5.7 Sequence & Entity Modeling (Optional – Unit V)

This module enhances understanding of medical text.

**Techniques:**

- Named Entity Recognition (NER)
- Identification of:
  - Diseases
  - Age
  - Conditions
  - Measurements

NER helps highlight why a patient is or isn't eligible.

### 5.8 Transformer-Based Enhancement (Optional – Unit VI)

For advanced performance:

- BERT / ClinicalBERT embeddings
- Transfer learning

Used only as an enhancement, not core dependency.

## 6. Model Training Strategy

### 6.1 Where Models Are Trained

- Local machine (CPU/GPU)
- Jupyter Notebook / Python scripts
- No cloud APIs (privacy preservation)

### 6.2 Training Data

- Synthetic labeled data
- Manual labeling:
  - Eligible (1)
  - Not Eligible (0)

### 6.3 Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1-score

## 7. Tools & Technologies Used

| Category      | Tools                  |
| ------------- | ---------------------- |
| Programming   | Python                 |
| NLP Libraries | NLTK, spaCy            |
| ML            | scikit-learn           |
| Transformers  | HuggingFace (optional) |
| Visualization | Matplotlib, PCA        |
| Data          | Pandas, NumPy          |

## 8. Expected Output

- Eligibility classification
- Probability score
- Similarity explanation
- Highlighted important terms

**Example Output:**

```
Patient: Eligible
Score: 0.84
Matched Conditions: Diabetes, Age Range
```

## 9. Advantages of the System

- Automates trial matching
- Reduces human error
- Preserves privacy
- Explainable results
- Syllabus-aligned
- Industry-relevant

## 10. Limitations

- Synthetic data
- Limited clinical complexity
- Rule-based privacy masking
- Not a real medical diagnosis tool

## 11. Future Enhancements

- Larger datasets
- RAG-based matching
- Federated learning
- Differential privacy
- Multilingual support
- Real hospital integration

## 12. Conclusion

This project demonstrates the practical application of Natural Language Processing techniques to solve a real-world healthcare problem while preserving data privacy.

By combining classical NLP methods with modern models, the system provides an effective and scalable solution for clinical trial eligibility matching.

```
clinical-trial-matching/
│
├── data/
│   ├── patients/                # Raw & anonymized patient JSON
│   ├── trials/                  # Clinical trial JSON
│   ├── pairs/                   # Training pairs with labels
│   └── processed/               # Preprocessed text & TF-IDF vectors
│
├── src/
│   ├── __init__.py
│   ├── privacy/
│   │   ├── anonymizer.py        # Rule-based privacy masking
│   │   └── validators.py        # Ensures JSON is clean & safe
│   │
│   ├── preprocessing/
│   │   ├── text_cleaner.py      # Lowercase, punctuation removal, etc.
│   │   ├── tokenizer.py         # Tokenization + lemmatization
│   │   └── stopwords.py         # Custom stopword list (medical)
│   │
│   ├── features/
│   │   ├── tfidf_vectorizer.py  # Fit + transform TF-IDF
│   │   └── similarity.py        # Cosine similarity functions
│   │
│   ├── models/
│   │   ├── train_classifier.py  # LogisticRegression + Naive Bayes
│   │   ├── predict.py           # Unified prediction pipeline
│   │   └── explain.py           # NER-based explanation
│   │
│   ├── utils/
│   │   ├── json_loader.py       # Reads/writes JSON safely
│   │   ├── logger.py            # Logs for debugging & reproducibility
│   │   └── config.py            # Configurations & paths
│   │
│   └── app/
│       ├── interface.py         # CLI interface
│       └── web_app.py           # Flask/FastAPI interface (optional)
│
├── models/
│   ├── tfidf.pkl                # Saved TF-IDF model
│   ├── classifier.pkl           # Saved Logistic Regression model
│   └── vectorizer_config.json   # Parameters & metadata
│
├── notebooks/
│   ├── EDA.ipynb                # Data exploration
│   ├── training.ipynb           # Training + evaluation
│   └── explainability.ipynb     # NER testing + case studies
│
├── docs/
│   ├── architecture-diagram.png
│   ├── workflow-diagram.png
│   └── report/ (optional research paper files)
│
├── requirements.txt
├── README.md
└── run.py                       # Main entry point for pipeline
```