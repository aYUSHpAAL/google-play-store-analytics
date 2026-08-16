"""
visualize.py
------------
Generates all 15 required charts for the project and saves them to
visualizations/. Run: python src/visualize.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "googleplaystore_cleaned.csv"
OUT_DIR = Path(__file__).resolve().parent.parent / "visualizations"

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110


def load():
    df = pd.read_csv(DATA_PATH)
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    return df


def savefig(name):
    plt.tight_layout()
    plt.savefig(OUT_DIR / name, bbox_inches="tight")
    plt.close()
    print(f"saved {name}")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    df = load()

    # 1. Distribution of ratings
    plt.figure(figsize=(8, 5))
    sns.histplot(df["rating"].dropna(), bins=20, kde=True, color="#4C72B0")
    plt.title("Distribution of App Ratings")
    plt.xlabel("Rating")
    plt.ylabel("Number of Apps")
    savefig("01_rating_distribution.png")

    # 2. Top 10 categories by number of apps
    top_count = df["category"].value_counts().head(10)
    plt.figure(figsize=(9, 5))
    sns.barplot(x=top_count.values, y=top_count.index, hue=top_count.index, palette="viridis", legend=False)
    plt.title("Top 10 Categories by Number of Apps")
    plt.xlabel("App Count")
    plt.ylabel("Category")
    savefig("02_top_categories_by_count.png")

    # 3. Top 10 categories by installs
    top_installs = df.groupby("category")["installs"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(9, 5))
    sns.barplot(x=top_installs.values, y=top_installs.index, hue=top_installs.index, palette="mako", legend=False)
    plt.title("Top 10 Categories by Total Installs")
    plt.xlabel("Total Installs")
    plt.ylabel("Category")
    savefig("03_top_categories_by_installs.png")

    # 4. Free vs paid app distribution
    plt.figure(figsize=(6, 6))
    type_counts = df["type"].value_counts()
    plt.pie(type_counts.values, labels=type_counts.index, autopct="%1.1f%%",
            colors=["#55A868", "#C44E52"], startangle=90)
    plt.title("Free vs Paid App Distribution")
    savefig("04_free_vs_paid_distribution.png")

    # 5. Installs by app type (boxplot on log scale)
    plt.figure(figsize=(7, 5))
    sns.boxplot(data=df, x="type", y="log_installs", hue="type", palette="Set2", legend=False)
    plt.title("Installs by App Type (log scale)")
    plt.xlabel("App Type")
    plt.ylabel("log(1 + Installs)")
    savefig("05_installs_by_type.png")

    # 6. Rating vs installs
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df.sample(min(3000, len(df)), random_state=42),
                     x="rating", y="log_installs", alpha=0.3, color="#4C72B0")
    plt.title("Rating vs Installs (log scale)")
    plt.xlabel("Rating")
    plt.ylabel("log(1 + Installs)")
    savefig("06_rating_vs_installs.png")

    # 7. Reviews vs installs
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df.sample(min(3000, len(df)), random_state=42),
                     x="log_reviews", y="log_installs", alpha=0.3, color="#C44E52")
    plt.title("Reviews vs Installs (log-log scale)")
    plt.xlabel("log(1 + Reviews)")
    plt.ylabel("log(1 + Installs)")
    savefig("07_reviews_vs_installs.png")

    # 8. Price vs installs (paid apps only)
    paid = df[df["type"] == "Paid"]
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=paid, x="price", y="log_installs", alpha=0.5, color="#8172B2")
    plt.title("Price vs Installs (Paid Apps Only)")
    plt.xlabel("Price ($)")
    plt.ylabel("log(1 + Installs)")
    savefig("08_price_vs_installs.png")

    # 9. Average rating by category (top 15 by app count for readability)
    top_cats = df["category"].value_counts().head(15).index
    avg_rating_cat = df[df["category"].isin(top_cats)].groupby("category")["rating"].mean().sort_values()
    plt.figure(figsize=(9, 7))
    sns.barplot(x=avg_rating_cat.values, y=avg_rating_cat.index, hue=avg_rating_cat.index, palette="crest", legend=False)
    plt.title("Average Rating by Category (Top 15 Categories by App Count)")
    plt.xlabel("Average Rating")
    plt.ylabel("Category")
    plt.xlim(3.5, 4.6)
    savefig("09_avg_rating_by_category.png")

    # 10. Average installs by category (top 15)
    avg_installs_cat = df[df["category"].isin(top_cats)].groupby("category")["installs"].mean().sort_values()
    plt.figure(figsize=(9, 7))
    sns.barplot(x=avg_installs_cat.values, y=avg_installs_cat.index, hue=avg_installs_cat.index, palette="flare", legend=False)
    plt.title("Average Installs by Category (Top 15 Categories by App Count)")
    plt.xlabel("Average Installs")
    plt.ylabel("Category")
    savefig("10_avg_installs_by_category.png")

    # 11. Price distribution of paid apps
    plt.figure(figsize=(8, 5))
    sns.histplot(paid[paid["price"] < 100]["price"], bins=30, color="#DD8452")
    plt.title("Price Distribution of Paid Apps (under $100)")
    plt.xlabel("Price ($)")
    plt.ylabel("Number of Apps")
    savefig("11_price_distribution_paid.png")

    # 12. Rating distribution by app type
    plt.figure(figsize=(8, 5))
    sns.kdeplot(data=df, x="rating", hue="type", fill=True, common_norm=False, alpha=0.4)
    plt.title("Rating Distribution by App Type")
    plt.xlabel("Rating")
    savefig("12_rating_distribution_by_type.png")

    # 13. App size vs installs
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df.dropna(subset=["size_mb"]).sample(min(3000, df["size_mb"].notna().sum()), random_state=42),
                     x="size_mb", y="log_installs", alpha=0.3, color="#64B5CD")
    plt.title("App Size (MB) vs Installs (log scale)")
    plt.xlabel("Size (MB)")
    plt.ylabel("log(1 + Installs)")
    savefig("13_size_vs_installs.png")

    # 14. Correlation heatmap
    corr_cols = ["rating", "reviews", "size_mb", "installs", "price", "log_installs", "log_reviews"]
    plt.figure(figsize=(8, 6))
    sns.heatmap(df[corr_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0)
    plt.title("Correlation Heatmap of Numeric Features")
    savefig("14_correlation_heatmap.png")

    # 15. Review-to-install ratio by category (top 15 by app count)
    ratio_cat = (
        df[df["category"].isin(top_cats)]
        .dropna(subset=["review_to_install_ratio"])
        .groupby("category")["review_to_install_ratio"]
        .mean()
        .sort_values()
    )
    plt.figure(figsize=(9, 7))
    sns.barplot(x=ratio_cat.values, y=ratio_cat.index, hue=ratio_cat.index, palette="rocket", legend=False)
    plt.title("Review-to-Install Ratio by Category (Engagement Proxy)")
    plt.xlabel("Avg Review-to-Install Ratio")
    plt.ylabel("Category")
    savefig("15_review_to_install_ratio_by_category.png")

    print("\nAll 15 visualizations saved to", OUT_DIR)


if __name__ == "__main__":
    main()
