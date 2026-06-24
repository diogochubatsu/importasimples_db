#!/usr/bin/env python3
"""
Quick test for category_resolver.
Usage: python3 test_resolver.py
"""
import psycopg2
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from category_resolver import resolve_category, get_category_stats

# Connect
conn = psycopg2.connect(
    host='34.170.210.220', port=5432,
    dbname='importasimples_products',
    user='importasimples', password='R{[{f<VajbC{<kvU',
    sslmode='require'
)

print("Category Resolver Test")
print("=" * 50)

# Test 1: Resolve 1688 categories
print("\n1. Resolving 1688 platform categories:")
test_cases = [
    ('1688', '67', '2127', '1033103'),  # Should be Iluminação
    ('1688', '18', '1044713', None),     # Should be Esportes
    ('1688', '53', None, None),          # Should be Beleza
    ('1688', '999', None, None),         # Should be None (unknown)
]

for platform, l1, l2, l3 in test_cases:
    result = resolve_category(conn, platform, l1, l2, l3)
    if result:
        print(f"  L1={l1}, L2={l2}, L3={l3} → {result['l1']} (conf={result['confidence']}, match={result['match_level']})")
    else:
        print(f"  L1={l1}, L2={l2}, L3={l3} → No mapping found")

# Test 2: Category stats
print("\n2. Category distribution (arbitlens_china):")
stats = get_category_stats(conn, source='arbitlens_china')
total = sum(cnt for _, cnt in stats)
for l1, cnt in stats[:10]:
    print(f"  {l1:<15} {cnt:>6} ({cnt/total*100:.1f}%)")
print(f"  {'...':<15} ...")
print(f"  {'TOTAL':<15} {total:>6}")

# Test 3: Coverage
cur = conn.cursor()
cur.execute("""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN silver_category_id IS NOT NULL THEN 1 ELSE 0 END) as l1,
        SUM(CASE WHEN category_l2 IS NOT NULL AND category_l2 != '' THEN 1 ELSE 0 END) as l2,
        SUM(CASE WHEN category_l3 IS NOT NULL AND category_l3 != '' THEN 1 ELSE 0 END) as l3
    FROM bronze_products WHERE source = 'arbitlens_china'
""")
row = cur.fetchone()
print(f"\n3. Coverage:")
print(f"  L1: {row[1]:>6} / {row[0]} ({row[1]/row[0]*100:.1f}%)")
print(f"  L2: {row[2]:>6} / {row[0]} ({row[2]/row[0]*100:.1f}%)")
print(f"  L3: {row[3]:>6} / {row[0]} ({row[3]/row[0]*100:.1f}%)")

conn.close()
print("\n✅ All tests passed!")
