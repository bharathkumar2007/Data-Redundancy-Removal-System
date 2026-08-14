import re


def validate_name(name):
    """Validate the user's name."""
    name = str(name).strip()

    if not name:
        return False, "Name cannot be empty."

    if len(name) < 2:
        return False, "Name must contain at least 2 characters."

    if not re.fullmatch(r"[A-Za-z\s.]+", name):
        return False, "Name can contain only letters, spaces, and periods."

    return True, "Valid name."


def validate_email(email):
    """Validate the email address."""
    email = str(email).strip().lower()

    if not email:
        return False, "Email cannot be empty."

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(pattern, email):
        return False, "Invalid email address."

    return True, "Valid email."


def validate_phone(phone):
    """Validate a 10-digit phone number."""
    phone = str(phone).strip()

    if not phone:
        return False, "Phone number cannot be empty."

    if not phone.isdigit():
        return False, "Phone number must contain only digits."

    if len(phone) != 10:
        return False, "Phone number must contain exactly 10 digits."

    return True, "Valid phone number."


def clean_record(name, email, phone):
    """Clean and normalize the submitted data."""
    return {
        "name": " ".join(str(name).strip().split()),
        "email": str(email).strip().lower(),
        "phone": str(phone).strip()
    }


def validate_record(name, email, phone):
    """
    Validate and clean the complete record.

    Returns:
        (True, message, cleaned_data) when valid
        (False, error_message, None) when invalid
    """

    cleaned_data = clean_record(name, email, phone)

    valid_name, name_message = validate_name(cleaned_data["name"])
    if not valid_name:
        return False, name_message, None

    valid_email, email_message = validate_email(cleaned_data["email"])
    if not valid_email:
        return False, email_message, None

    valid_phone, phone_message = validate_phone(cleaned_data["phone"])
    if not valid_phone:
        return False, phone_message, None

    return True, "Data is valid.", cleaned_data


# Test the validator when this file is run directly
if __name__ == "__main__":

    test_name = "Bharathkumar"
    test_email = "qwerty@gmail.com"
    test_phone = "9876543210"

    valid, message, data = validate_record(
        test_name,
        test_email,
        test_phone
    )

    print("Valid:", valid)
    print("Message:", message)
    print("Data:", data)