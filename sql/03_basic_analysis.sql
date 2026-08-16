-- ============================================================
-- 03_basic_analysis.sql
-- Foundational descriptive queries every stakeholder would ask first.
-- ============================================================

USE google_play_analytics;

-- 1. Total number of apps
SELECT COUNT(*) AS total_apps FROM apps;

-- 2. Number of unique categories
SELECT COUNT(DISTINCT category) AS unique_categories FROM apps;

-- 3. Average rating across all rated apps
SELECT ROUND(AVG(rating), 2) AS avg_rating FROM apps WHERE rating IS NOT NULL;

-- 4. Average number of reviews
SELECT ROUND(AVG(reviews), 0) AS avg_reviews FROM apps;

-- 5. Total installs across the store
SELECT SUM(installs) AS total_installs FROM apps;

-- 6. Free vs paid app count
SELECT app_type, COUNT(*) AS app_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM apps), 2) AS pct_of_total
FROM apps
GROUP BY app_type;

-- 7. Average price of paid apps only
SELECT ROUND(AVG(price), 2) AS avg_paid_price
FROM apps
WHERE app_type = 'Paid';

-- 8. Top 10 categories by app count
SELECT category, COUNT(*) AS app_count
FROM apps
GROUP BY category
ORDER BY app_count DESC
LIMIT 10;

-- 9. Top 10 apps by installs
SELECT app, category, installs
FROM apps
ORDER BY installs DESC
LIMIT 10;

-- 10. Top 10 apps by reviews
SELECT app, category, reviews
FROM apps
ORDER BY reviews DESC
LIMIT 10;

-- 11. Average rating by category
SELECT category, ROUND(AVG(rating), 2) AS avg_rating, COUNT(*) AS app_count
FROM apps
WHERE rating IS NOT NULL
GROUP BY category
ORDER BY avg_rating DESC;

-- 12. Average installs by category
SELECT category, ROUND(AVG(installs), 0) AS avg_installs
FROM apps
GROUP BY category
ORDER BY avg_installs DESC;

-- 13. Total reviews by category
SELECT category, SUM(reviews) AS total_reviews
FROM apps
GROUP BY category
ORDER BY total_reviews DESC;

-- 14. Number of paid apps by category
SELECT category, COUNT(*) AS paid_app_count
FROM apps
WHERE app_type = 'Paid'
GROUP BY category
ORDER BY paid_app_count DESC;

-- 15. Average price by category (paid apps only, since free apps would dilute the average)
SELECT category, ROUND(AVG(price), 2) AS avg_price
FROM apps
WHERE app_type = 'Paid'
GROUP BY category
ORDER BY avg_price DESC;
