# Interview Preparation — Google Play Store App Analytics

## 1. Strongest SQL Queries to Discuss

**1. Top 3 apps per category by installs (window function)**
```sql
WITH ranked AS (
    SELECT app, category, installs,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY installs DESC) AS rn
    FROM apps
)
SELECT category, app, installs
FROM ranked
WHERE rn <= 3;
```
Why it's strong: demonstrates `PARTITION BY` + `ROW_NUMBER()` to solve a
classic "top-N per group" problem without a self-join or subquery-per-row.

**2. Each category's percentage contribution to total installs**
```sql
WITH category_installs AS (
    SELECT category, SUM(installs) AS cat_installs FROM apps GROUP BY category
)
SELECT category, cat_installs,
       ROUND(cat_installs * 100.0 / SUM(cat_installs) OVER (), 2) AS pct_of_total
FROM category_installs;
```
Why it's strong: uses a window function with an **empty** `OVER ()` clause
to compute a grand total alongside grouped rows — a technique many
candidates don't know.

**3. Apps that outperform their own category average (correlated comparison)**
```sql
WITH category_avg AS (
    SELECT category, AVG(installs) AS avg_cat_installs FROM apps GROUP BY category
)
SELECT a.app, a.category, a.installs, c.avg_cat_installs
FROM apps a
JOIN category_avg c ON a.category = c.category
WHERE a.installs > c.avg_cat_installs;
```
Why it's strong: shows understanding that "above average" is meaningless
without specifying above *what* average — comparing within-group rather
than against the whole table.

**4. Categories where paid apps beat free apps in average rating**
```sql
WITH type_rating AS (
    SELECT category, app_type, AVG(rating) AS avg_rating
    FROM apps WHERE rating IS NOT NULL
    GROUP BY category, app_type
)
SELECT p.category, p.avg_rating AS paid_avg, f.avg_rating AS free_avg
FROM type_rating p
JOIN type_rating f ON p.category = f.category AND f.app_type = 'Free'
WHERE p.app_type = 'Paid' AND p.avg_rating > f.avg_rating;
```
Why it's strong: a self-join on a CTE to compare two subgroups side by
side — a pattern that comes up constantly in real analytics work (cohort
comparisons, A/B-style breakdowns).

**5. Rank price buckets by average installs**
```sql
SELECT price_bucket, ROUND(AVG(installs),0) AS avg_installs,
       RANK() OVER (ORDER BY AVG(installs) DESC) AS install_rank
FROM apps
GROUP BY price_bucket;
```
Why it's strong: directly ties a technical query to a pricing-strategy
business question — good for a data storytelling narrative.

## 2. Strongest Python Techniques to Discuss

1. **Generic corruption detection instead of hardcoding a row index.**
   The shifted-row bug was found by testing `pd.to_numeric(df['Category'])`
   for validity, not by hardcoding "row 10472." This means the fix survives
   if the dataset order changes — a materially more robust approach.

2. **Log transforms for heavily skewed count data.**
   `installs` and `reviews` span 0 to 1 billion. Using `np.log1p()` (log(1+x),
   safe for zero values) before plotting or correlating avoids a chart that's
   just a few dots crushed against the y-axis.

3. **Choosing the right statistical test for the data's shape.**
   Rating comparisons used a Welch's t-test (unequal variances assumed);
   installs comparisons used a Mann-Whitney U test instead of a t-test,
   because installs are extremely right-skewed and violate the normality
   assumption a t-test relies on.

4. **`pd.cut()` for reproducible, labeled bucketing** (install_bucket,
   rating_bucket, price_bucket) instead of manual `if/elif` chains — cleaner,
   vectorized, and consistent between the cleaning script and any downstream
   analysis that re-buckets on the fly.

5. **Deriving `Type` from `Price` rather than dropping rows with missing
   Type.** Since `Price` is a strictly more reliable signal (Price > 0 implies
   Paid), this recovers rows that would otherwise be lost, instead of
   discarding usable data.

## 3. 30-Second Explanation (Elevator Pitch)

"I built an end-to-end analytics project on ~10,000 Google Play Store apps
using Python and MySQL. I cleaned a genuinely messy dataset — fixing a
column-shift bug, parsing string-formatted installs and prices, handling
missing sizes — then loaded it into MySQL and wrote both basic and advanced
SQL, including window functions and CTEs, to answer real business
questions. I also ran correlation and hypothesis tests to check which
patterns were statistically real. The headline finding: star rating barely
predicts installs, but review volume does, and free apps get roughly 100x
more installs than paid ones — which directly shapes pricing and go-to-
market recommendations."

## 4. 2-Minute Explanation (Detailed Walkthrough)

"The project started with a raw scrape of the Google Play Store — about
10,800 apps with 13 columns. It was genuinely dirty: installs were stored
as strings like '10,000+', prices as '$4.99', app sizes mixed megabytes and
kilobytes with a 'varies with device' placeholder, and there was even a
column-shift bug where one row's missing category value pushed every
subsequent field one column to the left. I wrote a cleaning pipeline in
Pandas that detects that kind of corruption generically — by checking
whether the Category field is unexpectedly numeric — rather than hardcoding
a row index, so it's robust to reordering.

