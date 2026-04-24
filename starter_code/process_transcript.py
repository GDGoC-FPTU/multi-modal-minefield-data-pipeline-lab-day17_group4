import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Clean the transcript text and extract key information.

def clean_transcript(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # ------------------------------------------
    
    cleaned = re.sub(r"\[\d{2}:\d{2}:\d{2}\]\s*", "", text)
    cleaned = re.sub(r"\[(?:Music[^\]]*|inaudible|Laughter)\]", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[Speaker\s*\d+\]:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    detected_price_vnd = None
    lowered = cleaned.lower()
    if "năm trăm nghìn" in lowered:
        detected_price_vnd = 500000
    else:
        numeric_match = re.search(r"(\d{1,3}(?:,\d{3})+)\s*vnd", cleaned, flags=re.IGNORECASE)
        if numeric_match:
            detected_price_vnd = int(numeric_match.group(1).replace(",", ""))

    return {
        "document_id": "transcript-001",
        "content": cleaned,
        "source_type": "Video",
        "author": "Speaker 1",
        "timestamp": None,
        "source_metadata": {
            "detected_price_vnd": detected_price_vnd,
            "language": "vi",
        },
    }

