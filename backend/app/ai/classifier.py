
"""
DisasterMesh - Emergency Classification Engine

Loads:
1. Calibrated Linear SVM category model.
2. Calibrated Logistic Regression priority model.

Returns:
- Predicted emergency category
- Predicted priority
- Estimated class probabilities
- Human-review requirement
- Safety-rule warnings

Important:
AI predictions are decision-support information only.
They must not independently authorize rescue decisions
or advance incident status.
"""

from functools import lru_cache
from pathlib import Path

import joblib


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[2]

ARTIFACT_DIR = BACKEND_DIR / "artifacts"

CATEGORY_MODEL_PATH = (
    ARTIFACT_DIR / "emergency_category_model.joblib"
)

PRIORITY_MODEL_PATH = (
    ARTIFACT_DIR / "emergency_priority_model.joblib"
)


# ---------------------------------------------------------
# CONFIDENCE THRESHOLDS
# ---------------------------------------------------------

# Initial development thresholds.
# These must be tuned using independently validated data.

CATEGORY_CONFIDENCE_THRESHOLD = 0.60
PRIORITY_CONFIDENCE_THRESHOLD = 0.60


# ---------------------------------------------------------
# HIGH-RISK LANGUAGE
# ---------------------------------------------------------

# These phrases trigger mandatory human review.
# They do not independently change the model's prediction.

HIGH_RISK_PHRASES = (
    "trapped under",
    "people trapped",
    "child trapped",
    "unable to breathe",
    "difficulty breathing",
    "not breathing",
    "unconscious",
    "severe bleeding",
    "heavy bleeding",
    "cardiac arrest",
    "fire spreading",
    "gas cylinder fire",
    "stranded on rooftops",
    "immediate rescue",
    "life threatening",
    "life-threatening",
    "serious injury",
    "major explosion",
)


# ---------------------------------------------------------
# LOAD TRAINED MODELS
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def load_models():
    """
    Load both trained model bundles once.

    The cache prevents loading the model files for every
    incoming emergency message.
    """

    if not CATEGORY_MODEL_PATH.exists():
        raise FileNotFoundError(
            "Category model not found. "
            "Run: python -m app.ai.train_model"
        )

    if not PRIORITY_MODEL_PATH.exists():
        raise FileNotFoundError(
            "Priority model not found. "
            "Run: python -m app.ai.train_model"
        )

    category_bundle = joblib.load(
        CATEGORY_MODEL_PATH
    )

    priority_bundle = joblib.load(
        PRIORITY_MODEL_PATH
    )

    if (
        not isinstance(category_bundle, dict)
        or "model" not in category_bundle
    ):
        raise ValueError(
            "Invalid category model artifact."
        )

    if (
        not isinstance(priority_bundle, dict)
        or "model" not in priority_bundle
    ):
        raise ValueError(
            "Invalid priority model artifact."
        )

    category_model = category_bundle["model"]
    priority_model = priority_bundle["model"]

    if not hasattr(category_model, "predict_proba"):
        raise ValueError(
            "Category model does not support probabilities."
        )

    if not hasattr(priority_model, "predict_proba"):
        raise ValueError(
            "Priority model does not support probabilities."
        )

    return (
        category_model,
        priority_model,
        category_bundle.get("metadata", {}),
        priority_bundle.get("metadata", {}),
    )


# ---------------------------------------------------------
# PROBABILITY HELPER
# ---------------------------------------------------------

def get_prediction_details(model, text):
    """
    Return predicted class, maximum probability and
    probabilities for every available class.
    """

    predicted_class = str(
        model.predict([text])[0]
    )

    probabilities = model.predict_proba([text])[0]

    classes = model.classes_

    probability_map = {
        str(class_name): round(float(probability), 4)
        for class_name, probability in zip(
            classes,
            probabilities,
        )
    }

    maximum_probability = float(
        max(probabilities)
    )

    return (
        predicted_class,
        maximum_probability,
        probability_map,
    )


