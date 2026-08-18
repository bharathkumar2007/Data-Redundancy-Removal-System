import hashlib
from rapidfuzz.fuzz import ratio


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):
    """Convert text into a standard comparable format."""

    if value is None:
        return ""

    return str(value).strip().lower()


# =========================================================
# CREATE DATA HASH
# =========================================================

def create_data_hash(name, email, phone):
    """
    Create a SHA-256 hash using normalized
    name, email and phone.
    """

    normalized_name = normalize_text(name)
    normalized_email = normalize_text(email)
    normalized_phone = normalize_text(phone)

    combined = (
        normalized_name
        + "|"
        + normalized_email
        + "|"
        + normalized_phone
    )

    return hashlib.sha256(
        combined.encode("utf-8")
    ).hexdigest()


# =========================================================
# FIELD SIMILARITY
# =========================================================

def calculate_field_similarity(new_value, old_value):
    """Calculate similarity between two individual fields."""

    new_value = normalize_text(new_value)
    old_value = normalize_text(old_value)

    if not new_value or not old_value:
        return 0

    return ratio(new_value, old_value)


# =========================================================
# CLASSIFY RECORD
# =========================================================

def classify_record(new_record, existing_records):

    """
    Classify a new record as:

    Unique
    Review
    Duplicate

    The system compares name, email and phone separately.
    """

    new_name = normalize_text(
        new_record.get("name")
    )

    new_email = normalize_text(
        new_record.get("email")
    )

    new_phone = normalize_text(
        new_record.get("phone")
    )

    new_hash = create_data_hash(
        new_name,
        new_email,
        new_phone
    )

    # -----------------------------------------------------
    # No existing records
    # -----------------------------------------------------

    if not existing_records:

        return {
            "classification": "Unique",
            "similarity": 0,
            "matched_record": None,
            "data_hash": new_hash,
            "reason": "No existing records found."
        }

    best_match = None
    best_score = 0
    best_reason = ""

    # -----------------------------------------------------
    # Compare with every existing record
    # -----------------------------------------------------

    for record in existing_records:

        old_name = normalize_text(
            record.get("name")
        )

        old_email = normalize_text(
            record.get("email")
        )

        old_phone = normalize_text(
            record.get("phone")
        )

        # -------------------------------------------------
        # Exact field matching
        # -------------------------------------------------

        name_exact = (
            new_name == old_name
            and new_name != ""
        )

        email_exact = (
            new_email == old_email
            and new_email != ""
        )

        phone_exact = (
            new_phone == old_phone
            and new_phone != ""
        )

        # -------------------------------------------------
        # Field similarity
        # -------------------------------------------------

        name_score = calculate_field_similarity(
            new_name,
            old_name
        )

        email_score = calculate_field_similarity(
            new_email,
            old_email
        )

        phone_score = calculate_field_similarity(
            new_phone,
            old_phone
        )

        # -------------------------------------------------
        # Exact duplicate
        # -------------------------------------------------

        if (
            name_exact
            and email_exact
            and phone_exact
        ):

            return {
                "classification": "Duplicate",
                "similarity": 100,
                "matched_record": record,
                "data_hash": new_hash,
                "reason": (
                    "Name, email and phone number "
                    "exactly match an existing record."
                )
            }

        # -------------------------------------------------
        # Strong duplicate evidence
        # -------------------------------------------------

        if (
            email_exact
            and phone_exact
        ):

            score = 100

            reason = (
                "Email and phone number exactly "
                "match an existing record."
            )

        elif (
            phone_exact
            and name_score >= 85
        ):

            score = (
                name_score * 0.6
                + phone_score * 0.4
            )

            reason = (
                "Phone number exactly matches and "
                "the name is highly similar."
            )

        elif (
            email_exact
            and name_score >= 85
        ):

            score = (
                name_score * 0.6
                + email_score * 0.4
            )

            reason = (
                "Email exactly matches and "
                "the name is highly similar."
            )

        else:

            # -------------------------------------------------
            # General weighted similarity
            # -------------------------------------------------

            score = (
                name_score * 0.40
                + email_score * 0.35
                + phone_score * 0.25
            )

            reason = (
                f"Name similarity: {name_score:.2f}%, "
                f"Email similarity: {email_score:.2f}%, "
                f"Phone similarity: {phone_score:.2f}%."
            )

        # -------------------------------------------------
        # Store best match
        # -------------------------------------------------

        if score > best_score:

            best_score = score
            best_match = record
            best_reason = reason

    # =====================================================
    # FINAL CLASSIFICATION
    # =====================================================

    # Exact or extremely strong duplicate
    if best_score >= 95:

        classification = "Duplicate"

    # Potential duplicate / false positive
    elif best_score >= 80:

        classification = "Review"

    # Clearly different
    else:

        classification = "Unique"

    return {
        "classification": classification,
        "similarity": round(best_score, 2),
        "matched_record": best_match,
        "data_hash": new_hash,
        "reason": best_reason
    }