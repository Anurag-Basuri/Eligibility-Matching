import pickle
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


def train_and_evaluate(X, y):
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results = {}

    # ----------------------------
    # Logistic Regression
    # ----------------------------
    lr = LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    )
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)

    results["logistic_regression"] = {
        "model": lr,
        "accuracy": accuracy_score(y_test, y_pred_lr),
        "precision": precision_score(y_test, y_pred_lr),
        "recall": recall_score(y_test, y_pred_lr),
        "f1": f1_score(y_test, y_pred_lr),
        "confusion_matrix": confusion_matrix(y_test, y_pred_lr),
        "report": classification_report(y_test, y_pred_lr),
    }

    # ----------------------------
    # Naive Bayes
    # ----------------------------
    nb = MultinomialNB()
    nb.fit(X_train, y_train)
    y_pred_nb = nb.predict(X_test)

    results["naive_bayes"] = {
        "model": nb,
        "accuracy": accuracy_score(y_test, y_pred_nb),
        "precision": precision_score(y_test, y_pred_nb),
        "recall": recall_score(y_test, y_pred_nb),
        "f1": f1_score(y_test, y_pred_nb),
        "confusion_matrix": confusion_matrix(y_test, y_pred_nb),
        "report": classification_report(y_test, y_pred_nb),
    }

    return results
