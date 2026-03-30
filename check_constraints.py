import sys
from typing import Dict, List, Set

import ollama
import psycopg2
from psycopg2 import sql

from config import Config

REQUIRED_ENUMS = {
    "user_type_enum",
    "severity_level_enum",
    "detection_status_enum",
}

REQUIRED_TABLES = {
    "users",
    "field",
    "scan_history_chat",
    "user_scan_history",
    "disease",
    "treatment_recommendation",
    "detection",
    "applied_treatment",
    "user_refresh_token",
}

REQUIRED_CONSTRAINTS: Dict[str, Set[str]] = {
    "users": {"user_pk", "user_code_uk", "user_email_uk"},
    "field": {"field_pk", "field_user_fk"},
    "scan_history_chat": {"scan_history_chat_pk", "user_chat_code_uk"},
    "user_scan_history": {
        "user_scan_history_pk",
        "user_scan_history_user_fk",
        "user_scan_history_field_fk",
        "user_scan_history_scan_fk",
    },
    "disease": {"disease_pk", "disease_name_uk"},
    "treatment_recommendation": {
        "treatment_recommendation_pk",
        "treatment_recommendation_code_uk",
        "treatment_recommendation_rag_confidence_score_chk",
    },
    "detection": {
        "detection_pk",
        "detection_code_uk",
        "detection_scan_fk",
        "detection_disease_fk",
        "detection_confidence_chk",
        "detection_recovery_chk",
    },
    "applied_treatment": {
        "applied_treatment_pk",
        "applied_treatment_detection_fk",
        "applied_treatment_recommendation_fk",
    },
    "user_refresh_token": {
        "user_refresh_token_pk",
        "user_refresh_token_hash_uk",
        "user_refresh_token_user_fk",
    },
}

MIN_DISEASE_ROWS = 1


def print_ok(message: str) -> None:
    print(f"[OK] {message}")


def print_fail(message: str) -> None:
    print(f"[FAIL] {message}")


def get_connection(database_name: str):
    return psycopg2.connect(
        host=Config.DB_HOST,
        database=database_name,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
    )


def database_exists(default_db_name: str, target_db_name: str) -> bool:
    with get_connection(default_db_name) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db_name,))
            return cur.fetchone() is not None


def get_existing_tables(conn) -> Set[str]:
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return {row[0] for row in cur.fetchall()}


def get_existing_enums(conn) -> Set[str]:
    query = """
        SELECT t.typname
        FROM pg_type t
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE t.typtype = 'e' AND n.nspname = 'public'
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return {row[0] for row in cur.fetchall()}


def get_table_constraints(conn) -> Dict[str, Set[str]]:
    query = """
        SELECT c.relname AS table_name, con.conname AS constraint_name
        FROM pg_constraint con
        JOIN pg_class c ON c.oid = con.conrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
    """
    constraints: Dict[str, Set[str]] = {}
    with conn.cursor() as cur:
        cur.execute(query)
        for table_name, constraint_name in cur.fetchall():
            constraints.setdefault(table_name, set()).add(constraint_name.lower())
    return constraints


def get_disease_count(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier("disease")))
        return cur.fetchone()[0]


def run_db_checks() -> int:
    default_db_name = Config.DEFAULT_DB_NAME
    target_db_name = Config.DB_NAME

    if not default_db_name or not target_db_name:
        print_fail("Missing Config.DEFAULT_DB_NAME or Config.DB_NAME in environment.")
        return 1

    print(f"Checking database prerequisites for '{target_db_name}'...")

    try:
        if database_exists(default_db_name, target_db_name):
            print_ok(f"Database '{target_db_name}' exists")
        else:
            print_fail(f"Database '{target_db_name}' does not exist")
            return 1
    except Exception as exc:
        print_fail(f"Could not verify database existence: {exc}")
        return 1

    failures: List[str] = []

    try:
        with get_connection(target_db_name) as conn:
            existing_tables = get_existing_tables(conn)
            missing_tables = REQUIRED_TABLES - existing_tables
            if missing_tables:
                failures.append(f"Missing tables: {sorted(missing_tables)}")
            else:
                print_ok("All required tables exist")

            existing_enums = get_existing_enums(conn)
            missing_enums = REQUIRED_ENUMS - existing_enums
            if missing_enums:
                failures.append(f"Missing enums: {sorted(missing_enums)}")
            else:
                print_ok("All required enums exist")

            existing_constraints = get_table_constraints(conn)
            for table_name, expected_constraints in REQUIRED_CONSTRAINTS.items():
                found_constraints = existing_constraints.get(table_name, set())
                missing_constraints = expected_constraints - found_constraints
                if missing_constraints:
                    failures.append(
                        f"Table '{table_name}' missing constraints: {sorted(missing_constraints)}"
                    )

            if not any(msg.startswith("Table '") for msg in failures):
                print_ok("All required constraints exist")

            if "disease" in existing_tables:
                disease_count = get_disease_count(conn)
                if disease_count >= MIN_DISEASE_ROWS:
                    print_ok(f"Disease seed data found ({disease_count} rows)")
                else:
                    failures.append(
                        f"Disease table has insufficient data: expected >= {MIN_DISEASE_ROWS}, found {disease_count}"
                    )

    except Exception as exc:
        print_fail(f"Could not connect or query target database: {exc}")
        return 1

    if failures:
        print_fail("Pre-check failed")
        for item in failures:
            print_fail(item)
        return 1

    print_ok("All database prerequisite constraints are satisfied")
    return 0


def _extract_model_names(list_response) -> Set[str]:
    """Support different ollama-python response shapes across versions."""
    models = set()

    if isinstance(list_response, dict):
        raw_models = list_response.get("models", [])
    else:
        raw_models = getattr(list_response, "models", [])

    for item in raw_models or []:
        if isinstance(item, dict):
            model_name = item.get("model") or item.get("name")
        else:
            model_name = getattr(item, "model", None) or getattr(item, "name", None)
        if model_name:
            models.add(model_name)

    return models


def run_ollama_checks() -> int:
    model_name = Config.LLM_NAME

    try:
        response = ollama.list()
        print_ok("Ollama server is reachable")

        available_models = _extract_model_names(response)
        if model_name in available_models:
            print_ok(f"Ollama model '{model_name}' is available")
            return 0

        print_fail(f"Ollama model '{model_name}' is not available locally")
        return 1
    except Exception as exc:
        print_fail(f"Ollama check failed: {exc}")
        return 1


def check_prerequisites() -> int:
    py_status = run_python_version_check()
    db_status = run_db_checks()
    ollama_status = run_ollama_checks()

    # If all three checks return 0 (success), we are good to go!
    if py_status == 0 and db_status == 0 and ollama_status == 0:
        print_ok("All prerequisite checks passed")
        return 0

    print_fail("One or more prerequisite checks failed")
    return 1


def run_python_version_check() -> int:
    current_version = sys.version_info
    MIN_PYTHON_VERSION=Config.PYTHON_VERSION

    if current_version >= MIN_PYTHON_VERSION:
        print_ok(
            f"Python version >= {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} "
            f"(Found {current_version.major}.{current_version.minor}.{current_version.micro})"
        )
        return 0

    print_fail(
        f"Python version {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher is required. "
        f"Found {current_version.major}.{current_version.minor}.{current_version.micro}"
    )
    return 1

if __name__ == "__main__":
    sys.exit(check_prerequisites())
