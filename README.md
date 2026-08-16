# Google Play Store App Analytics

**Python · SQL · Pandas · MySQL**

An end-to-end data analytics project analysing 9,659 cleaned Google Play
Store apps (from a raw dataset of 10,841) to identify the factors that
drive app ratings, installs, pricing, and category performance — and to
turn those findings into concrete, data-backed business recommendations.

---

## Overview

This project simulates a real analytics engagement: a raw, messy scrape of
the Google Play Store is cleaned, loaded into a relational database,
explored statistically, and translated into recommendations a product or
growth team could act on. Every number in this README was computed from
the actual dataset — none of it is placeholder or invented.

## Business Problem

A team preparing to launch a new Android app (or evaluating an existing
portfolio) needs answers to concrete questions before committing resources:

- Which categories have real demand, and which are oversaturated?
- Does charging for an app help or hurt adoption?
- Does a higher star rating actually translate into more installs?
- Where is monetisation viable, and at what price point?
- What does a "successful" free app actually look like in the data?

This project answers each of these with evidence, not intuition.

## Objectives

1. Clean and structure a messy, real-world scraped dataset.
2. Explore ratings, installs, pricing, reviews, size, and category
   performance using Python.
3. Load the cleaned data into MySQL and answer business questions with SQL
   — from simple aggregations to window functions and CTEs.
4. Run statistical tests to separate genuine signal from noise.
5. Translate findings into concrete, actionable recommendations.

## Dataset

- **Source:** Kaggle "Google Play Store Apps" (lava18), a public scrape of
  Play Store metadata.
- **Raw size:** 10,841 rows × 13 columns.
- **Cleaned size:** 9,659 rows × 23 columns (after removing an unrecoverable
  corrupted row and de-duplicating repeated app listings).
- **Columns:** App, Category, Rating, Reviews, Size, Installs, Type, Price,
  Content Rating, Genres, Last Updated, Current Ver, Android Ver.

Place the raw file at `data/raw/googleplaystore.csv` before running the
pipeline (already included in this repository for reproducibility).

## Technologies Used

- **Python** — Pandas, NumPy for data wrangling
- **Matplotlib / Seaborn** — visualization
- **SciPy** — correlation and hypothesis testing
- **MySQL 8.0** — relational storage and SQL analysis
- **Jupyter Notebook** — exploratory workflow and narrative analysis

No Power BI, Tableau, Streamlit, Flask, or Excel is used anywhere in this
project, by design.

## Project Structure

```
google-play-store-analytics/
│
├── data/
│   ├── raw/googleplaystore.csv
│   └── processed/googleplaystore_cleaned.csv
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   └── 03_business_analysis.ipynb
│
├── sql/
│   ├── 01_database_setup.sql
│   ├── 02_data_quality.sql
│   ├── 03_basic_analysis.sql
│   ├── 04_advanced_analysis.sql
│   └── 05_business_insights.sql
│
├── src/
│   ├── data_cleaning.py
│   ├── eda.py
│   ├── analysis.py
│   ├── visualize.py
│   └── load_to_mysql.py
│
├── visualizations/        (15 PNG charts)
├── README.md
├── requirements.txt
└── .gitignore
```

## Data Cleaning

Handled in `src/data_cleaning.py` (see `notebooks/01_data_cleaning.ipynb`
for the walkthrough):

- **Column-shift bug repair** — one row had a missing `Category`, shifting
  every subsequent field one column left (its `Rating` of 1.9 was masquerading
  as a `Category`). Detected generically (not hardcoded to a row index) and
  repaired, then dropped since `Category` itself was unrecoverable.
- **Installs**: `"10,000+"` → `10000` (int)
- **Price**: `"$4.99"` → `4.99` (float)
- **Size**: `"19M"` → `19.0` MB, `"14k"` → `0.0137` MB, `"Varies with device"` → `NaN`
- **Rating**: bounded to a valid [0, 5] range
- **Type**: missing/invalid values inferred from `Price` (price > 0 ⇒ Paid)
- **Duplicates**: exact duplicate rows dropped; duplicate app names collapsed
  to the entry with the most reviews
- **Derived features**: `installs_numeric`, `price_numeric`, `size_mb`,
  `is_free`, `log_installs`, `log_reviews`, `review_to_install_ratio`,
  `updated_year`, `updated_month`, `install_bucket`, `rating_bucket`,
  `price_bucket`

**Result:** 10,841 → 9,659 rows, 33 valid categories, ratings correctly
bounded, zero remaining data-type inconsistencies.

## Exploratory Data Analysis

Performed in `notebooks/02_exploratory_data_analysis.ipynb` and
`src/eda.py`. Highlights:

- **92.2%** of apps are free (8,905 of 9,659); only **7.8%** are paid.
- Average rating across all rated apps: **4.17** / 5.
- **GAME** leads total installs at **13.46 billion**, followed by
  **COMMUNICATION** (11.04B) and **TOOLS** (8.10B).