After cleaning, I had about 9,700 valid rows across 33 categories. I loaded
that into a MySQL database with proper types and indexes, then wrote five
SQL scripts: schema setup, data-quality audits, basic aggregations,
advanced queries using CTEs and window functions like RANK and ROW_NUMBER,
and a final set of business-framed queries — like which categories combine
high demand with low competition.

On the statistics side, I ran Pearson and Spearman correlations between
rating, reviews, price, size, and installs, and used the right test for
each comparison — a Welch's t-test for ratings since that's roughly
continuous, but a Mann-Whitney U test for installs, because installs are
extremely skewed and a t-test's normality assumption doesn't hold.

The most interesting finding was that star rating is a weak predictor of
installs — correlation of about 0.04, statistically almost nothing — while
review count is strongly correlated, around 0.63 Pearson and 0.97 Spearman.
That reframes how a team should think about 'quality' metrics: rating tells
you about satisfaction, not about reach. I also found that free apps
average about 100 times more installs than paid apps, and that pricing
between $5 and $10 actually outperforms pricing under $1 — cheap apps don't
necessarily install better, possibly because rock-bottom pricing signals
low quality. All of that fed into a set of concrete recommendations: default
to free/freemium for mass-market reach, avoid impulse-tier pricing if you do
charge, and treat review count as a stronger popularity signal than rating."

## 5. 10 Likely Interview Questions and Strong Answers

**Q1: Why did you use MySQL instead of just doing everything in Pandas?**
A: Pandas is great for exploration, but SQL demonstrates a different and
equally important skill set — schema design, indexing, and set-based
thinking. It's also how most real analytics questions get asked against
production data warehouses, so showing I can express the same business
question in SQL (with window functions, not just SELECT *) is a meaningful
signal.

**Q2: How did you handle missing ratings — why not just drop them?**
A: About 1,463 of 9,659 apps (~15%) had no rating. Dropping them would bias
every rating-based analysis toward established apps and away from newer
ones. Instead, I kept them in the dataset and excluded them only from
rating-specific aggregations (using `WHERE rating IS NOT NULL` or
`.dropna()` scoped to that calculation), so they still contribute to
install, review, and category-level analysis.

**Q3: Walk me through the column-shift bug you found.**
A: One row was missing its Category value entirely, which shifted every
downstream field one position to the left — so what should have been the
Rating (1.9) landed in the Category column instead. I detected this
generically by testing whether `Category` was coercible to a number (a
real category name never is), then shifted the row's values back into the
correct columns. Since the original Category value was unrecoverable, I
ultimately dropped that single row rather than guess at it.

**Q4: Your rating-vs-installs correlation is very low. Doesn't that mean
rating doesn't matter?**
A: It means rating alone is a weak *linear* predictor of installs across
the whole dataset — not that quality is irrelevant. Apps in the 4-4.5
bucket actually out-install the 4.5-5 bucket, which suggests confounding
factors (marketing spend, app age, category) dominate. I was careful in the
writeup to say correlation doesn't imply causation, and that this finding
is about predictive strength, not about whether users value quality.

**Q5: Why Mann-Whitney U instead of a t-test for comparing installs?**
A: Installs range from 0 to 1 billion and are heavily right-skewed — a
handful of apps like Facebook and Instagram dominate the distribution. A
t-test assumes roughly normal data; that assumption is badly violated here.
Mann-Whitney U is a non-parametric test that compares distributions via
rank rather than raw values, so it's appropriate for this kind of skew.

**Q6: How would you scale this if the dataset were 10 million rows instead
of 10,000?**
A: I'd move heavier aggregations into SQL rather than Pandas (the database
can push down filters and use indexes far more efficiently), read data in
chunks rather than loading the full CSV into memory, and likely batch the
MySQL load with `LOAD DATA INFILE` instead of row-by-row `INSERT`s, which
is what I used here since 9,659 rows didn't require it.

**Q7: What's a limitation of this analysis you'd flag to a stakeholder?**
A: The dataset is a single scrape from one point in time, so it can't show
trends — I can say COMMUNICATION apps have high average installs today, but
not whether that's growing or shrinking. I'd also flag the duplicate
"I am Rich" style novelty apps as intentional outliers that shouldn't be
read as representative premium pricing behavior.

**Q8: How did you decide on your price buckets?**
A: I used buckets that map to how users actually perceive app pricing
tiers in practice — free, under $1 (impulse), $1-5 (typical premium app),
$5-10 (mid-tier), and $10+ (premium/professional) — rather than equal-width
bins, since pricing psychology isn't linear.

**Q9: What would you build next if you had more time?**
A: I'd bring in the companion `googleplaystore_user_reviews.csv` dataset (
sentiment-labeled user reviews) to connect review sentiment, not just
volume, to installs and ratings. I'd also look at genre-level detail (the
`Genres` column has finer granularity than `Category`) for more targeted
positioning recommendations.

**Q10: How do you know your cleaning didn't introduce bias?**
A: I validated post-cleaning: confirmed rating stayed within [0,5], installs
had zero negative values, and category count matched expectations (33,
consistent with the known dataset). I also chose the "most reviews wins"
tiebreaker for duplicate app names as a defensible, documented rule rather
than an arbitrary one, and I explain that rule directly in the README so
it's auditable rather than silent.
