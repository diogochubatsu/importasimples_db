import requests, json, re, time, sys, os
from bs4 import BeautifulSoup
import psycopg2

DB_HOST = '34.170.210.220'
DB_PORT = 5432
DB_NAME = 'importasimples_products'
DB_USER = 'importasimples'
DB_PASS = 'R{[{f<VajbC{<kvU'

API_URL = 'https://scraper-api.decodo.com/v2/scrape'
API_AUTH = 'Basic VTAwMDA0MzkyODI6UFdfMWJlYWQzNDU3NWIwYTA1NTY5YzUyNmFhMTcxOThkNDdj'

LOG_FILE = '/home/hermeshideki/scrape_final.log'

def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

l3_map = {
    'mouse-gamer': ('Eletrônicos', 'Periféricos', 'Mouse'),
    'pelicula-vidro': ('Eletrônicos', 'Acessórios para Celulares e Smartphones', 'Películas'),
    'capa-celular': ('Eletrônicos', 'Acessórios para Celulares e Smartphones', 'Capas'),
    'cabo-hdmi': ('Eletrônicos', 'Cabos e Conectores', 'Cabos HDMI'),
    'cabo-lightning': ('Eletrônicos', 'Cabos e Conectores', 'Cabos Lightning'),
    'cabo-usb-tipo-c': ('Eletrônicos', 'Cabos e Conectores', 'Cabos USB-C'),
    'cabo-usb': ('Eletrônicos', 'Cabos e Conectores', 'Cabos USB'),
    'camera-gopro': ('Eletrônicos', 'Câmeras e Drones', 'Câmeras de Ação'),
    'camera-dash-cam': ('Eletrônicos', 'Câmeras e Drones', 'Câmeras Veiculares'),
    'camera-digital': ('Eletrônicos', 'Câmeras e Drones', 'Câmeras Digitais'),
    'camera-seguranca-wifi': ('Eletrônicos', 'Segurança e Vigilância', 'Câmeras de Segurança'),
    'capa-tablet': ('Eletrônicos', 'Acessórios para Tablets', 'Capas'),
    'pelicula-tablet': ('Eletrônicos', 'Acessórios para Tablets', 'Películas'),
    'carregador-parede': ('Eletrônicos', 'Carregadores', 'Carregadores de Parede'),
    'carregador-sem-fio': ('Eletrônicos', 'Carregadores', 'Carregadores Sem Fio'),
    'carregador-veicular': ('Eletrônicos', 'Carregadores', 'Carregadores Veiculares'),
    'acessorio-celular': ('Eletrônicos', 'Acessórios para Celulares e Smartphones', 'Acessórios'),
    'capinha-celular': ('Eletrônicos', 'Acessórios para Celulares e Smartphones', 'Capas'),
    'pelicula-celular': ('Eletrônicos', 'Acessórios para Celulares e Smartphones', 'Películas'),
    'aspirador': ('Eletrônicos', 'Eletrodomésticos', 'Aspiradores'),
    'ferro-vapor': ('Eletrônicos', 'Eletrodomésticos', 'Ferros de Vapor'),
    'fritadeira': ('Eletrônicos', 'Eletrodomésticos', 'Fritadeiras'),
    'liquidificador': ('Eletrônicos', 'Eletrodomésticos', 'Liquidificadores'),
    'secador-cabelo': ('Eletrônicos', 'Cuidados Pessoais', 'Secadores de Cabelo'),
    'fone-bluetooth': ('Eletrônicos', 'Áudio', 'Fones de Ouvido Bluetooth'),
    'fone-com-fio': ('Eletrônicos', 'Áudio', 'Fones de Ouvido com Fio'),
    'fone-esportivo': ('Eletrônicos', 'Áudio', 'Fones Esportivos'),
    'fita-led': ('Eletrônicos', 'Iluminação', 'Fitas LED'),
    'lampada-led': ('Eletrônicos', 'Iluminação', 'Lâmpadas LED'),
    'mousepad': ('Eletrônicos', 'Periféricos', 'Mousepads'),
    'notebook-cooler': ('Eletrônicos', 'Acessórios para Notebooks', 'Coolers'),
    'suporte-monitor': ('Eletrônicos', 'Suportes', 'Suportes de Monitor'),
    'power-bank': ('Eletrônicos', 'Carregadores', 'Power Banks'),
    'power-bank-solar': ('Eletrônicos', 'Carregadores', 'Power Banks Solares'),
    'relogio-masculino': ('Eletrônicos', 'Relógios', 'Relógios Masculinos'),
    'smartwatch': ('Eletrônicos', 'Relógios', 'Smartwatches'),
    'alarme-casa': ('Eletrônicos', 'Segurança e Vigilância', 'Alarmes'),
    'cofre': ('Eletrônicos', 'Segurança e Vigilância', 'Cofres'),
    'lampada-inteligente': ('Eletrônicos', 'Iluminação', 'Lâmpadas Inteligentes'),
    'tomada-inteligente': ('Eletrônicos', 'Automação Residencial', 'Tomadas Inteligentes'),
    'sensor': ('Eletrônicos', 'Automação Residencial', 'Sensores'),
    'suporte-mesa': ('Eletrônicos', 'Suportes', 'Suportes de Mesa'),
    'suporte-veiculo': ('Eletrônicos', 'Suportes', 'Suportes Veiculares'),
    'teclado-mecanico': ('Eletrônicos', 'Periféricos', 'Teclados Mecânicos'),
    'teclado-sem-fio': ('Eletrônicos', 'Periféricos', 'Teclados Sem Fio'),
    'monope': ('Eletrônicos', 'Acessórios para Celulares e Smartphones', 'Monopés'),
    'tripe-profissional': ('Eletrônicos', 'Fotografia', 'Tripés'),
    'tripe-universal': ('Eletrônicos', 'Fotografia', 'Tripés'),
    'bolsa-mao': ('Moda', 'Acessórios', 'Bolsas'),
    'bolsa-ombro': ('Moda', 'Acessórios', 'Bolsas'),
    'bolsa-viagem': ('Moda', 'Acessórios', 'Bolsas'),
    'cinto-couro': ('Moda', 'Acessórios', 'Cintos'),
    'meias-esportivas': ('Moda', 'Acessórios', 'Meias'),
    'cinta-modeladora': ('Moda', 'Lingerie', 'Cintas Modeladoras'),
    'calcinha': ('Moda', 'Lingerie', 'Calcinhas'),
    'cueca': ('Moda', 'Lingerie', 'Cuecas'),
    'bone': ('Moda', 'Chapéus e Bonés', 'Bonés'),
    'gorro': ('Moda', 'Chapéus e Bonés', 'Gorros'),
    'vestido-festa': ('Moda', 'Roupas', 'Vestidos'),
    'necessaire': ('Moda', 'Acessórios', 'Necessaires'),
    'mala-viagem': ('Moda', 'Malas e Sacolas', 'Malas'),
    'toalha': ('Moda', 'Casa', 'Toalhas'),
    'chinelo': ('Moda', 'Calçados', 'Chinelos'),
    'mochila': ('Moda', 'Malas e Sacolas', 'Mochilas'),
    'camisa-masculina': ('Moda', 'Roupas Masculinas', 'Camisas'),
    'calca-masculina': ('Moda', 'Roupas Masculinas', 'Calças')
}

