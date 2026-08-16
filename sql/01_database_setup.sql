-- ============================================================
-- 01_database_setup.sql
-- Creates the database and the core `apps` table used for all
-- downstream analysis. Column types are chosen deliberately:
--   - app_id is the surrogate primary key created during cleaning
--     (the raw dataset has no unique app identifier).
--   - installs/reviews use BIGINT because top apps exceed 1 billion.
--   - price/rating/size use DECIMAL/FLOAT for numeric accuracy.
-- ============================================================

DROP DATABASE IF EXISTS google_play_analytics;
CREATE DATABASE google_play_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE google_play_analytics;

DROP TABLE IF EXISTS apps;

CREATE TABLE apps (
    app_id                      INT PRIMARY KEY,
    app                         VARCHAR(255) NOT NULL,
    category                    VARCHAR(64)  NOT NULL,
    rating                      DECIMAL(3,2)     NULL,
    reviews                     BIGINT           NOT NULL DEFAULT 0,
    size_mb                     DECIMAL(10,3)    NULL,
    installs                    BIGINT           NOT NULL DEFAULT 0,
    app_type                    VARCHAR(10)      NOT NULL,       -- Free / Paid
    price                       DECIMAL(10,2)    NOT NULL DEFAULT 0,
    content_rating              VARCHAR(32)      NOT NULL,
    genres                      VARCHAR(128)     NULL,
    last_updated                DATE             NULL,
    current_version             VARCHAR(64)      NULL,
    android_version             VARCHAR(64)      NULL,
    is_free                     TINYINT(1)       NOT NULL DEFAULT 1,
    log_installs                DECIMAL(10,4)    NULL,
    log_reviews                 DECIMAL(10,4)    NULL,
    review_to_install_ratio     DECIMAL(10,6)    NULL,
    updated_year                SMALLINT         NULL,
    updated_month               TINYINT          NULL,
    install_bucket              VARCHAR(16)      NULL,
    rating_bucket                VARCHAR(16)     NULL,
    price_bucket                VARCHAR(16)      NULL,

    INDEX idx_category (category),
    INDEX idx_installs (installs),
    INDEX idx_rating (rating),
    INDEX idx_type (app_type),
    INDEX idx_price_bucket (price_bucket)
) ENGINE=InnoDB;
