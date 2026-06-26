#!/usr/bin/env python3
"""
Simple keyword-based classifier for products without silver_category_id.
Uses product titles to classify into categories.
"""
import os
import sys
import psycopg2

# Keywords for each category
CATEGORY_KEYWORDS = {
    'Audio': ['fone', '耳机', 'caixa de som', 'microfone', 'áudio', 'bluetooth', 'speaker', 'headphone', 'earphone', 'coluna de som', 'rádio'],
    'Eletrônicos': ['celular', '手机', 'tablet', 'notebook', 'computador', 'mouse', 'teclado', 'cabo', 'carregador', '充电器', '充电宝', 'power bank', 'hub', 'adaptador', 'usb', 'hdmi', 'dock', 'estação de acoplamento', 'estação de docagem', 'conversor', '转换'],
    'Wearables': ['手表', 'relógio', 'smartwatch', 'pulseira', 'fitness', 'band'],
    'Moda': ['roupa', 'camisa', 'calça', 'vestido', '衣', '服', '帽', 'polo', 'camiseta'],
    'Beleza': ['maquiagem', '化妆品', 'skincare', 'cabelo', 'unha'],
    'Casa': ['casa', '家', 'decoração', 'organização', 'cozinha', 'socket', '插座', 'extensão'],
    'Cozinha': ['cozinha', 'panela', 'utensílio', '厨房', 'vela', 'aromática'],
    'Esportes': ['esporte', 'sport', '瑜伽', 'fitness', '足球'],
    'Ferramentas': ['ferramenta', '工具', '电钻', 'drill', 'serra', 'chave', 'hexagonal'],
    'Infantis': ['bebê', 'baby', 'brinquedo', 'toy', 'child', '儿童'],
    'Pets': ['pet', '动物', '狗', '猫', 'racao'],
    'Iluminação': ['luz', 'lampada', '灯', 'led', 'iluminação', 'vela'],
    'Automotivo': ['carro', '汽车', 'veículo', 'auto', 'gps', '定位', 'rastreador'],
    'Calçados': ['sapato', '鞋', 'tênis', 'sandália'],
    'Segurança': ['segurança', '摄像头', 'camera', 'alarme'],
    'Saúde': ['saúde', '健康', 'medic', '体温', '血压'],
    'Jardim': ['jardim', '花园', 'plant', 'água'],
    'Móveis': ['mesa', 'cadeira', '桌子', '椅子', 'sofá'],
    'Papelaria': ['papel', '笔', 'lápis', 'caderno'],
    'Bolsas': ['bolsa', 'mochila', 'bag', '背包'],
    'Acessórios': ['acessório', '配件', '戒指', '项链'],
    'Eletrodomésticos': ['aspirador', '吸尘器', 'máquina', 'ferro'],
    'Computadores': ['computador', '电脑', 'monitor', 'placa'],
    'Têxteis': ['tecido', '面料', 'cama', 'toalha', 'fio', 'pavio'],
    'Industrial': ['industrial', '工业', 'máquina'],
    'Organização': ['organização', '收纳', 'estante', 'gaveta'],
}

def classify_by_title(title):
    """Classify product by title using keywords."""
    title_lower = title.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return category
    
    return 'uncategorized'

def main():
    conn = psycopg2.connect(
        host='34.170.210.220',
        port=5432,
        dbname='importasimples_products',
        user='importasimples',
        password=os.environ.get('DB_PASSWORD', 'R{[{f<VajbC{<kvU'),
        sslmode='require'
    )
    
    cur = conn.cursor()
    
    # Get products without silver_category_id
    cur.execute("""
        SELECT id, title, marketplace
        FROM bronze_products 
        WHERE source = 'arbitlens_china' 
          AND silver_category_id IS NULL
        ORDER BY id
        LIMIT 50
    """)
    
    products = cur.fetchall()
    print(f"📊 Processing {len(products)} products...")
    
    updated = 0
    for pid, title, marketplace in products:
        category = classify_by_title(title)
        
        if category != 'uncategorized':
            # Get silver_category_id for this category
            cur.execute("""
                SELECT id FROM silver_categories 
                WHERE l1 = %s AND l2 IS NULL AND l3 IS NULL
            """, (category,))
            row = cur.fetchone()
            
            if row:
                cur.execute("""
                    UPDATE bronze_products 
                    SET silver_category_id = %s
                    WHERE id = %s
                """, (row[0], pid))
                updated += 1
                print(f"  ✅ {pid}: {category} ({title[:30]}...)")
            else:
                print(f"  ⚠️ {pid}: Category '{category}' not found in silver_categories")
        else:
            print(f"  ❌ {pid}: Could not classify ({title[:30]}...)")
    
    conn.commit()
    print(f"\n✅ Updated {updated}/{len(products)} products")
    
    conn.close()

if __name__ == '__main__':
    main()