def scrape_ml_search(search_term):
    url = f'https://lista.mercadolivre.com.br/{search_term}'
    headers = {
        'Authorization': API_AUTH,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        'url': url,
        'proxy_pool': 'premium',
        'headless': 'html',
        'locale': 'pt-br',
        'geo': 'br'
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        data = resp.json()

        if 'results' not in data or not data['results']:
            return []

        html = data['results'][0]['content']
        soup = BeautifulSoup(html, 'html.parser')

        products = []
        seen_ids = set()

        product_links = soup.find_all('a', href=re.compile(r'/p/MLB'))

        for link in product_links:
            href = link.get('href', '')
            mlb_match = re.search(r'(MLB\d+)', href)
            if not mlb_match:
                continue

            mlb_id = mlb_match.group(1)
            if mlb_id in seen_ids:
                continue
            seen_ids.add(mlb_id)

            # Walk up to find poly-card parent
            card = None
            parent = link.parent
            while parent and parent.name != 'body':
                classes = parent.get('class', [])
                if 'poly-card' in classes:
                    card = parent
                    break
                parent = parent.parent

            if card:
                img = card.find('img', src=re.compile(r'mlstatic'))
                if not img:
                    img = card.find('img')

                price = card.find(class_=re.compile(r'andes-money-amount__fraction'))
                title = card.find(class_=re.compile(r'poly-component__title'))
                if not title:
                    title = card.find(class_=re.compile(r'title'))

                img_url = img.get('src', '') if img else ''
                title_text = title.get_text(strip=True) if title else f'Produto {mlb_id}'
                price_text = price.get_text(strip=True) if price else '0'

                price_clean = price_text.replace('.', '').replace(',', '.')

                if img_url and 'mlstatic' in img_url:
                    products.append({
                        'mlb_id': mlb_id,
                        'title': title_text,
                        'image_url': img_url,
                        'price': price_clean
                    })

        return products

    except Exception as e:
        log(f"ERROR scraping {search_term}: {e}")
        return []

def main():
    # Clear log
    with open(LOG_FILE, 'w') as f:
        f.write(f"=== ML Scraper Started {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()

    cursor.execute("SELECT source_id FROM bronze_products WHERE source='arbitlens_brasil' AND source_id LIKE 'ml:%'")
    existing_ids = set(row[0] for row in cursor.fetchall())
    log(f"Existing ML products: {len(existing_ids)}")

    all_terms = list(l3_map.keys())
    total_inserted = 0
    total_found = 0

    for i, search_term in enumerate(all_terms):
        log(f"[{i+1}/{len(all_terms)}] {search_term}...")

        products = scrape_ml_search(search_term)
        total_found += len(products)

        inserted = 0
        for product in products:
            source_id = f"ml:{product['mlb_id']}"
            if source_id in existing_ids:
                continue

            l1, l2, l3 = l3_map[search_term]

            query = """
            INSERT INTO bronze_products (source, source_id, title, image_url, price_brl, category_l1, category_l2, category_l3)
            VALUES ('arbitlens_brasil', %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """

            try:
                cursor.execute(query, (
                    source_id,
                    product['title'],
                    product['image_url'],
                    product['price'],
                    l1, l2, l3
                ))
                existing_ids.add(source_id)
                inserted += 1
                total_inserted += 1
            except Exception as e:
                log(f"  DB Error {source_id}: {e}")
                conn.rollback()
                continue

        conn.commit()
        log(f"  Found: {len(products)}, Inserted: {inserted}")
        time.sleep(0.3)

    log(f"\n=== COMPLETE ===")
    log(f"Total found: {total_found}")
    log(f"Total inserted: {total_inserted}")

    cursor.execute("""
        SELECT COUNT(*) FROM bronze_products
        WHERE source='arbitlens_brasil' AND source_id LIKE 'ml:%'
    """)
    log(f"Total ML products now: {cursor.fetchone()[0]}")

    cursor.execute("""
        SELECT COUNT(*) FILTER (WHERE image_url IS NULL OR image_url = '') as no_image
        FROM bronze_products
        WHERE source='arbitlens_brasil' AND source_id LIKE 'ml:%'
    """)
    log(f"Products without images: {cursor.fetchone()[0]}")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
