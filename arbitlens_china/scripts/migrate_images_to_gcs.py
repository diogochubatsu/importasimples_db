#!/usr/bin/env python3
"""
Migrate images from source URLs to GCP Cloud Storage bucket.

Usage:
  python3 migrate_images_to_gcs.py --dry-run           # Preview
  python3 migrate_images_to_gcs.py --execute           # Run migration
  python3 migrate_images_to_gcs.py --execute --limit 100  # Process 100 images
  python3 migrate_images_to_gcs.py --verify            # Check results
"""
import os
import sys
import json
import subprocess
import argparse
import time

BUCKET = 'importasimples-intel-images'
SOURCE = 'arbitlens_china'
LOCAL_DB = 'postgresql://hermes1688:Lndgcp%40%2312@10.30.96.3:5432/intel_data'
REMOTE_DB = {
    'host': '34.170.210.220', 'port': 5432,
    'dbname': 'importasimples_products',
    'user': 'importasimples', 'password': 'R{[{f<VajbC{<kvU',
    'sslmode': 'require'
}


def upload_image(source, marketplace, source_id, img_index, image_url):
    """Download image from source and upload to GCS. Returns public URL or None."""
    try:
        result = subprocess.run(
            ['curl', '-sL', '-o', '/tmp/temp_img.jpg', '--max-time', '10',
             '-H', 'User-Agent: Mozilla/5.0', image_url],
            capture_output=True, timeout=15
        )
        if result.returncode != 0 or not os.path.exists('/tmp/temp_img.jpg'):
            return None
        if os.path.getsize('/tmp/temp_img.jpg') < 100:
            os.remove('/tmp/temp_img.jpg')
            return None
    except Exception:
        return None

    gcs_path = f'{source}/{marketplace}/{source_id}/img-{img_index}.jpg'
    try:
        subprocess.run(
            ['gcloud', 'storage', 'cp', '/tmp/temp_img.jpg', f'gs://{BUCKET}/{gcs_path}'],
            capture_output=True, timeout=30, check=True
        )
        os.remove('/tmp/temp_img.jpg')
        return f'https://storage.googleapis.com/{BUCKET}/{gcs_path}'
    except Exception:
        if os.path.exists('/tmp/temp_img.jpg'):
            os.remove('/tmp/temp_img.jpg')
        return None


def migrate_images(dry_run=True, limit=None):
    """Migrate images to GCS with resume support."""
    import psycopg2

    conn = psycopg2.connect(**REMOTE_DB)
    cur = conn.cursor()

    # Find products needing migration (have source URL, not yet GCS)
    query = f'''SELECT source, marketplace, source_id, image_url
        FROM bronze_products
        WHERE source = '{SOURCE}'
        AND image_url IS NOT NULL
        AND image_url NOT LIKE '%storage.googleapis.com%'
        ORDER BY source_id'''
    if limit:
        query += f' LIMIT {limit}'

    cur.execute(query)
    products = cur.fetchall()
    print(f'Found {len(products)} products to migrate images')

    if dry_run:
        for source, marketplace, source_id, image_url in products:
            print(f'  {marketplace}:{source_id[:40]}... → {image_url[:80]}...')
        conn.close()
        return

    uploaded = 0
    failed = 0
    failed_list = []
    start = time.time()

    for i, (source, marketplace, source_id, image_url) in enumerate(products):
        new_url = upload_image(source, marketplace, source_id, 0, image_url)
        if new_url:
            cur.execute('''UPDATE bronze_products
                SET image_url = %s
                WHERE source = %s AND source_id = %s''',
                (new_url, source, source_id))
            uploaded += 1
        else:
            failed += 1
            failed_list.append(f'{marketplace}:{source_id[:30]}')

        if (i + 1) % 50 == 0:
            conn.commit()
            elapsed = time.time() - start
            rate = (i + 1) / elapsed * 60
            print(f'  Progress: {i + 1}/{len(products)} ({uploaded} ok, {failed} failed) — {rate:.0f}/min')

    conn.commit()
    elapsed = time.time() - start
    print(f'\nDone: {uploaded} uploaded, {failed} failed in {elapsed:.0f}s')
    if failed_list:
        print(f'Failed items ({len(failed_list)}):')
        for f in failed_list[:20]:
            print(f'  {f}')
        if len(failed_list) > 20:
            print(f'  ... and {len(failed_list) - 20} more')
    conn.close()


def verify():
    """Check migration status."""
    import psycopg2

    conn = psycopg2.connect(**REMOTE_DB)
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM bronze_products WHERE source = '{SOURCE}'")
    total = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM bronze_products WHERE source = '{SOURCE}' AND image_url LIKE '%storage.googleapis.com%'")
    gcs_count = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM bronze_products WHERE source = '{SOURCE}' AND image_url IS NULL")
    null_count = cur.fetchone()[0]

    pending = total - gcs_count - null_count

    print(f'Total products: {total}')
    print(f'GCS URLs (migrated): {gcs_count} ({gcs_count/total*100:.1f}%)')
    print(f'Source URLs (pending): {pending} ({pending/total*100:.1f}%)')
    print(f'NULL image_url: {null_count}')
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()

    if args.verify:
        verify()
    elif args.execute:
        migrate_images(dry_run=False, limit=args.limit)
    else:
        migrate_images(dry_run=True, limit=args.limit)
