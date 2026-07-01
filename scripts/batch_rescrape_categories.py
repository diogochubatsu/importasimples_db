#!/usr/bin/env python3
"""
Batch re-scraping of products without silver_category_id.
Processes 10 products at a time, analyzes results, then continues.
Also checks/fixes URLs.
"""
import os
import sys
import json
import time
import urllib.request
import psycopg2

# Add path for category_resolver
sys.path.insert(0, '/tmp/importasimples_db')
from category_resolver import resolve_category, ensure_category

# Database connection
def get_db():
    return psycopg2.connect(
        host='34.170.210.220',
        port=5432,
        dbname='importasimples_products',
        user='importasimples',
        password=os.environ.get('DB_PASSWORD', 'R{[{f<VajbC{<kvU'),
        sslmode='require'
    )

def search_rakumart(query, source='1688', page=1):
    """Search Rakumart BR across 3 sources."""
    if source == 'alibaba':
        url = "https://lavel.rakumart.com.br/client/home/searchGoods"
        body = json.dumps({'q': query, 'type': 'alibaba', 'page': page}).encode()
        content_type = 'application/json'
    else:
        url = "https://api.rakumart.com.br/index.php?mod=inc&act=ordersysPc&str=searchGoods"
        body = f"q={query.replace(' ', '+')}&type={source}&filter=&sort=&priceStart=&priceEnd=&snId=&page={page}".encode()
        content_type = 'application/x-www-form-urlencoded'

    req = urllib.request.Request(url, data=body, headers={
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': content_type,
        'Origin': 'https://www.rakumart.com.br',
        'Referer': 'https://www.rakumart.com.br/commoditysearch',
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return data.get('data', {}).get('content', [])
    except Exception as e:
        print(f"  Error ({source}): {e}")
        return []

def get_category_ids(items, source_id):
    """Extract category IDs from search results matching source_id."""
    for item in items:
        iid = str(item.get('iid', ''))
        if iid in source_id:
            return {
                'topCategoryId': item.get('topCategoryId', [None])[0] if item.get('topCategoryId') else None,
                'secondCategoryId': item.get('secondCategoryId', [None])[0] if item.get('secondCategoryId') else None,
                'thirdCategoryId': item.get('thirdCategoryId', [None])[0] if item.get('thirdCategoryId') else None,
            }
    return None

def process_batch(conn, products, batch_num):
    """Process a batch of products."""
    results = {
        'processed': 0,
        'updated': 0,
        'failed': 0,
        'url_fixed': 0,
        'categories_found': 0
    }
    
    cur = conn.cursor()
    
    for product in products:
        pid = product['id']
        source_id = product['source_id']
        marketplace = product['marketplace']
        title = product['title']
        current_url = product['url']
        
        print(f"\n--- Product {pid} ({marketplace}) ---")
        print(f"  Title: {title[:50]}...")
        
        # Extract source from marketplace
        source_type = marketplace.replace('rakumart-', '') if 'rakumart' in marketplace else marketplace
        
        # Search Rakumart for this product
        search_query = title[:50]  # Use first 50 chars of title
        items = search_rakumart(search_query, source=source_type)
        
        if not items:
            print(f"  ❌ No results from Rakumart API")
            results['failed'] += 1
            continue
        
        # Get category IDs
        cat_ids = get_category_ids(items, source_id)
        
        if not cat_ids:
            # Try with extracted IID from source_id
            iid_match = source_id.split(':')[-1].split('_')[-1].split('/')[-1].split('.')[0]
            for item in items:
                if str(item.get('iid', '')) == iid_match:
                    cat_ids = {
                        'topCategoryId': item.get('topCategoryId', [None])[0] if item.get('topCategoryId') else None,
                        'secondCategoryId': item.get('secondCategoryId', [None])[0] if item.get('secondCategoryId') else None,
                        'thirdCategoryId': item.get('thirdCategoryId', [None])[0] if item.get('thirdCategoryId') else None,
                    }
                    break
        
        if cat_ids and any(cat_ids.values()):
            print(f"  ✅ Categories found: L1={cat_ids['topCategoryId']}, L2={cat_ids['secondCategoryId']}, L3={cat_ids['thirdCategoryId']}")
            
            # Resolve category
            result = resolve_category(
                conn, 
                platform=source_type,
                l1=str(cat_ids['topCategoryId']) if cat_ids['topCategoryId'] else None,
                l2=str(cat_ids['secondCategoryId']) if cat_ids['secondCategoryId'] else None,
                l3=str(cat_ids['thirdCategoryId']) if cat_ids['thirdCategoryId'] else None
            )
            
            if result and result.get('silver_category_id'):
                print(f"  ✅ Mapped to silver_category_id={result['silver_category_id']} ({result.get('l1', 'unknown')})")
                
                # Update product
                cur.execute("""
                    UPDATE bronze_products 
                    SET silver_category_id = %s
                    WHERE id = %s
                """, (result['silver_category_id'], pid))
                
                results['updated'] += 1
                results['categories_found'] += 1
            else:
                print(f"  ⚠️ Could not resolve category")
                results['failed'] += 1
        else:
            print(f"  ⚠️ No category IDs found")
            results['failed'] += 1
        
        # Check/fix URL
        if current_url and 'rakumart.com.br' in current_url:
            if '/product/' in current_url:
                # Fix old URL format
                new_url = current_url.replace('/product/', '/productdetails?').replace('&searchType=keywordSearch', '&searchType=classificationSearch')
                if 'type=' not in new_url:
                    new_url = f"https://www.rakumart.com.br/productdetails?type={source_type}&iid={source_id.split(':')[-1]}&searchType=classificationSearch"
                
                cur.execute("""
                    UPDATE bronze_products 
                    SET url = %s
                    WHERE id = %s
                """, (new_url, pid))
                print(f"  🔧 URL fixed: {new_url[:60]}...")
                results['url_fixed'] += 1
        
        results['processed'] += 1
        time.sleep(0.5)  # Rate limiting
    
    conn.commit()
    return results

def main():
    """Main function."""
    conn = get_db()
    cur = conn.cursor()
    
    # Get products without silver_category_id
    cur.execute("""
        SELECT id, source_id, marketplace, title, url, silver_category_id
        FROM bronze_products 
        WHERE source = 'arbitlens_china' 
          AND silver_category_id IS NULL
        ORDER BY id
    """)
    
    all_products = cur.fetchall()
    total = len(all_products)
    
    print(f"📊 Total products without silver_category_id: {total}")
    print(f"📦 Processing in batches of 10...")
    
    batch_size = 10
    all_results = []
    
    for i in range(0, total, batch_size):
        batch = all_products[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"\n{'='*60}")
        print(f"BATCH {batch_num} ({i+1}-{min(i+batch_size, total)} of {total})")
        print(f"{'='*60}")
        
        # Convert to dicts
        batch_dicts = []
        for row in batch:
            batch_dicts.append({
                'id': row[0],
                'source_id': row[1],
                'marketplace': row[2],
                'title': row[3],
                'url': row[4],
                'silver_category_id': row[5]
            })
        
        results = process_batch(conn, batch_dicts, batch_num)
        all_results.append(results)
        
        print(f"\n📈 Batch {batch_num} Results:")
        print(f"  Processed: {results['processed']}")
        print(f"  Updated: {results['updated']}")
        print(f"  Failed: {results['failed']}")
        print(f"  URLs fixed: {results['url_fixed']}")
        
        # Print running totals
        total_updated = sum(r['updated'] for r in all_results)
        total_failed = sum(r['failed'] for r in all_results)
        total_urls = sum(r['url_fixed'] for r in all_results)
        
        print(f"\n📊 Running Totals:")
        print(f"  Updated: {total_updated}/{total}")
        print(f"  Failed: {total_failed}")
        print(f"  URLs fixed: {total_urls}")
        
        # Pause after each batch for analysis
        if batch_num < (total // batch_size):
            print(f"\n⏸️  Pausing 2 seconds for analysis...")
            time.sleep(2)
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"FINAL SUMMARY")
    print(f"{'='*60}")
    
    total_updated = sum(r['updated'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    total_urls = sum(r['url_fixed'] for r in all_results)
    
    print(f"Total processed: {sum(r['processed'] for r in all_results)}/{total}")
    print(f"Total updated: {total_updated}")
    print(f"Total failed: {total_failed}")
    print(f"Total URLs fixed: {total_urls}")
    
    conn.close()

if __name__ == '__main__':
    main()
