"""
load_to_mysql.py
-----------------
Loads data/processed/googleplaystore_cleaned.csv into the
google_play_analytics.apps table (created by sql/01_database_setup.sql).
"""

import numpy as np
import pandas as pd
import mysql.connector
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "googleplaystore_cleaned.csv"

DB_CONFIG = dict(host="localhost", user="root", password="ClaudePass123!", database="google_play_analytics")


def nan_to_none(val):
    if pd.isna(val):
        return None
    return val


def main():
    df = pd.read_csv(CSV_PATH)
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce").dt.strftime("%Y-%m-%d")

    cols = [
        "app_id", "app", "category", "rating", "reviews", "size_mb", "installs",
        "type", "price", "content_rating", "genres", "last_updated",
        "current_version", "android_version", "is_free", "log_installs",
        "log_reviews", "review_to_install_ratio", "updated_year", "updated_month",
        "install_bucket", "rating_bucket", "price_bucket",
    ]

    records = []
    for _, row in df[cols].iterrows():
        records.append(tuple(nan_to_none(v) for v in row))

    insert_sql = f"""
        INSERT INTO apps
        (app_id, app, category, rating, reviews, size_mb, installs, app_type,
         price, content_rating, genres, last_updated, current_version,
         android_version, is_free, log_installs, log_reviews,
         review_to_install_ratio, updated_year, updated_month,
         install_bucket, rating_bucket, price_bucket)
        VALUES ({','.join(['%s'] * len(cols))})
    """

    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS=0;")
    cur.executemany(insert_sql, records)
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM apps;")
    count = cur.fetchone()[0]
    print(f"Rows inserted: {count}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
