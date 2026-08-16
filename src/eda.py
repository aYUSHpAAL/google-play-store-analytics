"""
eda.py
------
Exploratory Data Analysis on the cleaned Google Play Store dataset.
Produces console summaries; visualizations are generated separately
by the notebook / plotting calls that import these functions.

Run: python src/eda.py
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "googleplaystore_cleaned.csv"


def load_clean(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    return df


def dataset_overview(df: pd.DataFrame) -> dict:
    return {
        "total_apps": len(df),
        "num_categories": df["category"].nunique(),
        "free_apps": int((df["type"] == "Free").sum()),
        "paid_apps": int((df["type"] == "Paid").sum()),
        "apps_with_rating": int(df["rating"].notna().sum()),
        "apps_without_rating": int(df["rating"].isna().sum()),
        "unique_apps": df["app"].nunique(),
        "avg_rating": round(df["rating"].mean(), 2),
        "avg_installs": round(df["installs"].mean(), 0),
        "avg_price_paid": round(df.loc[df["type"] == "Paid", "price"].mean(), 2),
    }


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby("category").agg(
        app_count=("app", "count"),
        avg_rating=("rating", "mean"),
        median_rating=("rating", "median"),
        total_reviews=("reviews", "sum"),
        avg_reviews=("reviews", "mean"),
        total_installs=("installs", "sum"),
        avg_installs=("installs", "mean"),
    ).reset_index()

    paid_pct = df.groupby("category")["is_free"].apply(lambda x: round((1 - x.mean()) * 100, 2))
    summary["pct_paid"] = summary["category"].map(paid_pct)
    return summary.sort_values("total_installs", ascending=False)


def rating_vs_installs_check(df: pd.DataFrame) -> pd.Series:
    """Do highly-rated apps actually get more installs? Compare mean installs by rating bucket."""
    return df.groupby("rating_bucket", observed=True)["installs"].mean().sort_index()


def pricing_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("price_bucket", observed=True).agg(
        app_count=("app", "count"),
        avg_installs=("installs", "mean"),
        avg_rating=("rating", "mean"),
    ).reset_index()


def engagement_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.dropna(subset=["review_to_install_ratio"])
        .groupby("category")["review_to_install_ratio"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )


def size_summary(df: pd.DataFrame) -> pd.DataFrame:
    bins = [0, 10, 30, 60, 100, df["size_mb"].max() + 1]
    labels = ["<10MB", "10-30MB", "30-60MB", "60-100MB", "100MB+"]
    df = df.copy()
    df["size_bucket_calc"] = pd.cut(df["size_mb"], bins=bins, labels=labels, include_lowest=True)
    return df.groupby("size_bucket_calc", observed=True).agg(
        app_count=("app", "count"),
        avg_installs=("installs", "mean"),
        avg_rating=("rating", "mean"),
    ).reset_index()


def run():
    df = load_clean()
    print("=== DATASET OVERVIEW ===")
    for k, v in dataset_overview(df).items():
        print(f"{k}: {v}")

    print("\n=== TOP 10 CATEGORIES BY INSTALLS ===")
    print(category_summary(df).head(10).to_string(index=False))

    print("\n=== RATING BUCKET vs AVG INSTALLS ===")
    print(rating_vs_installs_check(df))

    print("\n=== PRICING BUCKET SUMMARY ===")
    print(pricing_summary(df))

    print("\n=== TOP 10 ENGAGEMENT (REVIEW/INSTALL RATIO) CATEGORIES ===")
    print(engagement_summary(df).head(10).to_string(index=False))

    print("\n=== SIZE BUCKET SUMMARY ===")
    print(size_summary(df))


if __name__ == "__main__":
    run()
