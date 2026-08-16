-- ============================================================
-- 04_advanced_analysis.sql
-- Interview-ready analytical queries using CTEs, window functions,
-- CASE WHEN, and subqueries. Each query answers a specific business
-- question, stated in the comment above it.
-- ============================================================

USE google_play_analytics;

-- 1. Rank categories by total installs (demand ranking)
SELECT category,
       SUM(installs) AS total_installs,
       RANK() OVER (ORDER BY SUM(installs) DESC) AS install_rank
FROM apps
GROUP BY category;

-- 2. Rank categories by average rating (quality ranking, min 20 apps to avoid noise)
SELECT category,
       ROUND(AVG(rating), 2) AS avg_rating,
       COUNT(*) AS app_count,
       RANK() OVER (ORDER BY AVG(rating) DESC) AS rating_rank
FROM apps
WHERE rating IS NOT NULL
GROUP BY category
HAVING COUNT(*) >= 20;

-- 3. Top 3 apps in each category by installs
-- Business use: identify category leaders / benchmark competitors.
WITH ranked AS (
    SELECT app, category, installs,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY installs DESC) AS rn
    FROM apps
)
SELECT category, app, installs
FROM ranked
WHERE rn <= 3
ORDER BY category, installs DESC;

-- 4. Top 3 apps in each category by reviews
WITH ranked AS (
    SELECT app, category, reviews,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY reviews DESC) AS rn
    FROM apps
)
SELECT category, app, reviews
FROM ranked
WHERE rn <= 3
ORDER BY category, reviews DESC;

-- 5. Each category's percentage contribution to total installs
-- Business use: prioritisation - where is user demand concentrated?
WITH category_installs AS (
    SELECT category, SUM(installs) AS cat_installs
    FROM apps
    GROUP BY category
)
SELECT category,
       cat_installs,
       ROUND(cat_installs * 100.0 / SUM(cat_installs) OVER (), 2) AS pct_of_total_installs
FROM category_installs
ORDER BY pct_of_total_installs DESC;

-- 6. Average installs for free vs paid apps
-- Business use: quantify the install-volume cost of charging upfront.
SELECT app_type,
       ROUND(AVG(installs), 0) AS avg_installs,
       ROUND(AVG(rating), 2) AS avg_rating
FROM apps
GROUP BY app_type;

-- 7. Apps whose rating is above the overall average
-- Business use: benchmark set for "what a good app looks like."
SELECT app, category, rating
FROM apps
WHERE rating > (SELECT AVG(rating) FROM apps WHERE rating IS NOT NULL)
ORDER BY rating DESC
LIMIT 20;

-- 8. Apps whose installs are above their OWN category average
-- Business use: find over-performers relative to category norms, not the whole store.
WITH category_avg AS (
    SELECT category, AVG(installs) AS avg_cat_installs
    FROM apps
    GROUP BY category
)
SELECT a.app, a.category, a.installs, ROUND(c.avg_cat_installs, 0) AS category_avg_installs
FROM apps a
JOIN category_avg c ON a.category = c.category
WHERE a.installs > c.avg_cat_installs
ORDER BY a.installs DESC
LIMIT 20;

-- 9. Expensive apps ($10+) that still have high installs (>= 100K)
-- Business use: proof that premium pricing CAN coexist with scale, and which niches allow it.
SELECT app, category, price, installs
FROM apps
WHERE price >= 10 AND installs >= 100000
ORDER BY installs DESC;

-- 10. Categories where paid apps outperform free apps in average rating
-- Business use: signals where users reward paying for quality/ad-free experience.
WITH type_rating AS (
    SELECT category, app_type, AVG(rating) AS avg_rating
    FROM apps
    WHERE rating IS NOT NULL
    GROUP BY category, app_type
)
SELECT p.category,
       p.avg_rating AS paid_avg_rating,
       f.avg_rating AS free_avg_rating,
       ROUND(p.avg_rating - f.avg_rating, 2) AS rating_gap
FROM type_rating p
JOIN type_rating f ON p.category = f.category AND f.app_type = 'Free'
WHERE p.app_type = 'Paid'
  AND p.avg_rating > f.avg_rating
ORDER BY rating_gap DESC;

-- 11. Categories with high installs but low average ratings (< 4.0)
-- Business use: flags categories where user demand outpaces perceived quality -
-- an opportunity for a well-built new entrant.
SELECT category,
       ROUND(AVG(rating), 2) AS avg_rating,
       ROUND(AVG(installs), 0) AS avg_installs
FROM apps
WHERE rating IS NOT NULL
GROUP BY category
HAVING AVG(rating) < 4.0
ORDER BY avg_installs DESC;

-- 12. Categories with low competition (few apps) but high average installs
-- Business use: "blue ocean" categories - high demand, low supply.
SELECT category,
       COUNT(*) AS app_count,
       ROUND(AVG(installs), 0) AS avg_installs
FROM apps
GROUP BY category
HAVING COUNT(*) < 200
ORDER BY avg_installs DESC
LIMIT 10;

-- 13. Apps with high installs (top 25% percentile-like threshold) but
-- relatively low review counts, i.e. weak review_to_install_ratio
-- Business use: apps that are installed widely but not actively reviewed -
-- possible engagement gap or install-fraud risk to investigate.
SELECT app, category, installs, reviews, review_to_install_ratio
FROM apps
WHERE installs >= 1000000
  AND review_to_install_ratio IS NOT NULL
ORDER BY review_to_install_ratio ASC
LIMIT 15;

-- 14. Category-level review-to-install ratio (engagement proxy)
SELECT category,
       ROUND(AVG(review_to_install_ratio), 4) AS avg_review_to_install_ratio
FROM apps
WHERE review_to_install_ratio IS NOT NULL
GROUP BY category
ORDER BY avg_review_to_install_ratio DESC
LIMIT 10;

-- 15. Rank price buckets by average installs
-- Business use: directly informs pricing strategy.
SELECT price_bucket,
       ROUND(AVG(installs), 0) AS avg_installs,
       COUNT(*) AS app_count,
       RANK() OVER (ORDER BY AVG(installs) DESC) AS install_rank
FROM apps
GROUP BY price_bucket;
