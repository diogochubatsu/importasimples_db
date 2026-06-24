#!/usr/bin/env python3
"""
Migrate ArbitLens (arbt.ly) products to ImportaSimples bronze_products.

Usage:
  python3 migrate_to_importasimples.py --dry-run    # Preview
  python3 migrate_to_importasimples.py --execute    # Run migration
  python3 migrate_to_importasimples.py --verify     # Check counts
"""
import os
import sys
import json
import psycopg2
import argparse

# ArbitLens database (source)
ARBITLENS_DB = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'arbtbr',
    'user': 'hermes1688'
}

# ImportaSimples database (destination)
DESTINATION_DB = {
    'host': '34.170.210.220',
    'port': 5432,
    'dbname': 'importasimples_products',
    'user': 'importasimples',
    'password': 'R{[{f<VajbC{<kvU',
    'sslmode': 'require'
}

# Source identifier — MUST be 'arbt.ly', NOT 'arbitlens_brasil'
SOURCE_VALUE = 'arbt.ly'
SCRIPT_NAME = 'migrate_to_importasimples.py'

# Platform mapping
PLATFORM_MAP = {
    'amazon_br': 'amazon_br',
    'amazon_us': 'amazon_usa',
    'ml': 'mercadolivre'
}


def get_arbitlens_conn():
    return psycopg2.connect(**ARBITLENS_DB)


def get_destination_conn():
    return psycopg2.connect(**DESTINATION_DB)


def map_product(row):
    """Map ArbitLens product to bronze_products format."""
    (id, platform, platform_id, title, price, currency, url, image_urls,
     sales_30d, review_count, review_avg, category_l1, category_l2, category_l3,
     image_hash) = row
    
    source_id = f"{platform}:{platform_id}"
    marketplace = PLATFORM_MAP.get(platform, platform)
    
    imgs = image_urls or []
    levels = sum(1 for x in [category_l1, category_l2, category_l3] if x)
    cat_raw = ' > '.join(x for x in [category_l1, category_l2, category_l3] if x)
    
    return {
        'source': SOURCE_VALUE,
        'source_id': source_id,
        'marketplace': marketplace,
        'title': title,
        'image_url': imgs[0] if imgs else None,
        'image_urls': imgs,
        'image_count': len(imgs),
        'price': price,
        'currency': currency or 'BRL',
        'price_brl': price,
        'url': url,
        'product_url': url,
        'category_raw': cat_raw,
        'category_level': levels,
        'category_l1': category_l1 or '',
        'category_l2': category_l2 or '',
        'category_l3': category_l3 or '',
        'sales_30d': sales_30d or 0,
        'review_count': review_count or 0,
        'review_avg': review_avg,
        'raw_data': json.dumps({'arbtly_id': id, 'image_hash': image_hash}),
        'script_name': SCRIPT_NAME
    }


UPSERT_SQL = """
    INSERT INTO bronze_products (
        source, source_id, marketplace, title,
        image_url, image_urls, image_count,
        price, currency, price_brl,
        url, product_url,
        category_raw, category_level, category_l1, category_l2, category_l3,
        sales_30d, review_count, review_avg,
        raw_data, script_name
    ) VALUES (
        %(source)s, %(source_id)s, %(marketplace)s, %(title)s,
        %(image_url)s, %(image_urls)s, %(image_count)s,
        %(price)s, %(currency)s, %(price_brl)s,
        %(url)s, %(product_url)s,
        %(category_raw)s, %(category_level)s, %(category_l1)s, %(category_l2)s, %(category_l3)s,
        %(sales_30d)s, %(review_count)s, %(review_avg)s,
        %(raw_data)s, %(script_name)s
    )
    ON CONFLICT (source, source_id) DO UPDATE SET
        title = EXCLUDED.title,
        image_url = EXCLUDED.image_url, image_urls = EXCLUDED.image_urls,
        image_count = EXCLUDED.image_count,
        price = EXCLUDED.price, currency = EXCLUDED.currency, price_brl = EXCLUDED.price_brl,
        category_raw = EXCLUDED.category_raw, category_level = EXCLUDED.category_level,
        category_l1 = EXCLUDED.category_l1, category_l2 = EXCLUDED.category_l2, category_l3 = EXCLUDED.category_l3,
        sales_30d = EXCLUDED.sales_30d, review_count = EXCLUDED.review_count, review_avg = EXCLUDED.review_avg,
        raw_data = EXCLUDED.raw_data, scraped_at = NOW()
    RETURNING (xmax = 0) AS is_new
"""


