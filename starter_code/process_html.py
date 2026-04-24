from bs4 import BeautifulSoup
import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract product data from the HTML table, ignoring boilerplate.

def parse_html_catalog(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    # ------------------------------------------

    table = soup.find('table', id='main-catalog')
    if table is None:
        return []

    docs = []
    rows = table.select('tbody tr')
    for row in rows:
        cells = [c.get_text(strip=True) for c in row.find_all('td')]
        if len(cells) < 6:
            continue

        sku, name, category, raw_price, raw_stock, rating = cells
        lowered_price = raw_price.lower()
        if lowered_price in {'n/a', 'liên hệ', 'lien he', 'null', 'none'}:
            parsed_price = None
        else:
            digits = re.sub(r'[^\d]', '', raw_price)
            parsed_price = int(digits) if digits else None

        try:
            stock_quantity = int(raw_stock)
        except ValueError:
            stock_quantity = None

        price_text = f"{parsed_price} VND" if parsed_price is not None else "unknown price"
        docs.append({
            "document_id": f"html-{sku}",
            "content": f"Catalog item {name} ({category}) listed at {price_text}.",
            "source_type": "HTML",
            "author": "Unknown",
            "timestamp": None,
            "source_metadata": {
                "sku": sku,
                "name": name,
                "category": category,
                "listed_price_vnd": parsed_price,
                "stock_quantity": stock_quantity,
                "rating": rating,
            },
        })

    return docs

