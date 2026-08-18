import streamlit as st
import pandas as pd

from database import (
    create_tables,
    get_all_records,
    get_record_count,
    get_status_counts,
    insert_record,
    add_duplicate_log,
    get_duplicate_logs
)

from validator import validate_record

from duplicate_detector import classify_record


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Data Redundancy Removal System",
    page_icon="🗄️",
    layout="wide"
)


# =========================================================
# INITIALIZE DATABASE
# =========================================================

create_tables()


# =========================================================
# APPLICATION TITLE
# =========================================================

st.title("🗄️ Data Redundancy Removal System")

st.write(
    "A cloud-ready system for validating data, detecting "
    "duplicates, identifying potential false positives, "
    "and storing only unique verified records."
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Dashboard",
        "Add Data",
        "Check Duplicate",
        "Database Records",
        "Detection Logs"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.header("📊 Dashboard")

    total_records = get_record_count()

    status_counts = get_status_counts()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Records",
            total_records
        )

    with col2:
        st.metric(
            "Unique Records",
            status_counts["Unique"]
        )

    with col3:
        st.metric(
            "Review Records",
            status_counts["Review"]
        )

    with col4:
        st.metric(
            "Duplicate Records",
            status_counts["Duplicate"]
        )

    st.divider()

    st.subheader("System Workflow")

    st.info(
        """
        New Data
        ↓
        Validation
        ↓
        Duplicate Detection
        ↓
        Similarity Analysis
        ↓
        Classification
        ↓
        Store Unique Data
        """
    )

    st.subheader("Record Statistics")

    chart_data = pd.DataFrame({
        "Category": [
            "Unique",
            "Review",
            "Duplicate"
        ],
        "Count": [
            status_counts["Unique"],
            status_counts["Review"],
            status_counts["Duplicate"]
        ]
    })

    st.bar_chart(
        chart_data.set_index("Category")
    )


# =========================================================
# ADD DATA
# =========================================================

elif page == "Add Data":

    st.header("➕ Add New Data")

    st.write(
        "Enter a record below. The system will first validate "
        "the information and then compare it with existing records."
    )

    with st.form("data_entry_form"):

        name = st.text_input(
            "Name",
            placeholder="Enter your name"
        )

        email = st.text_input(
            "Email",
            placeholder="Example: qwerty@gmail.com"
        )

        phone = st.text_input(
            "Phone Number",
            placeholder="Enter your phone number"
        )

        submitted = st.form_submit_button(
            "Validate and Submit"
        )

    if submitted:

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        valid, message, cleaned_data = validate_record(
            name,
            email,
            phone
        )

        if not valid:

            st.error(
                f"❌ {message}"
            )

        else:

            st.success(
                "✅ Data validation successful."
            )

            # -------------------------------------------------
            # GET EXISTING RECORDS
            # -------------------------------------------------

            existing_records = get_all_records()

            # -------------------------------------------------
            # DUPLICATE ANALYSIS
            # -------------------------------------------------

            result = classify_record(
                cleaned_data,
                existing_records
            )

            classification = result["classification"]
            similarity = result["similarity"]
            matched_record = result["matched_record"]
            data_hash = result["data_hash"]
            reason = result["reason"]

            st.write(
                f"Similarity Score: **{similarity}%**"
            )

            # -------------------------------------------------
            # UNIQUE RECORD
            # -------------------------------------------------

            if classification == "Unique":

                inserted, record_id = insert_record(
                    cleaned_data["name"],
                    cleaned_data["email"],
                    cleaned_data["phone"],
                    data_hash,
                    "Unique"
                )

                if inserted:

                    st.success(
                        "✅ Unique and verified record "
                        "successfully added to the database."
                    )

                    st.write(
                        f"Record ID: **{record_id}**"
                    )

                else:

                    st.error(
                        "❌ Record could not be added."
                    )

            # -------------------------------------------------
            # DUPLICATE RECORD
            # -------------------------------------------------

            elif classification == "Duplicate":

                matched_record_id = None

                if matched_record:
                    matched_record_id = matched_record["id"]

                add_duplicate_log(
                    cleaned_data["name"],
                    cleaned_data["email"],
                    cleaned_data["phone"],
                    matched_record_id,
                    similarity,
                    "Duplicate",
                    reason
                )

                st.error(
                    "❌ Duplicate record detected."
                )

                st.warning(
                    "The duplicate record was NOT inserted "
                    "into the database."
                )

                if matched_record:

                    st.subheader(
                        "Matching Existing Record"
                    )

                    st.dataframe(
                        pd.DataFrame([matched_record]),
                        use_container_width=True,
                        hide_index=True
                    )

            # -------------------------------------------------
            # REVIEW / POSSIBLE FALSE POSITIVE
            # -------------------------------------------------

            elif classification == "Review":

                matched_record_id = None

                if matched_record:
                    matched_record_id = matched_record["id"]

                add_duplicate_log(
                    cleaned_data["name"],
                    cleaned_data["email"],
                    cleaned_data["phone"],
                    matched_record_id,
                    similarity,
                    "Review",
                    reason
                )

                st.warning(
                    "⚠️ Potential duplicate detected."
                )

                st.info(
                    "The record has been classified as "
                    "a possible false positive and was NOT "
                    "automatically inserted."
                )

                if matched_record:

                    st.subheader(
                        "Potential Matching Record"
                    )

                    st.dataframe(
                        pd.DataFrame([matched_record]),
                        use_container_width=True,
                        hide_index=True
                    )


