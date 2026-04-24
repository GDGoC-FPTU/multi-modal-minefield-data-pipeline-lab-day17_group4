import json
import time
import os
from typing import Any, Dict, List

# Robust path handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "raw_data")


# Import role-specific modules
from schema import UnifiedDocument
from process_pdf import extract_pdf_data
from process_transcript import clean_transcript
from process_html import parse_html_catalog
from process_csv import process_sales_csv
from process_legacy_code import extract_logic_from_code
from quality_check import run_quality_gate

# ==========================================
# ROLE 4: DEVOPS & INTEGRATION SPECIALIST
# ==========================================
# Task: Orchestrate the ingestion pipeline and handle errors/SLA.

def main():
    start_time = time.time()
    final_kb: List[Dict[str, Any]] = []
    stage_durations: Dict[str, float] = {}
    
    # --- FILE PATH SETUP (Handled for students) ---
    pdf_path = os.path.join(RAW_DATA_DIR, "lecture_notes.pdf")
    trans_path = os.path.join(RAW_DATA_DIR, "demo_transcript.txt")
    html_path = os.path.join(RAW_DATA_DIR, "product_catalog.html")
    csv_path = os.path.join(RAW_DATA_DIR, "sales_records.csv")
    code_path = os.path.join(RAW_DATA_DIR, "legacy_pipeline.py")
    
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "processed_knowledge_base.json")
    # ----------------------------------------------

    sources = [
        ("pdf", extract_pdf_data, pdf_path),
        ("transcript", clean_transcript, trans_path),
        ("html", parse_html_catalog, html_path),
        ("csv", process_sales_csv, csv_path),
        ("legacy_code", extract_logic_from_code, code_path),
    ]

    for source_name, processor, file_path in sources:
        stage_start = time.time()

        if not os.path.exists(file_path):
            print(f"[{source_name}] Missing input file: {file_path}. Skipping.")
            stage_durations[source_name] = time.time() - stage_start
            continue

        try:
            result = processor(file_path)
        except Exception as exc:
            print(f"[{source_name}] Processor error: {exc}")
            stage_durations[source_name] = time.time() - stage_start
            continue

        documents = result if isinstance(result, list) else [result]
        accepted_count = 0

        for doc in documents:
            if not isinstance(doc, dict):
                print(f"[{source_name}] Ignored non-dict output.")
                continue

            if not run_quality_gate(doc):
                print(f"[{source_name}] Rejected by quality gate: {doc.get('document_id', 'unknown-id')}")
                continue

            try:
                validated = UnifiedDocument(**doc)
            except Exception as exc:
                print(
                    f"[{source_name}] Schema validation failed for "
                    f"{doc.get('document_id', 'unknown-id')}: {exc}"
                )
                continue

            final_kb.append(validated.model_dump(mode="json"))
            accepted_count += 1

        stage_durations[source_name] = time.time() - stage_start
        print(f"[{source_name}] Accepted {accepted_count}/{len(documents)} documents.")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_kb, f, ensure_ascii=False, indent=2)

    print("Stage timings (seconds):")
    for source_name, duration in stage_durations.items():
        print(f"  - {source_name}: {duration:.2f}")
    print(f"Output file: {output_path}")

    end_time = time.time()
    print(f"Pipeline finished in {end_time - start_time:.2f} seconds.")
    print(f"Total valid documents stored: {len(final_kb)}")


if __name__ == "__main__":
    main()