def migrate(dry_run=True):
    print(f"Connecting to source (arbtbr)...")
    src_conn = get_arbitlens_conn()
    src_cur = src_conn.cursor()
    
    print(f"Connecting to destination (ImportaSimples)...")
    dst_conn = get_destination_conn()
    dst_cur = dst_conn.cursor()
    
    # Count source products
    src_cur.execute("SELECT COUNT(*) FROM products WHERE is_active = TRUE")
    src_count = src_cur.fetchone()[0]
    print(f"Source products: {src_count}")
    
    # Count existing in destination
    dst_cur.execute("SELECT COUNT(*) FROM bronze_products WHERE source = %s", (SOURCE_VALUE,))
    dst_count = dst_cur.fetchone()[0]
    print(f"Existing in destination: {dst_count}")
    
    # Fetch all products
    src_cur.execute("""
        SELECT id, platform, platform_id, title, price, currency, url, image_urls,
               sales_30d, review_count, review_avg, category_l1, category_l2, category_l3,
               image_hash
        FROM products WHERE is_active = TRUE
    """)
    products = src_cur.fetchall()
    
    if dry_run:
        print(f"\n[DRY RUN] Would process {len(products)} products")
        # Show sample
        for p in products[:3]:
            mapped = map_product(p)
            print(f"  {mapped['source_id']}: {mapped['title'][:50]}...")
        return
    
    # Execute migration
    inserted = 0
    updated = 0
    errors = 0
    
    for i in range(0, len(products), 100):
        batch = products[i:i+100]
        try:
            for row in batch:
                try:
                    mapped = map_product(row)
                    dst_cur.execute(UPSERT_SQL, mapped)
                    result = dst_cur.fetchone()
                    if result and result[0]:
                        inserted += 1
                    else:
                        updated += 1
                except Exception as e:
                    errors += 1
                    print(f"  Error: {e}")
            dst_conn.commit()
            print(f"  Batch {i//100 + 1}: {len(batch)} products")
        except Exception as e:
            dst_conn.rollback()
            errors += len(batch)
            print(f"  Batch FAILED: {e}")
    
    src_conn.close()
    dst_conn.close()
    
    print(f"\nMigration complete:")
    print(f"  New: {inserted}")
    print(f"  Updated: {updated}")
    print(f"  Errors: {errors}")


def verify():
    print("Verifying migration...")
    dst_conn = get_destination_conn()
    dst_cur = dst_conn.cursor()
    
    dst_cur.execute("""
        SELECT COUNT(*) FROM bronze_products WHERE source = %s
    """, (SOURCE_VALUE,))
    total = dst_cur.fetchone()[0]
    print(f"  Total products: {total}")
    
    dst_cur.execute("""
        SELECT marketplace, COUNT(*) as cnt,
            COUNT(*) FILTER (WHERE silver_category_id IS NOT NULL) as has_silver
        FROM bronze_products WHERE source = %s
        GROUP BY marketplace ORDER BY marketplace
    """, (SOURCE_VALUE,))
    print("\n  By marketplace:")
    for r in dst_cur.fetchall():
        pct = (r[2]/r[1]*100) if r[1] > 0 else 0
        print(f"    {r[0]}: {r[1]} products, {pct:.0f}% silver")
    
    dst_conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate arbt.ly to ImportaSimples')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    
    if args.verify:
        verify()
    elif args.execute:
        migrate(dry_run=False)
    else:
        migrate(dry_run=True)
