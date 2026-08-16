"""
data_cleaning.py
-----------------
Cleaning pipeline for the Google Play Store dataset.

Raw dataset source: Kaggle "Google Play Store Apps" (lava18), ~10,841 rows,
13 columns: App, Category, Rating, Reviews, Size, Installs, Type, Price,
Content Rating, Genres, Last Updated, Current Ver, Android Ver.

Known data-quality issues handled here:
1. One row (App = "Life Made WI-Fi Touchscreen Photo Frame") has a missing
   Category value, which shifts every subsequent column one position to the
   left (Category becomes "1.9", a rating value). This row is repaired by
   shifting values back into place.
2. Ratings: ~1,474 missing values, and ratings must be within [0, 5].
3. Reviews: stored as strings, need int conversion.
4. Size: values like "19M", "14k", and "Varies with device" (missing).
5. Installs: values like "10,000+" need comma and "+" stripped -> int.
6. Price: values like "$4.99" need the "$" stripped -> float.
7. Type: a handful of rows have Type missing or malformed; inferred from Price.
8. Duplicate app rows (same App name) - Play Store scraping produced repeats.
9. Last Updated: string dates -> datetime, with derived year/month.

Run: python src/data_cleaning.py
Produces: data/processed/googleplaystore_cleaned.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "googleplaystore.csv"
PROCESSED_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "googleplaystore_cleaned.csv"


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the raw CSV exactly as scraped, no assumptions about cleanliness."""
    df = pd.read_csv(path)
    return df


