import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from google.cloud import storage
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from sqlalchemy import text

# Load environment variables from .env file
load_dotenv()

# Required environment variables
API_KEY = os.getenv('YOUTUBE_API_KEY')
PROJECT_ID = os.getenv('PROJECT_ID')
REGION = os.getenv('REGION')
INSTANCE_NAME = os.getenv('INSTANCE_NAME')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'first-pipeline-raw-data')

# Validate required environment variables
missing = []
for name, value in [
    ('YOUTUBE_API_KEY', API_KEY),
    ('PROJECT_ID', PROJECT_ID),
    ('REGION', REGION),
    ('INSTANCE_NAME', INSTANCE_NAME),
    ('DB_NAME', DB_NAME),
    ('DB_USER', DB_USER),
    ('DB_PASSWORD', DB_PASSWORD),
]:
    if not value:
        missing.append(name)

if missing:
    print(f"Missing required environment variables: {', '.join(missing)}")
    print("Please check your .env file")
    exit(1)

BASE_URL = "https://www.googleapis.com/youtube/v3"
CHANNEL_ID = "UCWf7prs03RhgFfC5Aind0Ww"  # AFTV Xtra


def get_channel_stats(channel_id=CHANNEL_ID):
    """
    Fetch YouTube channel statistics and metadata from the YouTube Data API.

    Args:
        channel_id (str): YouTube channel ID.

    Returns:
        dict | None: A dictionary containing channel statistics and metadata,
                     or None if the API request fails or no data is found.
    """
    params = {
        'part': 'statistics,snippet',
        'id': channel_id,
        'key': API_KEY
    }

    try:
        r = requests.get(f"{BASE_URL}/channels", params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        if 'items' not in data or not data['items']:
            print(f"Error: No channel found for ID: {channel_id}")
            return None

        item = data['items'][0]
        stats = item['statistics']
        snippet = item['snippet']

        return {
            "Channel_Name": snippet.get('title', 'Unknown'),
            "Channel_ID": item['id'],
            "Date_Collected": datetime.now(timezone.utc).isoformat(),
            "Subscribers": stats.get('subscriberCount', 'Hidden'),
            "Views": stats.get('viewCount', '0'),
            "Videos": stats.get('videoCount', '0'),
            "Hidden_Subscribers": stats.get('hiddenSubscriberCount', False)
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from YouTube API: {e}")
        return None


def upload_to_gcs(bucket_name, data, file_name):
    """
    Upload raw JSON data to Google Cloud Storage.

    Args:
        bucket_name (str): Name of the GCS bucket.
        data (dict): Data to upload.
        file_name (str): Name of the destination file in GCS.

    Returns:
        bool: True if upload succeeds, False otherwise.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        json_data = json.dumps(data, indent=4)
        blob.upload_from_string(json_data, content_type='application/json')

        print(f"File {file_name} uploaded to bucket {bucket_name} successfully.")
        return True
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        return False


def get_sqlalchemy_engine():
    """
    Create a SQLAlchemy engine for connecting to a Cloud SQL PostgreSQL instance
    using the Cloud SQL Python Connector.

    Returns:
        sqlalchemy.Engine | None: SQLAlchemy engine if successful, otherwise None.
    """
    try:
        connector = Connector(ip_type=IPTypes.PUBLIC)  # Use PRIVATE if required

        def getconn():
            return connector.connect(
                f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}",
                "pg8000",
                user=DB_USER,
                password=DB_PASSWORD,
                db=DB_NAME
            )

        engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
        )
        return engine

    except Exception as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        return None


def load_to_postgres(stats):
    """
    Load structured YouTube channel statistics into PostgreSQL.

    Args:
        stats (dict): Channel statistics data.

    Returns:
        bool: True if data insertion succeeds, False otherwise.
    """
    if not stats:
        print("No data to load into Postgres")
        return False

    engine = get_sqlalchemy_engine()
    if not engine:
        print("Cannot connect to database - engine creation failed")
        return False

    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO youtube_channel_stats (
                    channel_id, channel_name, collected_at,
                    subscribers, total_views, video_count,
                    hidden_subscribers, raw_data
                )
                VALUES (
                    :channel_id, :channel_name, :collected_at,
                    :subscribers, :total_views, :video_count,
                    :hidden_subscribers, :raw_data
                )
            """)

            conn.execute(
                query,
                {
                    "channel_id": stats["Channel_ID"],
                    "channel_name": stats["Channel_Name"],
                    "collected_at": stats["Date_Collected"],
                    "subscribers": int(stats["Subscribers"]) if stats["Subscribers"] != "Hidden" else None,
                    "total_views": int(stats["Views"]),
                    "video_count": int(stats["Videos"]),
                    "hidden_subscribers": stats["Hidden_Subscribers"],
                    "raw_data": json.dumps(stats),
                }
            )

            conn.commit()
            print("Data successfully inserted into PostgreSQL")
            return True

    except Exception as e:
        print(f"Error loading data into Postgres: {e}")
        return False


if __name__ == "__main__":
    """
    Main execution block for running the pipeline end-to-end:
    1. Extract YouTube channel statistics
    2. Upload raw data to GCS
    3. Load structured data into PostgreSQL
    """
    stats = get_channel_stats()

    if not stats:
        print("Failed to retrieve channel statistics.")
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_name = f"youtube_stats_{CHANNEL_ID}_{timestamp}.json"

        # 1. Upload raw data to GCS (data lake)
        gcs_success = upload_to_gcs(BUCKET_NAME, stats, file_name)

        # 2. Load structured data to PostgreSQL (warehouse)
        pg_success = load_to_postgres(stats)

        print("\nPipeline summary:")
        print(f"  GCS upload:       {'SUCCESS' if gcs_success else 'FAILED'}")
        print(f"  Postgres insert:  {'SUCCESS' if pg_success else 'FAILED'}")
