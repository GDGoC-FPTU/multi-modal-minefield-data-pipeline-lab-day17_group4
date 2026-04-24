import os
import json
import re
import time
from typing import Any, Dict, Optional

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _is_rate_limit_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "429" in message or "resourceexhausted" in message or "rate" in message


def extract_pdf_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY is missing. Skipping PDF extraction.")
        return None
        
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print(f"Uploading {file_path} to Gemini...")
    try:
        pdf_file = genai.upload_file(path=file_path)
    except Exception as e:
        print(f"Failed to upload file to Gemini: {e}")
        return None

    prompt = """
Analyze this PDF and return strict JSON only with this schema:
{
    "title": "string",
    "author": "string or null",
    "main_topics": ["topic1", "topic2"],
    "tables": [
        {
            "name": "string",
            "columns": ["col1", "col2"],
            "sample_rows": [["v1", "v2"]]
        }
    ]
}

Rules:
- No markdown fences.
- Use empty array if no table exists.
- Keep output valid JSON.
"""
    
    print("Generating content from PDF using Gemini...")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = model.generate_content([pdf_file, prompt])
            payload = _extract_json_block(response.text if response and response.text else "")
            if payload is None:
                raise ValueError("Gemini response is not valid JSON.")

            title = payload.get("title") or "Untitled PDF"
            author = payload.get("author") or "Unknown"
            main_topics = payload.get("main_topics") or []
            tables = payload.get("tables") or []

            summary = f"Title: {title}. Main topics: {', '.join(main_topics) if main_topics else 'N/A'}."
            return {
                "document_id": "pdf-doc-001",
                "content": summary,
                "source_type": "PDF",
                "author": author,
                "timestamp": None,
                "source_metadata": {
                    "original_file": os.path.basename(file_path),
                    "title": title,
                    "main_topics": main_topics,
                    "tables": tables,
                },
            }
        except Exception as exc:
            is_last_attempt = attempt == max_retries - 1
            if not _is_rate_limit_error(exc) or is_last_attempt:
                print(f"Failed to extract PDF data: {exc}")
                return None

            wait_seconds = 2 ** attempt
            print(f"Gemini rate limit hit. Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)

    return None
