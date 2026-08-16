-- ============================================================
-- 05_business_insights.sql
-- Business-framed queries that directly answer the strategic
-- questions in the README's "Key Findings" and "Recommendations"
-- sections.
-- ============================================================

USE google_play_analytics;

-- Q1. Which categories combine high demand (installs) AND high supply pressure (app count)?
-- These are "oversaturated" categories - hard to break into.
SELECT category,
       COUNT(*) AS app_count,
       ROUND(AVG(installs), 0) AS avg_installs,
       SUM(installs) AS total_installs
FROM apps
GROUP BY category
ORDER BY app_count DESC
LIMIT 10;

-- Q2. Which content-rating segments perform best on average installs and rating?
SELECT content_rating,
       COUNT(*) AS app_count,
       ROUND(AVG(rating), 2) AS avg_rating,
       ROUND(AVG(installs), 0) AS avg_installs
FROM apps
GROUP BY content_rating
ORDER BY avg_installs DESC;

-- Q3. Does app size correlate with better installs? (bucketed manually via CASE)
SELECT
    CASE
        WHEN size_mb IS NULL THEN 'Varies with device'
        WHEN size_mb < 10 THEN '<10MB'
        WHEN size_mb < 30 THEN '10-30MB'
        WHEN size_mb < 60 THEN '30-60MB'
        WHEN size_mb < 100 THEN '60-100MB'
        ELSE '100MB+'
    END AS size_bucket,
    COUNT(*) AS app_count,
    ROUND(AVG(installs), 0) AS avg_installs,
    ROUND(AVG(rating), 2) AS avg_rating
FROM apps
GROUP BY size_bucket
ORDER BY avg_installs DESC;

-- Q4. Freshness check: do apps updated more recently have higher ratings?
SELECT updated_year,
       COUNT(*) AS app_count,
       ROUND(AVG(rating), 2) AS avg_rating,
       ROUND(AVG(installs), 0) AS avg_installs
FROM apps
WHERE updated_year IS NOT NULL
GROUP BY updated_year
ORDER BY updated_year DESC;

-- Q5. Monetisation potential score per category:
-- combines paid-app share and average paid price into a single comparative view.
SELECT category,
       COUNT(*) AS total_apps,
       SUM(CASE WHEN app_type = 'Paid' THEN 1 ELSE 0 END) AS paid_apps,
       ROUND(SUM(CASE WHEN app_type = 'Paid' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_paid,
       ROUND(AVG(CASE WHEN app_type = 'Paid' THEN price END), 2) AS avg_paid_price
FROM apps
GROUP BY category
HAVING paid_apps >= 10
ORDER BY pct_paid DESC;

-- Q6. "Sweet spot" apps: high rating (>=4.5) AND high installs (>=1M) AND free
-- These represent the benchmark for what a successful free app looks like.
SELECT app, category, rating, installs, reviews
FROM apps
WHERE rating >= 4.5 AND installs >= 1000000 AND app_type = 'Free'
ORDER BY installs DESC
LIMIT 20;

-- Q7. Underrated opportunity apps: high review_to_install_ratio (engaged users)
-- but relatively low absolute installs (<1M) - may signal strong product-market
-- fit that hasn't scaled yet.
SELECT app, category, installs, reviews, review_to_install_ratio, rating
FROM apps
WHERE installs BETWEEN 10000 AND 1000000
  AND review_to_install_ratio IS NOT NULL
  AND rating >= 4.3
ORDER BY review_to_install_ratio DESC
LIMIT 15;
