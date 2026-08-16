"""
analysis.py
-----------
Statistical analysis: Pearson/Spearman correlations and simple hypothesis
tests (free vs paid comparisons). Correlation is used to describe
association strength only; causal language is deliberately avoided.

Run: python src/analysis.py
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "googleplaystore_cleaned.csv"


def load_clean() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def correlation_table(df: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("rating", "installs"),
        ("rating", "reviews"),
        ("price", "installs"),
        ("price", "rating"),
        ("size_mb", "installs"),
        ("reviews", "installs"),
    ]
    rows = []
    for a, b in pairs:
        sub = df[[a, b]].dropna()
        pearson_r, pearson_p = stats.pearsonr(sub[a], sub[b])
        spearman_r, spearman_p = stats.spearmanr(sub[a], sub[b])
        rows.append({
            "pair": f"{a} vs {b}",
            "n": len(sub),
            "pearson_r": round(pearson_r, 4),
            "pearson_p": round(pearson_p, 6),
            "spearman_r": round(spearman_r, 4),
            "spearman_p": round(spearman_p, 6),
        })
    return pd.DataFrame(rows)


def free_vs_paid_tests(df: pd.DataFrame) -> dict:
    free_rating = df.loc[df["type"] == "Free", "rating"].dropna()
    paid_rating = df.loc[df["type"] == "Paid", "rating"].dropna()
    free_installs = df.loc[df["type"] == "Free", "installs"].dropna()
    paid_installs = df.loc[df["type"] == "Paid", "installs"].dropna()

    rating_t, rating_p = stats.ttest_ind(free_rating, paid_rating, equal_var=False)
    # installs are heavily skewed -> Mann-Whitney U is more appropriate than a t-test
    installs_u, installs_p = stats.mannwhitneyu(free_installs, paid_installs, alternative="two-sided")

    return {
        "free_avg_rating": round(free_rating.mean(), 3),
        "paid_avg_rating": round(paid_rating.mean(), 3),
        "rating_ttest_stat": round(rating_t, 3),
        "rating_ttest_p": round(rating_p, 6),
        "free_median_installs": int(free_installs.median()),
        "paid_median_installs": int(paid_installs.median()),
        "installs_mannwhitney_stat": round(installs_u, 1),
        "installs_mannwhitney_p": round(installs_p, 10),
    }


def run():
    df = load_clean()

    print("=== CORRELATION ANALYSIS (Pearson & Spearman) ===")
    corr = correlation_table(df)
    print(corr.to_string(index=False))
    print(
        "\nNote: correlation measures association strength, not causation. "
        "A positive correlation between reviews and installs, for example, "
        "does not prove that reviews CAUSE installs -- both likely stem from "
        "a shared underlying driver, an app's overall popularity."
    )

    print("\n=== FREE vs PAID HYPOTHESIS TESTS ===")
    results = free_vs_paid_tests(df)
    for k, v in results.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    run()
