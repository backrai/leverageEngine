"""
LSM-PN Schema Validator
Validates LSM-PN JSON documents against the v1.0 schema.
"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMA_PATH = Path(__file__).parent / "lsm_pn_v1.schema.json"


def load_schema() -> dict:
    """Load the LSM-PN v1.0 JSON schema."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_document(doc: dict) -> list[str]:
    """Validate an LSM-PN document. Returns list of error messages (empty = valid)."""
    schema = load_schema()
    errors = []

    if not HAS_JSONSCHEMA:
        # Fallback: basic structural validation without jsonschema library
        errors.extend(_basic_validate(doc, schema))
        return errors

    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"[{path}] {error.message}")
    return errors


def validate_file(filepath: str | Path) -> list[str]:
    """Validate an LSM-PN JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        doc = json.load(f)
    return validate_document(doc)


def _basic_validate(doc: dict, schema: dict) -> list[str]:
    """Basic validation without jsonschema library."""
    errors = []

    # Check required top-level fields
    for field in schema.get("required", []):
        if field not in doc:
            errors.append(f"Missing required field: '{field}'")

    # Check meta
    if "meta" in doc:
        meta = doc["meta"]
        if meta.get("schema_version") != "1.0":
            errors.append(f"schema_version must be '1.0', got '{meta.get('schema_version')}'")
        if "sign_id" not in meta:
            errors.append("meta.sign_id is required")
        if "gloss" not in meta:
            errors.append("meta.gloss is required")

    # Check dominant hand
    if "dominant_hand" in doc:
        hand = doc["dominant_hand"]
        if "handshape" not in hand:
            errors.append("dominant_hand.handshape is required")
        else:
            hs = hand["handshape"]
            if "cm_id" not in hs:
                errors.append("dominant_hand.handshape.cm_id is required")
            elif not (1 <= hs["cm_id"] <= 101):
                errors.append(f"cm_id must be 1-101, got {hs['cm_id']}")

            valid_flexion = {"EXTENDED", "CURVED", "BENT", "CLOSED"}
            if "finger_states" in hs:
                for finger in ["index", "middle", "ring", "pinky"]:
                    val = hs["finger_states"].get(finger)
                    if val and val not in valid_flexion:
                        errors.append(f"Invalid flexion '{val}' for {finger}")

            valid_opposition = {"OPPOSED", "PARALLEL", "CROSSED"}
            if "thumb_opposition" in hs and hs["thumb_opposition"] not in valid_opposition:
                errors.append(f"Invalid thumb_opposition: '{hs['thumb_opposition']}'")

    # Check timing
    if "timing" in doc:
        timing = doc["timing"]
        if "phases" not in timing:
            errors.append("timing.phases is required")
        else:
            valid_phases = {"PREPARATION", "STROKE", "HOLD", "RETRACTION"}
            for phase in timing["phases"]:
                if phase not in valid_phases:
                    errors.append(f"Invalid phase: '{phase}'")

    return errors


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.schema.validate <file.json> [file2.json ...]")
        sys.exit(1)

    all_valid = True
    for filepath in sys.argv[1:]:
        errors = validate_file(filepath)
        if errors:
            all_valid = False
            print(f"\n❌ {filepath} — {len(errors)} error(s):")
            for err in errors:
                print(f"   • {err}")
        else:
            print(f"✅ {filepath} — valid LSM-PN v1.0")

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
