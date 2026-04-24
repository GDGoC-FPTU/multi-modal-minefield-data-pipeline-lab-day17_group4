import pandas as pd
import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Process sales records, handling type traps and duplicates.


def _parse_price(value):
    if pd.isna(value):
        return None

    raw = str(value).strip()
    lowered = raw.lower()
    if lowered in {"n/a", "null", "none", "liên hệ", "lien he", ""}:
        return None

    if re.search(r"[a-zA-Z]", raw) and "$" not in raw:
        return None

    cleaned = raw.replace(",", "")
    cleaned = cleaned.replace("$", "")
    cleaned = cleaned.strip()

    try:
        parsed = float(cleaned)
    except ValueError:
        return None

    if parsed < 0:
        return None
    return parsed


def _parse_date(value):
    if pd.isna(value):
        return None

    raw = str(value).strip()
    known_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%B %dth %Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d %b %Y",
    ]

    for fmt in known_formats:
        dt = pd.to_datetime(raw, format=fmt, errors="coerce")
        if not pd.isna(dt):
            return dt.date().isoformat()

    dt = pd.to_datetime(raw, errors="coerce")
    if pd.isna(dt):
        return None
    return dt.date().isoformat()

def process_sales_csv(file_path):
    # --- FILE READING (Handled for students) ---
    df = pd.read_csv(file_path)
    # ------------------------------------------

    df = df.drop_duplicates(subset=["id"], keep="first").copy()
    df["clean_price"] = df["price"].apply(_parse_price)
    df["normalized_date"] = df["date_of_sale"].apply(_parse_date)
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce")

    docs = []
    for _, row in df.iterrows():
        sale_id = int(row["id"])
        clean_price = row["clean_price"]
        normalized_date = row["normalized_date"]

        price_text = f"{clean_price:.2f}" if clean_price is not None else "unknown"
        docs.append({
            "document_id": f"csv-{sale_id}",
            "content": (
                f"Sale record for {row['product_name']} in category {row['category']} "
                f"priced at {price_text} {row['currency']} on {normalized_date or 'unknown date'}."
            ),
            "source_type": "CSV",
            "author": str(row.get("seller_id", "Unknown")),
            "timestamp": normalized_date,
            "source_metadata": {
                "original_id": sale_id,
                "product_name": row["product_name"],
                "category": row["category"],
                "clean_price": clean_price,
                "currency": row["currency"],
                "stock_quantity": None if pd.isna(row["stock_quantity"]) else int(row["stock_quantity"]),
            },
        })

    return docs

