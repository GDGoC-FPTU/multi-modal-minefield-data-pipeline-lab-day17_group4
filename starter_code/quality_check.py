# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

import re


TOXIC_ERROR_PATTERNS = [
    "null pointer exception",
    "traceback",
    "fatal error",
    "segmentation fault",
    "syntax error",
]

def run_quality_gate(document_dict):
    """Return True when the document passes all quality checks, else False."""
    if not isinstance(document_dict, dict):
        return False

    # 1) Basic content-length gate.
    content = str(document_dict.get("content", "")).strip()
    if len(content) < 20:
        return False

    # 2) Toxic/error marker gate over the whole document text.
    haystack = " ".join(str(value) for value in document_dict.values()).lower()
    if any(pattern in haystack for pattern in TOXIC_ERROR_PATTERNS):
        return False

    # 3) Tax-rate discrepancy gate between comments and code snippets.
    comments_text = " ".join(
        str(value)
        for key, value in document_dict.items()
        if "comment" in str(key).lower()
    )
    code_text = " ".join(
        str(value)
        for key, value in document_dict.items()
        if "code" in str(key).lower()
    )

    if "tax" in comments_text.lower() and "tax" in code_text.lower():
        comment_rates = set(re.findall(r"(\d+(?:\.\d+)?)\s*%", comments_text.lower()))
        code_rates = set(re.findall(r"(\d+(?:\.\d+)?)\s*%", code_text.lower()))
        if comment_rates and code_rates and comment_rates != code_rates:
            return False

    return True