- **FAMILY** is the most crowded category by app count (1,876 apps), followed
  by **GAME** (946) and **TOOLS** (829).
- Rating vs. installs is **not** a clean upward line: apps in the 4–4.5
  rating bucket average **13.8M** installs, actually *higher* than apps in
  the top 4.5–5 bucket (**5.5M**) — a genuinely counter-intuitive finding
  explored further below.

## SQL Analysis

MySQL database `google_play_analytics`, table `apps` (9,659 rows loaded via
`src/load_to_mysql.py`). Query files:

- `01_database_setup.sql` — schema, indexes
- `02_data_quality.sql` — null/duplicate/outlier audits run directly against
  the loaded table
- `03_basic_analysis.sql` — 15 foundational aggregation queries
- `04_advanced_analysis.sql` — 15 queries using CTEs, window functions
  (`RANK()`, `ROW_NUMBER()`, `PARTITION BY`), and conditional aggregation
- `05_business_insights.sql` — 7 queries directly answering strategic
  questions (content-rating performance, size buckets, monetisation
  potential by category, etc.)

Sample result — installs by price bucket (from query 15 in
`04_advanced_analysis.sql`):

| price_bucket | avg_installs | app_count |
|---|---|---|
| Free | 8,452,012 | 8,905 |
| $5–$10 | 176,779 | 84 |
| $0.01–$1 | 131,067 | 148 |
| $1–$5 | 49,534 | 449 |
| $10+ | 11,998 | 73 |

## Key Findings

1. **Free apps dominate the install base.**
   *Evidence:* Free apps average **8,452,012** installs vs. **76,079** for
   paid apps (median: 100,000 vs. 1,000) — a Mann-Whitney U test confirms
   this gap is statistically significant (p ≈ 8×10⁻¹¹⁶).
   *Implication:* For mass-market reach, a freemium or ad-supported model
   massively outperforms an upfront paid model.

