"""Verify 1688 URLs using Decodo Site Unblocker."""
import psycopg2
import requests
import time
import json
import sys
import urllib3
urllib3.disable_warnings()

# Decodo Site Unblocker credentials
SU_USER = "U0000446415"
SU_PASS = "PW_175269699c8c2859bc8499cc9161922fb"
SU_PROXY = "https://unblock.decodo.com:60000"
SU_HEADERS = {
    'X-SU-Geo': 'China',
    'X-SU-Locale': 'zh-cn',
    'X-SU-Headless': 'html',
    'X-SU-Markdown': '1',
}

# DB credentials
DB_HOST = "34.170.210.220"
DB_PORT = 5432
DB_NAME = "importasimples_products"
DB_USER = "importasimples"
DB_PASS = "R{[{f<VajbC{<kvU"

def verify_url(url, timeout=45):
    """Verify a single URL using Decodo Site Unblocker."""
    try:
        r = requests.get(
            url,
            proxies={'https': SU_PROXY},
            auth=(SU_USER, SU_PASS),
            headers=SU_HEADERS,
            verify=False,
            timeout=timeout
        )
        
        content = r.text
        has_product = '阿里巴巴' in content or '1688.com' in content
        has_captcha = 'captcha' in content.lower() or 'rgv587_flag' in content
        
        return {
            'status': 'OK' if has_product and not has_captcha else 'FAIL',
            'size': len(content),
            'has_product': has_product,
            'has_captcha': has_captcha,
            'content_preview': content[:200]
        }
    except requests.Timeout:
        return {'status': 'TIMEOUT', 'size': 0, 'has_product': False, 'has_captcha': False}
    except Exception as e:
        return {'status': 'ERROR', 'size': 0, 'has_product': False, 'has_captcha': False, 'error': str(e)[:50]}

def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS, sslmode='require',
        connect_timeout=10
    )
    cur = conn.cursor()
    
    cur.execute(f"""
        SELECT id, source_id, url, title, category_l1, category_l2
        FROM bronze_products 
        WHERE source = '1688' 
        AND url LIKE '%detail.1688.com%'
        AND title IS NOT NULL AND title != ''
        ORDER BY RANDOM()
        LIMIT {limit}
    """)
    products = cur.fetchall()
    
    print(f"Verificando {len(products)} URLs com Site Unblocker:")
    print()
    
    verified = 0
    failed = 0
    errors = 0
    
    for pid, sid, url, title, l1, l2 in products:
        time.sleep(3)
        result = verify_url(url)
        
        if result['status'] == 'OK':
            verified += 1
            print(f"  OK ID={pid} ({l1}>{l2}) [{result['size']} bytes]")
        elif result['status'] == 'TIMEOUT':
            errors += 1
            print(f"  TIMEOUT ID={pid} ({l1}>{l2})")
        else:
            errors += 1
            print(f"  ERR ID={pid} ({l1}>{l2}): {result.get('error', 'captcha')}")
    
    total = len(products)
    print(f"\nRESULTADO ({total} URLs):")
    print(f"  Verificadas: {verified} ({verified*100//total}%)")
    print(f"  Erros: {errors}")
    
    results = {
        'total': total,
        'verified': verified,
        'errors': errors,
        'verified_pct': verified*100//total
    }
    with open('/tmp/url_verification_results.json', 'w') as f:
        json.dump(results, f)
    
    conn.close()

if __name__ == '__main__':
    main()
