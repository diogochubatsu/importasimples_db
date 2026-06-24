#!/usr/bin/env python3
"""
Migrate ArbitLens products to ImportaSimples bronze_products table.

Usage:
  python3 migrate_to_importasimples.py --dry-run    # Preview migration
  python3 migrate_to_importasimples.py --execute    # Run migration
"""
import os
import sys
import json
import psycopg2
import argparse

# ArbitLens database (source)
ARBITLENS_DB = {
    'host': '10.30.96.3',
    'port': 5432,
    'dbname': 'intel_data',
    'user': 'hermes1688',
    'password': 'Lndgcp@#12'
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

def get_arbitlens_conn():
    return psycopg2.connect(**ARBITLENS_DB)

def get_destination_conn():
    return psycopg2.connect(**DESTINATION_DB)

def map_product(row):
    """Map ArbitLens product to bronze_products format."""
    (id, platform, platform_id, title, price, currency, url, image_urls,
     supplier_name, moq, sales_30d, review_count, category, category_n2,
     category_n3, category_n4, category_path, title_cn, image_embedding) = row
    
    # Format source_id
    source_id = f"{platform}:{platform_id}"
    
    # Map category levels
    category_l1 = category or ''
    category_l2 = category_n2.split('.')[-1] if category_n2 else ''
    category_l3 = category_n3.split('.')[-1] if category_n3 else ''
    category_l4 = category_n4.split('.')[-1] if category_n4 else ''
    
    # Store embedding in raw_data
    raw_data = {}
    if image_embedding:
        try:
            import struct
            if isinstance(image_embedding, memoryview):
                image_embedding = bytes(image_embedding)
            count = len(image_embedding) // 4
            embedding_list = list(struct.unpack(f'{count}f', image_embedding[:count * 4]))
            raw_data['image_embedding'] = embedding_list
        except:
            pass
    
    return {
        'source': 'arbitlens',
        'source_id': source_id,
        'marketplace': platform,
        'title': title,
        'title_cn': title_cn,
        'image_url': image_urls[0] if image_urls else None,
        'image_urls': image_urls,
        'image_count': len(image_urls) if image_urls else 0,
        'price': price,
        'currency': currency or 'BRL',
        'price_cny': None,  # Don't convert
        'price_brl': price,  # Same as price (already BRL)
        'url': url,
        'product_url': url,
        'category_raw': category_path or category or '',
        'category_level': 3 if category_n3 else (2 if category_n2 else 1),
        'category_l1': category_l1,
        'category_l2': category_l2,
        'category_l3': category_l3,
        'category_l4': category_l4,
        'supplier_name': supplier_name,
        'sales_30d': sales_30d,
        'monthly_sales': sales_30d,
        'review_count': review_count,
        'moq': moq,
        'raw_data': json.dumps(raw_data),
        'script_name': 'classify_products.py'
    }

def migrate(dry_run=True):
    """Execute migration."""
    print("Connecting to source database...")
    src_conn = get_arbitlens_conn()
    src_cur = src_conn.cursor()
    
    print("Connecting to destination database...")
    dst_conn = get_destination_conn()
    dst_cur = dst_conn.cursor()
    
    # Get all active products
    src_cur.execute("""
        SELECT id, platform, platform_id, title, price, currency, url, 
               image_urls, supplier_name, moq, sales_30d, review_count,
               category, category_n2, category_n3, category_n4, category_path,
               title_cn, image_embedding
        FROM arbitlens_products 
        WHERE is_active = true
        ORDER BY id
    """)
    
    products = src_cur.fetchall()
    print(f"Found {len(products)} products to migrate")
    
    if dry_run:
        print("\n[DRY RUN] Would migrate these products:")
        for i, row in enumerate(products[:5]):
            mapped = map_product(row)
            print(f"  {i+1}. {mapped['source_id'][:40]}... | {mapped['category_l1']} | {mapped['price_brl']}")
        print(f"  ... and {len(products) - 5} more")
        src_conn.close()
        dst_conn.close()
        return
    
    # UPSERT SQL
    upsert_sql = """
        INSERT INTO bronze_products (
            source, source_id, marketplace, title, title_cn,
            image_url, image_urls, image_count,
            price, currency, price_cny, price_brl,
            url, product_url,
            category_raw, category_level, category_l1, category_l2, category_l3, category_l4,
            supplier_name, sales_30d, monthly_sales, review_count, moq,
            raw_data, script_name
        ) VALUES (
            %(source)s, %(source_id)s, %(marketplace)s, %(title)s, %(title_cn)s,
            %(image_url)s, %(image_urls)s, %(image_count)s,
            %(price)s, %(currency)s, %(price_cny)s, %(price_brl)s,
            %(url)s, %(product_url)s,
            %(category_raw)s, %(category_level)s, %(category_l1)s, %(category_l2)s, %(category_l3)s, %(category_l4)s,
            %(supplier_name)s, %(sales_30d)s, %(monthly_sales)s, %(review_count)s, %(moq)s,
            %(raw_data)s::jsonb, %(script_name)s
        )
        ON CONFLICT (source, source_id) DO UPDATE SET
            title = EXCLUDED.title,
            title_cn = EXCLUDED.title_cn,
            image_url = EXCLUDED.image_url,
            image_urls = EXCLUDED.image_urls,
            price = EXCLUDED.price,
            currency = EXCLUDED.currency,
            price_brl = EXCLUDED.price_brl,
            category_raw = EXCLUDED.category_raw,
            category_level = EXCLUDED.category_level,
            category_l1 = EXCLUDED.category_l1,
            category_l2 = EXCLUDED.category_l2,
            category_l3 = EXCLUDED.category_l3,
            category_l4 = EXCLUDED.category_l4,
            supplier_name = EXCLUDED.supplier_name,
            sales_30d = EXCLUDED.sales_30d,
            review_count = EXCLUDED.review_count,
            raw_data = EXCLUDED.raw_data,
            scraped_at = NOW(),
            script_name = EXCLUDED.script_name
    """
    
    inserted = 0
    updated = 0
    errors = 0
    
    # Process in batches of 100
    for i in range(0, len(products), 100):
        batch = products[i:i+100]
        try:
            dst_cur.execute("BEGIN")
            for row in batch:
                try:
                    mapped = map_product(row)
                    dst_cur.execute(upsert_sql, mapped)
                    inserted += 1
                except Exception as e:
                    errors += 1
                    print(f"  Error on row: {e}")
            dst_cur.execute("COMMIT")
            print(f"  Batch {i//100 + 1}: processed {len(batch)} products")
        except Exception as e:
            dst_cur.execute("ROLLBACK")
            print(f"  Batch {i//100 + 1} FAILED: {e}")
            errors += len(batch)
    
    src_conn.close()
    dst_conn.close()
    
    print(f"\nMigration complete:")
    print(f"  Inserted/Updated: {inserted}")
    print(f"  Errors: {errors}")

def verify():
    """Verify migration."""
    print("Verifying migration...")
    dst_conn = get_destination_conn()
    dst_cur = dst_conn.cursor()
    
    # Count by source
    dst_cur.execute("SELECT source, COUNT(*) FROM bronze_products WHERE source = 'arbitlens' GROUP BY source")
    for source, count in dst_cur.fetchall():
        print(f"  {source}: {count} products")
    
    # Check nulls in required fields
    dst_cur.execute("""
        SELECT COUNT(*) FROM bronze_products 
        WHERE source = 'arbitlens' AND (title IS NULL OR source_id IS NULL)
    """)
    nulls = dst_cur.fetchone()[0]
    print(f"  Nulls in required fields: {nulls}")
    
    # Sample products
    dst_cur.execute("""
        SELECT source_id, marketplace, title, price_brl, category_l1
        FROM bronze_products 
        WHERE source = 'arbitlens'
        ORDER BY scraped_at DESC
        LIMIT 5
    """)
    print("\n  Recent products:")
    for source_id, marketplace, title, price, cat in dst_cur.fetchall():
        print(f"    {source_id[:30]}... | {marketplace} | {cat} | R${price}")
    
    dst_conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate to ImportaSimples')
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
