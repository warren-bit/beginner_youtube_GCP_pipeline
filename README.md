# Beginner YouTube GCP Pipeline

## 📌 Project Overview

This project is a beginner-friendly cloud data engineering pipeline built to familiarize with **Google Cloud Platform (GCP)** services and real-world ETL concepts.

The pipeline extracts **YouTube channel analytics data** using the **YouTube Data API**, stores raw data in **Google Cloud Storage (GCS)** as a data lake, and loads structured data into **PostgreSQL (Cloud SQL)** as a data warehouse.

This project serves as a foundation for more advanced orchestration and time-series analytics, which will be implemented in a follow-up Apache Airflow project.

---

## 🎯 Objectives

* Learn how to work with external APIs in a data pipeline
* Understand cloud-based data ingestion using GCP
* Practice separating raw and structured data layers
* Gain hands-on experience with Cloud SQL and GCS
* Build a recruiter-ready, end-to-end data engineering project

---

## 🏗️ Architecture

**Data Flow:**

1. YouTube Data API (Extract)
2. Google Cloud Storage – Raw JSON (Data Lake)
3. PostgreSQL (Cloud SQL) – Structured Tables (Data Warehouse)

```
YouTube API
    ↓
Python Script
    ↓
GCS (Raw JSON)
    ↓
PostgreSQL (Cloud SQL)
```

---

## 🧰 Tech Stack

* **Language:** Python
* **API:** YouTube Data API v3
* **Cloud Platform:** Google Cloud Platform (GCP)
* **Storage:** Google Cloud Storage
* **Database:** PostgreSQL (Cloud SQL)
* **Libraries:**

  * requests
  * python-dotenv
  * google-cloud-storage
  * google-cloud-sql-connector
  * SQLAlchemy

---

## 📊 Data Collected

For a selected YouTube channel:

* Channel name
* Channel ID
* Subscriber count
* Total views
* Total video count
* Hidden subscriber flag
* Timestamp of data collection

Raw API responses are preserved in JSON format for traceability and reprocessing.

---

## 🗄️ Database Schema

**Table:** `youtube_channel_stats`

| Column             | Type      | Description           |
| ------------------ | --------- | --------------------- |
| channel_id         | TEXT      | YouTube channel ID    |
| channel_name       | TEXT      | Channel name          |
| collected_at       | TIMESTAMP | Data snapshot time    |
| subscribers        | INTEGER   | Subscriber count      |
| total_views        | BIGINT    | Total views           |
| video_count        | INTEGER   | Total videos          |
| hidden_subscribers | BOOLEAN   | Subscriber visibility |
| raw_data           | JSONB     | Raw API response      |

---

## ⚙️ Setup & Configuration

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/beginner_youtube_gcp_pipeline.git
cd beginner_youtube_gcp_pipeline
```

### 2️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Variables

Create a `.env` file:

```env
YOUTUBE_API_KEY=your_api_key
PROJECT_ID=your_gcp_project
REGION=your_region
INSTANCE_NAME=your_cloudsql_instance
DB_NAME=your_database
DB_USER=your_db_user
DB_PASSWORD=your_db_password
BUCKET_NAME=your_gcs_bucket
```

---

## ▶️ Running the Pipeline

```bash
python script.py
```

The script will:

1. Fetch channel statistics from YouTube API
2. Upload raw JSON data to GCS
3. Insert structured data into PostgreSQL

---

## ✅ Key Learning Outcomes

* API-based data extraction
* Cloud authentication and service interaction
* Raw vs structured data design
* Using SQLAlchemy with Cloud SQL
* Writing production-style Python ETL code

---

## 🚀 Next Steps (Planned Enhancements)

* Apache Airflow orchestration
* Daily time-series snapshots
* Video-level performance metrics
* Automated scheduling
* Data visualization dashboards

---

## 👤 Author

**Warren Odiwuor Otieno**
Aspiring Data Engineer | Cloud & Analytics Enthusiast

---

## 📄 License

This project is for educational and portfolio purposes.
