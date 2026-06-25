#!/usr/bin/env python3
"""
export_categories.py — Export category data to JSON for backup/audit.

Usage:
    python3 export_categories.py                    # Export all
    python3 export_categories.py --output /path     # Custom output dir
    python3 export_categories.py --stats            # Show stats only
"""

import psycopg2
import json
import argparse
from pathlib import Path
from datetime import datetime

# Database config
DB_CONFIG = {
    'host': '34.170.210.220',
    'port': 5432,
    'dbname': 'importasimples_products',
    'user': 'importasimples',
    'password': 'R{[{f<VajbC{<kvU',
    'sslmode': 'require'
}


def export_categories(conn):
    """Export silver_categories to JSON."""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, l1, l2, l3, l4, icon, ncm_codes, 
               created_at, updated_at
        FROM silver_categories
        ORDER BY id
    """)
    
    categories = []
    for row in cur.fetchall():
        categories.append({
            'id': row[0],
            'l1': row[1],
            'l2': row[2],
            'l3': row[3],
            'l4': row[4],
            'icon': row[5],
            'ncm_codes': row[6],
            'created_at': row[7].isoformat() if row[7] else None,
            'updated_at': row[8].isoformat() if row[8] else None,
        })
    
    cur.close()
    return categories


def export_mappings(conn):
    """Export silver_categories_map to JSON."""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, platform, platform_l1_id, platform_l2_id, 
               platform_l3_id, platform_category_name,
               silver_category_id, confidence, verified,
               created_at, updated_at, created_by
        FROM silver_categories_map
        ORDER BY platform, platform_l1_id
    """)
    
    mappings = []
    for row in cur.fetchall():
        mappings.append({
            'id': row[0],
            'platform': row[1],
            'platform_l1_id': row[2],
            'platform_l2_id': row[3],
            'platform_l3_id': row[4],
            'platform_category_name': row[5],
            'silver_category_id': row[6],
            'confidence': float(row[7]) if row[7] else None,
            'verified': row[8],
            'created_at': row[9].isoformat() if row[9] else None,
            'updated_at': row[10].isoformat() if row[10] else None,
            'created_by': row[11],
        })
    
    cur.close()
    return mappings


def get_stats(conn):
    """Get category statistics."""
    cur = conn.cursor()
    
    stats = {}
    
    # Total counts
    cur.execute("SELECT COUNT(*) FROM silver_categories")
    stats['total_categories'] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM silver_categories WHERE l2 IS NULL")
    stats['l1_count'] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM silver_categories WHERE l2 IS NOT NULL AND l3 IS NULL")
    stats['l2_count'] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM silver_categories WHERE l3 IS NOT NULL")
    stats['l3_count'] = cur.fetchone()[0]
    
    # Mappings by platform
    cur.execute("""
        SELECT platform, COUNT(*) 
        FROM silver_categories_map 
        GROUP BY platform
    """)
    stats['mappings_by_platform'] = {row[0]: row[1] for row in cur.fetchall()}
    
    # Products by source
    cur.execute("""
        SELECT source, COUNT(*) as total,
               SUM(CASE WHEN silver_category_id IS NOT NULL THEN 1 ELSE 0 END) as mapped
        FROM bronze_products
        GROUP BY source
    """)
    stats['products_by_source'] = {}
    for row in cur.fetchall():
        stats['products_by_source'][row[0]] = {
            'total': row[1],
            'mapped': row[2],
            'coverage': round(row[2] * 100 / row[1], 1) if row[1] > 0 else 0
        }
    
    # Created_by breakdown
    cur.execute("""
        SELECT created_by, COUNT(*) 
        FROM silver_categories_map 
        GROUP BY created_by
    """)
    stats['mappings_by_agent'] = {row[0] or 'unknown': row[1] for row in cur.fetchall()}
    
    cur.close()
    return stats


def main():
    parser = argparse.ArgumentParser(description='Export category data to JSON')
    parser.add_argument('--output', default='platform_categories', 
                       help='Output directory (default: platform_categories)')
    parser.add_argument('--stats', action='store_true',
                       help='Show stats only, no export')
    args = parser.parse_args()
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    if args.stats:
        stats = get_stats(conn)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export categories
        categories = export_categories(conn)
        cat_file = output_dir / f'silver_categories_{timestamp}.json'
        cat_file.write_text(json.dumps(categories, indent=2, ensure_ascii=False))
        print(f'✓ Exported {len(categories)} categories → {cat_file}')
        
        # Export mappings
        mappings = export_mappings(conn)
        map_file = output_dir / f'silver_categories_map_{timestamp}.json'
        map_file.write_text(json.dumps(mappings, indent=2, ensure_ascii=False))
        print(f'✓ Exported {len(mappings)} mappings → {map_file}')
        
        # Also export latest (no timestamp)
        (output_dir / 'silver_categories.json').write_text(
            json.dumps(categories, indent=2, ensure_ascii=False)
        )
        (output_dir / 'silver_categories_map.json').write_text(
            json.dumps(mappings, indent=2, ensure_ascii=False)
        )
        print(f'✓ Updated latest exports')
        
        # Stats
        stats = get_stats(conn)
        stats_file = output_dir / f'stats_{timestamp}.json'
        stats_file.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
        print(f'✓ Exported stats → {stats_file}')
    
    conn.close()
    print('\nDone!')


if __name__ == '__main__':
    main()