2. **Paid apps rate slightly higher, but reach far fewer users.**
   *Evidence:* Paid apps average a **4.262** rating vs. **4.166** for free
   apps (Welch's t-test, p = 0.00005 — significant).
   *Implication:* Paying users self-select and tend to be more satisfied,
   but this doesn't translate into scale.

3. **Rating is a weak predictor of installs.**
   *Evidence:* Pearson r = **0.040** between rating and installs (Spearman
   r = 0.027) — both essentially negligible, and installs in the 4.5–5
   rating bucket (5.5M avg) are *lower* than in the 4–4.5 bucket (13.8M avg).
   *Implication:* A five-star rating alone won't drive downloads — discovery,
   marketing, and reviews volume matter more.

4. **Reviews volume is strongly tied to installs (unsurprisingly).**
   *Evidence:* Pearson r = **0.625**, Spearman r = **0.968** between reviews
   and installs.
   *Implication:* Review count is a much stronger popularity signal than
   star rating — useful as a proxy metric when installs data isn't directly
   available.

5. **Price has a real, negative relationship with installs, but it isn't
   perfectly linear.**
   *Evidence:* Spearman r = **-0.232** (p ≈ 9×10⁻¹¹⁸) between price and
   installs. Notably, the **$5–$10** bucket (176,779 avg installs) actually
   outperforms the **$0.01–$1** bucket (131,067 avg installs).
   *Implication:* Pricing too low may signal low quality; a modest,
   deliberate price point can outperform "impulse-buy" pricing.

6. **GAME is both the most competitive and the highest-demand category.**
   *Evidence:* 946 apps, 13.46B total installs, and the highest engagement
   proxy score (review-to-install ratio 0.056, the highest of any category).
   *Implication:* Huge opportunity, but also the hardest category to break
   into — differentiation is essential.

7. **MEDICAL is a low-demand, high-monetisation category.**
   *Evidence:* Average installs of just **96,944** (lowest of any category)
   but the second-highest paid-app share at **20.76%**.
   *Implication:* Medical apps trade install volume for willingness to pay —
   a niche, expertise-driven monetisation play rather than a mass-market one.

8. **App size correlates positively, moderately, with installs.**
   *Evidence:* Pearson r = 0.134 (Spearman r = 0.310) between size and
   installs; apps in the 60–100MB bucket average **13.3M** installs vs.
   **1.1M** for apps under 10MB.
   *Implication:* Larger, presumably feature-richer apps tend to attract
   more installs — but "Varies with device" apps (dynamically sized, often
   large enterprise/media apps like Google's own) average even higher, at
   **35.7M**.

9. **Content rating "Teen" slightly outperforms "Everyone" on both metrics.**
   *Evidence:* Teen-rated apps average 4.23 rating / 15.9M installs vs.
   Everyone-rated apps at 4.17 rating / 6.6M installs.
   *Implication:* This likely reflects category mix (games and social apps
   skew Teen) rather than a direct effect of the rating itself.

10. **A near-duplicate "I am Rich" novelty-app cluster inflates the top of
    the price distribution.**
    *Evidence:* 16 nearly-identical apps priced at $379.99–$400.00 (e.g.
    "I am rich", "I Am Rich Premium", "Eu Sou Rico") appear as separate
    listings, most with minimal functionality.
    *Implication:* Analysts should treat extreme-price apps as intentional
    outliers/novelty products, not representative premium pricing signals.

11. **Freshness correlates with quality.**
    *Evidence:* Apps last updated in 2018 average a 4.23 rating and 11.2M
    installs; apps last updated in 2012 average a 3.79 rating and 538K
    installs.
    *Implication:* Update cadence is a meaningful proxy for active
    maintenance and user trust — a stale app is a red flag.

12. **A "blue ocean" opportunity set exists.**
    *Evidence:* Categories with below-median app count *and* above-median
    average installs include COMMUNICATION, PRODUCTIVITY, and PHOTOGRAPHY —
    high demand, comparatively lower supply pressure than GAME or FAMILY.
    *Implication:* These categories offer a better demand-to-competition
    ratio for a new entrant than the most crowded categories.

## Business Recommendations

1. **Default to a free, ad-supported or freemium model** for any
   mass-market app — the data shows an overwhelming, statistically
   significant install advantage over paid apps.
2. **Target under-served, high-demand categories** such as COMMUNICATION,
   PRODUCTIVITY, or PHOTOGRAPHY rather than the most saturated GAME or
   FAMILY categories, unless prepared to out-differentiate incumbents.
3. **If monetising directly, avoid the sub-$1 "impulse tier."** The data
   shows $5–$10 apps outperform $0.01–$1 apps in average installs — cheap
   pricing does not reliably drive volume and may cheapen perceived quality.
4. **Don't over-optimise for star rating alone.** Since rating barely
   correlates with installs, invest more in discoverability, ASO, and review
   volume than in chasing a marginal ratings bump.
5. **Treat review count as a leading indicator of traction** — it's a far
   stronger, more available signal of real popularity than star rating.
6. **Maintain an active update cadence.** Apps updated within the last year
   show meaningfully higher ratings and installs than stale ones; this is
   a low-cost lever compared to acquisition spend.
7. **For niche, expertise-driven categories (e.g. MEDICAL, FINANCE,
   BUSINESS), lean into paid/premium pricing** rather than chasing install
   volume — these categories already show the market rewards willingness to
   pay over reach.
8. **Invest in app depth/size where relevant to the category.** The positive
   size-installs relationship suggests users are not deterred by (and may be
   drawn to) more feature-complete apps, contrary to the common "keep it
   lightweight" assumption.

## Visualizations

All 15 charts are generated by `src/visualize.py` and saved to
`visualizations/`:

1. Distribution of ratings
2. Top 10 categories by app count
3. Top 10 categories by installs
4. Free vs paid app distribution
5. Installs by app type (log scale)
6. Rating vs installs
7. Reviews vs installs
8. Price vs installs (paid apps)
9. Average rating by category
10. Average installs by category
11. Price distribution of paid apps
12. Rating distribution by app type
13. App size vs installs
14. Correlation heatmap
15. Review-to-install ratio by category

## How to Run the Project

### 1. Python Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. MySQL Setup

```bash
# Start MySQL locally, then:
mysql -u root -p < sql/01_database_setup.sql
python src/load_to_mysql.py     # loads the cleaned CSV into MySQL
```

Update the `DB_CONFIG` dict at the top of `src/load_to_mysql.py` with your
own host/user/password before running.

### 3. Run the Pipeline End-to-End

```bash
python src/data_cleaning.py     # raw -> cleaned CSV
python src/load_to_mysql.py     # cleaned CSV -> MySQL
python src/eda.py               # console EDA summary
python src/analysis.py          # correlations + hypothesis tests
python src/visualize.py         # generates all 15 charts
```

### 4. Explore the Notebooks

```bash
jupyter notebook notebooks/
```

Run in order: `01_data_cleaning.ipynb` → `02_exploratory_data_analysis.ipynb`
→ `03_business_analysis.ipynb`.

### 5. Run the SQL Analysis

```bash
mysql -u root -p google_play_analytics < sql/02_data_quality.sql
mysql -u root -p google_play_analytics < sql/03_basic_analysis.sql
mysql -u root -p google_play_analytics < sql/04_advanced_analysis.sql
mysql -u root -p google_play_analytics < sql/05_business_insights.sql
```

## Skills Demonstrated

- End-to-end data pipeline design (raw → cleaned → database → analysis)
- Robust, generic (non-hardcoded) handling of real-world data-entry bugs
- Pandas data wrangling: type coercion, string parsing, feature engineering
- SQL: schema design, indexing, CTEs, window functions
  (`RANK`, `ROW_NUMBER`, `PARTITION BY`), conditional aggregation, subqueries
- Statistical analysis: Pearson/Spearman correlation, Welch's t-test,
  Mann-Whitney U test, correct handling of skewed distributions via log
  transforms
- Data visualization with Matplotlib/Seaborn
- Translating quantitative findings into business recommendations
- Reproducible project structure suitable for a GitHub portfolio