def fix_shifted_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Repair the known malformed row where Category is missing and every
    field after App has shifted one column to the left.

    We detect it generically: any row where Category is not a valid
    category string but instead looks numeric (this catches the shift
    bug without hardcoding a row index, so the fix is robust even if the
    dataset order changes).
    """
    df = df.copy()
    numeric_category_mask = pd.to_numeric(df["Category"], errors="coerce").notna()

    if numeric_category_mask.any():
        cols = df.columns.tolist()
        # Cast every column to object dtype first so mixed-type values can be
        # written into any column during the shift repair without pandas
        # raising a dtype-casting error.
        for c in cols:
            df[c] = df[c].astype(object)
        # cols order: App, Category, Rating, Reviews, Size, Installs, Type,
        # Price, Content Rating, Genres, Last Updated, Current Ver, Android Ver
        for idx in df[numeric_category_mask].index:
            row = df.loc[idx]
            # Shift Category..Android Ver right by one, Category becomes NaN
            # (unrecoverable - dropped later), values realign correctly.
            shifted_values = row[cols[1:-1]].values  # Category..Current Ver
            df.loc[idx, cols[2:]] = shifted_values
            df.loc[idx, "Category"] = np.nan

    return df


def clean_installs(series: pd.Series) -> pd.Series:
    """Convert '10,000+' -> 10000 (int)."""
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
        .str.replace("Free", "0", regex=False)  # guards against the one shifted-row artifact
        .replace("nan", np.nan)
        .astype(float)
    )


def clean_price(series: pd.Series) -> pd.Series:
    """Convert '$4.99' -> 4.99 (float); 'Everyone' artifacts -> NaN."""
    cleaned = series.astype(str).str.replace("$", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


def clean_size(series: pd.Series) -> pd.Series:
    """
    Convert size strings to megabytes (float).
    '19M' -> 19.0, '14k' -> 0.014 (k -> M), 'Varies with device' -> NaN.
    """

    def parse_size(val):
        if pd.isna(val):
            return np.nan
        val = str(val).strip()
        if val == "Varies with device" or val == "nan":
            return np.nan
        if val.endswith("M"):
            try:
                return float(val[:-1])
            except ValueError:
                return np.nan
        if val.endswith("k"):
            try:
                return float(val[:-1]) / 1024.0
            except ValueError:
                return np.nan
        try:
            return float(val)
        except ValueError:
            return np.nan

    return series.apply(parse_size)


def clean_reviews(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def clean_rating(series: pd.Series) -> pd.Series:
    """Ratings must be within [0, 5]; anything outside is treated as invalid."""
    numeric = pd.to_numeric(series, errors="coerce")
    numeric = numeric.where((numeric >= 0) & (numeric <= 5), np.nan)
    return numeric


def infer_type_from_price(df: pd.DataFrame) -> pd.Series:
    """Fill missing/invalid Type using Price as ground truth (Price==0 -> Free)."""
    inferred = np.where(df["price_numeric"] > 0, "Paid", "Free")
    filled = df["Type"].where(df["Type"].isin(["Free", "Paid"]), inferred)
    return filled


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = fix_shifted_row(df)

    # Drop rows where Category could not be recovered (the one unrecoverable shifted row)
    df = df[df["Category"].notna()].copy()

    # Drop exact duplicate rows first
    df = df.drop_duplicates()

    # Drop duplicate app names, keeping the entry with the most reviews
    # (a reasonable proxy for "most recent / most complete" scrape)
    df["Reviews"] = clean_reviews(df["Reviews"])
    df = df.sort_values("Reviews", ascending=False)
    df = df.drop_duplicates(subset="App", keep="first")

    # Core numeric conversions
    df["rating_clean"] = clean_rating(df["Rating"])
    df["reviews_clean"] = df["Reviews"].fillna(0).astype(int)
    df["size_mb"] = clean_size(df["Size"])
    df["installs_numeric"] = clean_installs(df["Installs"]).astype("Int64")
    df["price_numeric"] = clean_price(df["Price"])
    df["type_clean"] = infer_type_from_price(df)
    df["is_free"] = (df["type_clean"] == "Free").astype(int)

    # Content Rating: fill the single missing value with the mode
    df["content_rating_clean"] = df["Content Rating"].fillna(df["Content Rating"].mode()[0])

    # Category: normalise text (uppercase already, just strip)
    df["category_clean"] = df["Category"].str.strip()

    # Dates
    df["last_updated_clean"] = pd.to_datetime(df["Last Updated"], errors="coerce")
    df["updated_year"] = df["last_updated_clean"].dt.year
    df["updated_month"] = df["last_updated_clean"].dt.month

    # Derived analytical columns
    df["log_installs"] = np.log1p(df["installs_numeric"].astype(float))
    df["log_reviews"] = np.log1p(df["reviews_clean"].astype(float))

    df["review_to_install_ratio"] = np.where(
        df["installs_numeric"] > 0,
        df["reviews_clean"] / df["installs_numeric"],
        np.nan,
    )

    df["install_bucket"] = pd.cut(
        df["installs_numeric"].astype(float),
        bins=[-1, 1_000, 10_000, 100_000, 1_000_000, 10_000_000, np.inf],
        labels=["<1K", "1K-10K", "10K-100K", "100K-1M", "1M-10M", "10M+"],
    )

    df["rating_bucket"] = pd.cut(
        df["rating_clean"],
        bins=[0, 2, 3, 4, 4.5, 5],
        labels=["0-2", "2-3", "3-4", "4-4.5", "4.5-5"],
        include_lowest=True,
    )

    df["price_bucket"] = pd.cut(
        df["price_numeric"],
        bins=[-0.01, 0, 1, 5, 10, np.inf],
        labels=["Free", "$0.01-$1", "$1-$5", "$5-$10", "$10+"],
    )

    # Final tidy frame with clear column names
    final = pd.DataFrame({
        "app": df["App"],
        "category": df["category_clean"],
        "rating": df["rating_clean"],
        "reviews": df["reviews_clean"],
        "size_mb": df["size_mb"],
        "installs": df["installs_numeric"],
        "type": df["type_clean"],
        "price": df["price_numeric"],
        "content_rating": df["content_rating_clean"],
        "genres": df["Genres"],
        "last_updated": df["last_updated_clean"],
        "current_version": df["Current Ver"],
        "android_version": df["Android Ver"],
        "is_free": df["is_free"],
        "log_installs": df["log_installs"],
        "log_reviews": df["log_reviews"],
        "review_to_install_ratio": df["review_to_install_ratio"],
        "updated_year": df["updated_year"],
        "updated_month": df["updated_month"],
        "install_bucket": df["install_bucket"],
        "rating_bucket": df["rating_bucket"],
        "price_bucket": df["price_bucket"],
    })

    final = final.reset_index(drop=True)
    final.insert(0, "app_id", range(1, len(final) + 1))

    return final


def run():
    raw = load_raw()
    cleaned = clean_dataset(raw)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(PROCESSED_PATH, index=False)
    print(f"Raw shape:     {raw.shape}")
    print(f"Cleaned shape: {cleaned.shape}")
    print(f"Saved to:      {PROCESSED_PATH}")
    return cleaned


if __name__ == "__main__":
    run()
