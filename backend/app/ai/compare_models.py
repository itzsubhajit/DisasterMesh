
"""
DisasterMesh - ML Algorithm Comparison

Compares:
1. Logistic Regression
2. Multinomial Naive Bayes
3. Linear SVM

Uses:
- Stratified 5-fold cross-validation on training data
- A separate stratified holdout test set
- Accuracy and macro F1-score

Does not overwrite the existing trained models.
"""

import csv
import json

from pathlib import Path

import sklearn

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from sklearn.pipeline import Pipeline
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate,
)

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


# ---------------------------------------------------------
# PATHS AND SETTINGS
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
FOLDS = 5


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

        required = {"text", "category", "priority"}

        if not required.issubset(reader.fieldnames):
            raise ValueError(
                "Required columns: text, category, priority"
            )

        for row in reader:

            text = (row.get("text") or "").strip()
            category = (row.get("category") or "").strip()
            priority = (row.get("priority") or "").strip().upper()

            if not text and not category and not priority:
                continue

            if not text or not category or not priority:
                raise ValueError("Dataset contains missing values.")

            texts.append(text)
            categories.append(category)
            priorities.append(priority)

    return texts, categories, priorities


# ---------------------------------------------------------
# CREATE MODEL PIPELINE
# ---------------------------------------------------------

def build_models():

    return {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),

        "Multinomial Naive Bayes": MultinomialNB(
            alpha=0.3,
        ),

        "Linear SVM": LinearSVC(
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
    }


def build_pipeline(classifier):

    return Pipeline([
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


# ---------------------------------------------------------
# COMPARE ONE CLASSIFICATION TASK
# ---------------------------------------------------------

def compare_task(texts, labels, task_name):

    print("\n" + "=" * 70)
    print("TASK:", task_name)
    print("=" * 70)

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    cross_validation = StratifiedKFold(
        n_splits=FOLDS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    results = {}

    for model_name, classifier in build_models().items():

        print("\nTesting:", model_name)

        pipeline = build_pipeline(classifier)

        # Cross-validation only uses training data.
        cv_results = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=cross_validation,
            scoring={
                "accuracy": "accuracy",
                "macro_f1": "f1_macro",
            },
            n_jobs=1,
        )

        cv_accuracy = cv_results["test_accuracy"]
        cv_f1 = cv_results["test_macro_f1"]

        # Evaluate once on the untouched holdout set.
        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)

        test_accuracy = accuracy_score(
            y_test,
            predictions,
        )

        test_f1 = f1_score(
            y_test,
            predictions,
            average="macro",
            zero_division=0,
        )

        print(
            f"CV Accuracy: {cv_accuracy.mean():.4f} "
            f"+/- {cv_accuracy.std():.4f}"
        )

        print(
            f"CV Macro F1: {cv_f1.mean():.4f} "
            f"+/- {cv_f1.std():.4f}"
        )

        print("Holdout Accuracy:", round(test_accuracy, 4))
        print("Holdout Macro F1:", round(test_f1, 4))

        print("\nHoldout Classification Report:")

        print(
            classification_report(
                y_test,
                predictions,
                zero_division=0,
                digits=3,
            )
        )

        print("Confusion Matrix:")

        classes = sorted(set(labels))

        print("Class order:", classes)

        print(
            confusion_matrix(
                y_test,
                predictions,
                labels=classes,
            )
        )

        results[model_name] = {
            "cv_accuracy_mean": float(cv_accuracy.mean()),
            "cv_accuracy_std": float(cv_accuracy.std()),
            "cv_macro_f1_mean": float(cv_f1.mean()),
            "cv_macro_f1_std": float(cv_f1.std()),
            "holdout_accuracy": float(test_accuracy),
            "holdout_macro_f1": float(test_f1),
        }

    print("\n" + "-" * 70)
    print("SUMMARY:", task_name)
    print("-" * 70)

    print(
        f"{'MODEL':30} {'CV MACRO F1':15} {'TEST MACRO F1':15}"
    )

    for name, values in results.items():

        print(
            f"{name:30} "
            f"{values['cv_macro_f1_mean']:<15.4f} "
            f"{values['holdout_macro_f1']:<15.4f}"
        )

    return results


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    if not DATASET_PATH.exists():
        raise FileNotFoundError(DATASET_PATH)

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    texts, categories, priorities = load_dataset()

    print("\nDISASTERMESH ALGORITHM COMPARISON")
    print("Scikit-learn version:", sklearn.__version__)
    print("Dataset examples:", len(texts))
    print("Cross-validation folds:", FOLDS)

    category_results = compare_task(
        texts,
        categories,
        "Emergency Category Classification",
    )

    priority_results = compare_task(
        texts,
        priorities,
        "Emergency Priority Classification",
    )

    summary = {
        "project": "DisasterMesh",
        "dataset_examples": len(texts),
        "scikit_learn_version": sklearn.__version__,
        "cross_validation_folds": FOLDS,
        "category_comparison": category_results,
        "priority_comparison": priority_results,
    }

    output_path = ARTIFACT_DIR / "model_comparison.json"

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )

    print("\nCOMPARISON COMPLETED.")
    print("Saved results:", output_path)
    print("\nExisting trained models were not modified.")


if __name__ == "__main__":
    main()