# ---------------------------------------------------------
# HUMAN REVIEW RULES
# ---------------------------------------------------------

def get_review_reasons(
    text,
    category,
    category_confidence,
    priority,
    priority_confidence,
):
    """
    Apply conservative human-review requirements.

    A critical predicted priority always requires review.

    Low-confidence predictions require review.

    High-risk language also requires review even when
    the predicted priority is not CRITICAL.
    """

    reasons = []

    normalized_text = " ".join(
        text.lower().split()
    )

    # Critical-priority review rule.
    if priority == "CRITICAL":

        reasons.append(
            "CRITICAL_PRIORITY_REQUIRES_OPERATOR_REVIEW"
        )

    # Category confidence rule.
    if (
        category_confidence
        < CATEGORY_CONFIDENCE_THRESHOLD
    ):

        reasons.append(
            "LOW_CATEGORY_CONFIDENCE"
        )

    # Priority confidence rule.
    if (
        priority_confidence
        < PRIORITY_CONFIDENCE_THRESHOLD
    ):

        reasons.append(
            "LOW_PRIORITY_CONFIDENCE"
        )

    # High-risk language detection.
    matched_phrases = [
        phrase
        for phrase in HIGH_RISK_PHRASES
        if phrase in normalized_text
    ]

    if matched_phrases:

        reasons.append(
            "HIGH_RISK_LANGUAGE_REQUIRES_REVIEW"
        )

    return reasons, matched_phrases


# ---------------------------------------------------------
# MAIN CLASSIFICATION FUNCTION
# ---------------------------------------------------------

def classify_emergency(text):
    """
    Classify an incoming emergency message.

    Example:
        result = classify_emergency(
            "Person trapped beneath collapsed concrete."
        )
    """

    if not isinstance(text, str):
        raise TypeError(
            "Emergency message must be a string."
        )

    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError(
            "Emergency message cannot be empty."
        )

    (
        category_model,
        priority_model,
        category_metadata,
        priority_metadata,
    ) = load_models()

    # Predict category.
    (
        category,
        category_confidence,
        category_probabilities,
    ) = get_prediction_details(
        category_model,
        cleaned_text,
    )

    # Predict priority.
    (
        priority,
        priority_confidence,
        priority_probabilities,
    ) = get_prediction_details(
        priority_model,
        cleaned_text,
    )

    # Apply human-review rules.
    review_reasons, matched_phrases = get_review_reasons(
        text=cleaned_text,
        category=category,
        category_confidence=category_confidence,
        priority=priority,
        priority_confidence=priority_confidence,
    )

    requires_human_review = bool(
        review_reasons
    )

    return {
        "category": category,
        "category_confidence": round(
            category_confidence,
            4,
        ),
        "category_probabilities": category_probabilities,

        "priority": priority,
        "priority_confidence": round(
            priority_confidence,
            4,
        ),
        "priority_probabilities": priority_probabilities,

        "requires_human_review": requires_human_review,
        "review_reasons": review_reasons,
        "matched_high_risk_phrases": matched_phrases,

        "confidence_thresholds": {
            "category": CATEGORY_CONFIDENCE_THRESHOLD,
            "priority": PRIORITY_CONFIDENCE_THRESHOLD,
        },

        "model_information": {
            "category_algorithm": category_metadata.get(
                "algorithm",
                "Unknown",
            ),
            "priority_algorithm": priority_metadata.get(
                "algorithm",
                "Unknown",
            ),
        },

        "decision_authority": "HUMAN_OPERATOR",
    }


# ---------------------------------------------------------
# DIRECT TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    import json

    test_messages = [
        "Person trapped under concrete rubble and unable to breathe.",

        "Large flames spreading inside a residential building.",

        "Relief camp has run out of drinking water.",

        "All residents accounted for and confirmed safe.",
    ]

    for message in test_messages:

        print("\n" + "=" * 65)
        print("MESSAGE:", message)
        print("=" * 65)

        prediction = classify_emergency(message)

        print(
            json.dumps(
                prediction,
                indent=4,
            )
        )