# =========================================================
# CHECK DUPLICATE
# =========================================================

elif page == "Check Duplicate":

    st.header("🔍 Check Data for Redundancy")

    st.write(
        "Use this page to check whether a record already exists "
        "without inserting it into the database."
    )

    name = st.text_input(
        "Name",
        key="duplicate_name"
    )

    email = st.text_input(
        "Email",
        key="duplicate_email"
    )

    phone = st.text_input(
        "Phone Number",
        key="duplicate_phone"
    )

    if st.button("Check Record"):

        valid, message, cleaned_data = validate_record(
            name,
            email,
            phone
        )

        if not valid:

            st.error(
                f"❌ {message}"
            )

        else:

            existing_records = get_all_records()

            result = classify_record(
                cleaned_data,
                existing_records
            )

            classification = result["classification"]
            similarity = result["similarity"]
            matched_record = result["matched_record"]

            st.metric(
                "Similarity Score",
                f"{similarity}%"
            )

            if classification == "Unique":

                st.success(
                    "✅ No significant duplicate found."
                )

                st.write(
                    "This record appears to be unique."
                )

            elif classification == "Duplicate":

                st.error(
                    "❌ Duplicate record detected."
                )

                st.write(
                    "This record appears to already exist "
                    "in the database."
                )

            else:

                st.warning(
                    "⚠️ Potential duplicate detected."
                )

                st.write(
                    "This may be a false positive and "
                    "requires verification."
                )

            if matched_record:

                st.subheader(
                    "Closest Matching Record"
                )

                st.dataframe(
                    pd.DataFrame([matched_record]),
                    use_container_width=True,
                    hide_index=True
                )


# =========================================================
# DATABASE RECORDS
# =========================================================

elif page == "Database Records":

    st.header("📋 Database Records")

    records = get_all_records()

    if records:

        dataframe = pd.DataFrame(records)

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No records are currently stored."
        )


# =========================================================
# DETECTION LOGS
# =========================================================

elif page == "Detection Logs":

    st.header("📑 Duplicate Detection Logs")

    logs = get_duplicate_logs()

    if logs:

        dataframe = pd.DataFrame(logs)

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No duplicate or review logs are available."
        )


# =========================================================
# FOOTER
# =========================================================

st.sidebar.divider()

st.sidebar.info(
    "Data Redundancy Removal System\n\n"
    "Python + Streamlit + PostgreSQL + RapidFuzz"
)