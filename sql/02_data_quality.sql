-- ============================================================
-- 02_data_quality.sql
-- Data quality audit on the loaded `apps` table. Even though the
-- table was populated from an already-cleaned CSV, a real analyst
-- re-validates quality inside the database rather than trusting
-- the pipeline blindly.
-- ============================================================

USE google_play_analytics;

-- 1. Apps with NULL rating (never rated, or rating was invalid/out of range)
SELECT COUNT(*) AS apps_with_null_rating
FROM apps
WHERE rating IS NULL;

-- 2. Duplicate app names (should be zero post-cleaning; dedup happened in Python)
SELECT app, COUNT(*) AS occurrences
FROM apps
GROUP BY app
HAVING COUNT(*) > 1;

-- 3. Invalid prices (negative, or absurd outliers worth flagging)
SELECT app, price
FROM apps
WHERE price < 0
   OR price > 350;   -- flags the known "I Am Rich" style $300+ novelty apps

-- 4. Invalid installs (should never be negative)
SELECT COUNT(*) AS invalid_install_rows
FROM apps
WHERE installs < 0;

-- 5. Categories with suspicious values (very low row counts may be noise)
SELECT category, COUNT(*) AS app_count
FROM apps
GROUP BY category
HAVING COUNT(*) < 5
ORDER BY app_count;

-- 6. Apps with zero reviews (freshly listed, or scraping gaps)
SELECT COUNT(*) AS apps_with_zero_reviews
FROM apps
WHERE reviews = 0;

-- 7. Apps with extremely high review counts (top of the distribution)
SELECT app, category, reviews
FROM apps
ORDER BY reviews DESC
LIMIT 10;

-- 8. Apps with extreme prices (top 10 most expensive)
SELECT app, category, price
FROM apps
WHERE app_type = 'Paid'
ORDER BY price DESC
LIMIT 10;

-- 9. Missing size values (size_mb NULL means "Varies with device" in source data)
SELECT COUNT(*) AS apps_with_missing_size
FROM apps
WHERE size_mb IS NULL;

-- 10. Rating sanity check - confirm all ratings fall within [0, 5]
SELECT MIN(rating) AS min_rating, MAX(rating) AS max_rating
FROM apps
WHERE rating IS NOT NULL;
