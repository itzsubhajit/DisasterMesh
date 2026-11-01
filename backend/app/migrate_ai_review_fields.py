"""Add AI classification and operator-review columns to existing SQLite DB."""

from sqlalchemy import inspect, text

from .database import engine


COLUMNS_TO_ADD = {
    "messages": {
        "ai_category": "VARCHAR(50)",
        "ai_category_confidence": "FLOAT",
        "ai_category_probabilities": "JSON",
        "ai_priority": "VARCHAR(20)",
        "ai_priority_confidence": "FLOAT",
        "ai_priority_probabilities": "JSON",
        "ai_requires_human_review": "BOOLEAN NOT NULL DEFAULT 0",
        "ai_review_reasons": "JSON",
        "ai_matched_high_risk_phrases": "JSON",
        "ai_decision_authority": "VARCHAR(30) NOT NULL DEFAULT 'HUMAN_OPERATOR'",
        "ai_model_info": "JSON",
    },
    "emergency_requests": {
        "ai_reviewed_at": "DATETIME",
        "ai_reviewed_by": "INTEGER REFERENCES users(user_id)",
        "ai_review_decision": "VARCHAR(20)",
        "ai_review_notes": "TEXT",
    },
}


def migrate() -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        for table_name, columns in COLUMNS_TO_ADD.items():
            if table_name not in existing_tables:
                raise RuntimeError(
                    f"Required table '{table_name}' does not exist. "
                    "Initialize the current DisasterMesh database first."
                )

            existing_columns = {
                column["name"] for column in inspect(engine).get_columns(table_name)
            }

            for column_name, column_sql in columns.items():
                if column_name in existing_columns:
                    print(f"SKIP: {table_name}.{column_name} already exists")
                    continue

                statement = (
                    f'ALTER TABLE "{table_name}" '
                    f'ADD COLUMN "{column_name}" {column_sql}'
                )
                connection.execute(text(statement))
                print(f"ADDED: {table_name}.{column_name}")

    print("AI classification and operator-review migration completed.")


if __name__ == "__main__":
    migrate()
