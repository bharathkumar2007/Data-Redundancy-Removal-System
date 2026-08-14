import hashlib
from rapidfuzz.fuzz import ratio


def normalize_text(text):
    """Normalize text before comparison."""
    return " ".join(str(text).lower().strip().split())


def generate_hash(name, email, phone):
    """
    Generate a SHA-256 hash for exact duplicate detection.
    """

    normalized_data = (
        f"{normalize_text(name)}|"
        f"{str(email).lower().strip()}|"
        f"{str(phone).strip()}"
    )

    return hashlib.sha256(
        normalized_data.encode("utf-8")
    ).hexdigest()


def calculate_similarity(new_record, existing_record):
    """
    Calculate similarity between a new record
    and an existing record.
    """

    name_score = ratio(
        normalize_text(new_record["name"]),
        normalize_text(existing_record["name"])
    )

    email_score = ratio(
        str(new_record["email"]).lower().strip(),
        str(existing_record["email"]).lower().strip()
    )

    phone_score = ratio(
        str(new_record["phone"]).strip(),
        str(existing_record["phone"]).strip()
    )

    # Weighted similarity score
    total_score = (
        (name_score * 0.4)
        + (email_score * 0.3)
        + (phone_score * 0.3)
    )

    return round(total_score, 2)


def classify_record(new_record, existing_records):
    """
    Classify the new record as:

    Unique     -> Safe to add
    Duplicate  -> Already exists
    Review     -> Possible false positive
    """

    # Generate hash for the new record
    new_hash = generate_hash(
        new_record["name"],
        new_record["email"],
        new_record["phone"]
    )

    # -----------------------------------------
    # STEP 1: EXACT DUPLICATE CHECK
    # -----------------------------------------

    for record in existing_records:

        if new_hash == record["data_hash"]:

            return {
                "classification": "Duplicate",
                "similarity": 100.0,
                "matched_record": record,
                "data_hash": new_hash,
                "reason": "Exact duplicate found."
            }

    # -----------------------------------------
    # STEP 2: SIMILARITY CHECK
    # -----------------------------------------

    highest_score = 0
    best_match = None

    for record in existing_records:

        existing_record = {
            "name": record["name"],
            "email": record["email"],
            "phone": record["phone"]
        }

        score = calculate_similarity(
            new_record,
            existing_record
        )

        if score > highest_score:
            highest_score = score
            best_match = record

    # -----------------------------------------
    # STEP 3: CLASSIFICATION
    # -----------------------------------------

    if highest_score >= 90:

        classification = "Duplicate"
        reason = "Highly similar record detected."

    elif highest_score >= 70:

        classification = "Review"
        reason = "Potential duplicate or false positive."

    else:

        classification = "Unique"
        reason = "No significant duplicate found."

    return {
        "classification": classification,
        "similarity": highest_score,
        "matched_record": best_match,
        "data_hash": new_hash,
        "reason": reason
    }


# -----------------------------------------
# SIMPLE TEST
# -----------------------------------------

if __name__ == "__main__":

    existing_records = [
        {
            "id": 1,
            "name": "Bharathkumar",
            "email": "qwerty@gmail.com",
            "phone": "9876543210",
            "data_hash": generate_hash(
                "Bharathkumar",
                "qwerty@gmail.com",
                "9876543210"
            )
        }
    ]

    new_record = {
        "name": "Bharathkumar",
        "email": "qwerty@gmail.com",
        "phone": "9876543210"
    }

    result = classify_record(
        new_record,
        existing_records
    )

    print("Classification:", result["classification"])
    print("Similarity:", result["similarity"])
    print("Reason:", result["reason"])