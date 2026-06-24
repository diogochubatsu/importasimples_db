-- ImportaSimples Database Schema
-- Category architecture for all agents

-- ============================================================
-- silver_categories: Single source of truth for categories
-- ============================================================
CREATE TABLE IF NOT EXISTS silver_categories (
    id SERIAL PRIMARY KEY,
    l1 VARCHAR(100),           -- Top-level (Audio, Moda, Eletrônicos, etc.)
    l2 VARCHAR(100),           -- Sub-category (nullable)
    l3 VARCHAR(100),           -- Sub-sub-category (nullable)
    l4 VARCHAR(100),           -- Sub-sub-sub-category (nullable)
    icon VARCHAR(10),          -- Emoji for UI
    ncm_codes INTEGER[],       -- NCM tax codes (for import)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sc_l1 ON silver_categories(l1);
CREATE INDEX IF NOT EXISTS idx_sc_l2 ON silver_categories(l2);
CREATE INDEX IF NOT EXISTS idx_sc_l3 ON silver_categories(l3);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sc_unique ON silver_categories(l1, l2, l3);

-- ============================================================
-- silver_categories_map: Maps platform IDs → silver_categories
-- ============================================================
CREATE TABLE IF NOT EXISTS silver_categories_map (
    id SERIAL PRIMARY KEY,
    silver_category_id INTEGER NOT NULL REFERENCES silver_categories(id),
    platform VARCHAR(30) NOT NULL,       -- '1688', 'ml', 'amazon', 'alibaba', 'dhgate'
    platform_l1_id VARCHAR(50),          -- Marketplace's L1 category ID
    platform_l2_id VARCHAR(50),          -- Marketplace's L2 category ID (nullable)
    platform_l3_id VARCHAR(50),          -- Marketplace's L3 category ID (nullable)
    platform_category_name VARCHAR(200), -- Original name (Chinese/English)
    confidence DECIMAL(3,2) DEFAULT 0.8, -- How reliable this mapping is (0-1)
    verified BOOLEAN DEFAULT FALSE,      -- Manually verified?
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(platform, platform_l1_id, platform_l2_id, platform_l3_id)
);

CREATE INDEX IF NOT EXISTS idx_scm_platform ON silver_categories_map(platform);
CREATE INDEX IF NOT EXISTS idx_scm_l1 ON silver_categories_map(platform_l1_id);
CREATE INDEX IF NOT EXISTS idx_scm_silver_id ON silver_categories_map(silver_category_id);

-- ============================================================
-- bronze_products: Products with category FK
-- ============================================================
-- Add silver_category_id column to existing bronze_products table
ALTER TABLE bronze_products ADD COLUMN IF NOT EXISTS silver_category_id INTEGER REFERENCES silver_categories(id);
CREATE INDEX IF NOT EXISTS idx_bp_silver_cat ON bronze_products(silver_category_id);
