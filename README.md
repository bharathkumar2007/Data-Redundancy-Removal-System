# Data Redundancy Removal System

## Project Overview

The Data Redundancy Removal System is a cloud-based application designed to identify duplicate, unique, and potentially similar records before they are stored in a database.

The system validates newly submitted data against existing records using field-level similarity analysis. It prevents exact duplicate records from being inserted and identifies potentially similar records as possible false positives for review.

The application uses Streamlit for the web interface and Supabase PostgreSQL as the cloud database.

## Objectives

- Identify redundant and duplicate data.
- Validate new records against existing records.
- Prevent duplicate records from being added to the cloud database.
- Store only unique and verified records.
- Identify potentially similar records as false positives for review.
- Maintain logs of duplicate and review attempts.
- Improve database accuracy and reduce unnecessary redundancy.

## Technologies Used

- Python
- Streamlit
- PostgreSQL
- Supabase
- RapidFuzz
- psycopg2
- python-dotenv
- Git and GitHub

## System Workflow

User enters new data
        ↓
Data validation
        ↓
Compare with existing records
        ↓
Similarity analysis
        ↓
┌───────────────┬────────────────┬─────────────────┐
│ Unique        │ Review         │ Duplicate       │
│ < 80%         │ 80–94.99%      │ ≥ 95%           │
└───────────────┴────────────────┴─────────────────┘
        ↓               ↓                ↓
    Insert          Log for review    Reject
        ↓               ↓                ↓
        └───────────────┴────────────────┘
                        ↓
               Supabase PostgreSQL

## Classification

### 1. Unique Record

Records with a similarity score below 80% are classified as unique and can be inserted into the database.

### 2. Potential Duplicate / Review

Records with a similarity score between 80% and 94.99% are classified as potential duplicates or possible false positives. These records are not automatically inserted and are recorded in the detection logs.

### 3. Duplicate

Records with a similarity score of 95% or above are classified as duplicates and are rejected to prevent redundant database entries.

## Project Structure

```text
Data-Redundancy-Removal-System/
│
├── app.py
├── database.py
├── duplicate_detector.py
├── validator.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── data/
    └── database.db
