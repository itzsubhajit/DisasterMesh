
"""
DisasterMesh - Final Model Training

Selected algorithms:
1. Category: Calibrated Linear SVM
2. Priority: Calibrated Logistic Regression

Uses TF-IDF text features and sigmoid probability calibration.

These models are for prototype decision support only.
"""

import csv
import json

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import sklearn

from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    BACKEND_DIR
    / "app"
    / "ai"
    / "data"
    / "emergency_dataset.csv"
)

ARTIFACT_DIR = BACKEND_DIR / "artifacts"

RANDOM_STATE = 42
TEST_SIZE = 0.25
CALIBRATION_FOLDS = 5


# ---------------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------------

def load_dataset():

    texts = []
    categories = []
    priorities = []

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV header is missing.")

        reader.fieldnames = [
            name.strip().lower()
            for name in reader.fieldnames
        ]

        required = {
            "text",
            "category",
            "priority",
        }

        if not required.issubset(reader.fieldnames):
            raise ValueError(
                "Required columns: text, category, priority"
            )

        for row_number, row in enumerate(reader, start=2):

            text = (row.get("text") or "").strip()
            category = (row.get("category") or "").strip()
            priority = (row.get("priority") or "").strip().upper()

            if not text and not category and not priority:
                continue

            if not text or not category or not priority:
                raise ValueError(
                    f"Missing value at row {row_number}"
                )

            texts.append(text)
            categories.append(category)
            priorities.append(priority)

    if not texts:
        raise ValueError("Dataset is empty.")

    return texts, categories, priorities


# ---------------------------------------------------------
# BUILD CLASSIFIER
# ---------------------------------------------------------

def build_classifier(task_name):

    if task_name == "category":

        classifier = LinearSVC(
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )

    elif task_name == "priority":

        classifier = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )

    else:
        raise ValueError("Unknown classification task.")

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=(1, 2),
                min_df=1,
                sublinear_tf=True,
            ),
        ),
        ("classifier", classifier),
    ])

    return CalibratedClassifierCV(
        estimator=pipeline,
        method="sigmoid",
        cv=CALIBRATION_FOLDS,
    )


# ---------------------------------------------------------
# TRAIN AND EVALUATE
# ---------------------------------------------------------

def train_task(
    texts,
    labels,
    task_name,
    display_name,
    output_filename,
):

    print("\n" + "=" * 65)
    print("TRAINING:", display_name)
    print("=" * 65)

    distribution = Counter(labels)

    print("\nClass distribution:")

    for name, count in sorted(distribution.items()):
        print(f"{name}: {count}")

    if min(distribution.values()) < CALIBRATION_FOLDS:
        raise ValueError(
            "Not enough examples per class for calibration."
        )

    # Separate evaluation data.
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    print("\nTraining samples:", len(X_train))
    print("Testing samples:", len(X_test))

    # Evaluate the selected calibrated model.
    evaluation_model = build_classifier(task_name)

    evaluation_model.fit(
        X_train,
        y_train,
    )

    predictions = evaluation_model.predict(X_test)

    probabilities = evaluation_model.predict_proba(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    print("\nHoldout accuracy:", round(accuracy, 4))
    print("Holdout macro F1:", round(macro_f1, 4))

    print("\nClassification report:")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
            digits=3,
        )
    )

    classes = list(evaluation_model.classes_)

    print("Confusion matrix class order:", classes)

    print(
        confusion_matrix(
            y_test,
            predictions,
            labels=classes,
        )
    )

    print("\nProbability calibration check:")
    print(
        "Average maximum predicted probability:",
        round(float(probabilities.max(axis=1).mean()), 4),
    )

    # Train final deployment model on all available data.
    print("\nTraining final model using all examples...")

    final_model = build_classifier(task_name)

    final_model.fit(
        texts,
        labels,
    )

    metadata = {
        "task": task_name,
        "algorithm": (
            "Linear SVM"
            if task_name == "category"
            else "Logistic Regression"
        ),
        "feature_extraction": "TF-IDF",
        "probability_calibration": "Sigmoid",
        "calibration_folds": CALIBRATION_FOLDS,
        "classes": [str(value) for value in final_model.classes_],
        "dataset_examples": len(texts),
        "evaluation_training_examples": len(X_train),
        "evaluation_testing_examples": len(X_test),
        "holdout_accuracy": float(accuracy),
        "holdout_macro_f1": float(macro_f1),
        "random_state": RANDOM_STATE,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": sklearn.__version__,
        "confidence_warning": (
            "Estimated probabilities from synthetic development data; "
            "not validated for real-world emergency decisions."
        ),
    }

    model_bundle = {
        "model": final_model,
        "metadata": metadata,
    }

    output_path = ARTIFACT_DIR / output_filename

    joblib.dump(
        model_bundle,
        output_path,
    )

    print("\nSaved:", output_path)

    return metadata


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("\nDISASTERMESH FINAL MODEL TRAINING")

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    texts, categories, priorities = load_dataset()

    print("\nDataset examples:", len(texts))
    print("Category classes:", len(set(categories)))
    print("Priority classes:", len(set(priorities)))

    category_metadata = train_task(
        texts=texts,
        labels=categories,
        task_name="category",
        display_name="Emergency Category - Linear SVM",
        output_filename="emergency_category_model.joblib",
    )

    priority_metadata = train_task(
        texts=texts,
        labels=priorities,
        task_name="priority",
        display_name="Emergency Priority - Logistic Regression",
        output_filename="emergency_priority_model.joblib",
    )

    summary = {
        "project": "DisasterMesh",
        "dataset_examples": len(texts),
        "category_model": category_metadata,
        "priority_model": priority_metadata,
    }

    summary_path = ARTIFACT_DIR / "training_summary.json"

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )

    print("\n" + "=" * 65)
    print("DISASTERMESH FINAL TRAINING COMPLETED")
    print("=" * 65)

    print("\nModels saved:")
    print("1. emergency_category_model.joblib")
    print("2. emergency_priority_model.joblib")
    print("3. training_summary.json")

    print("\nTraining artifacts:", ARTIFACT_DIR)


if __name__ == "__main__":
    main()
