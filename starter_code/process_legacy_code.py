import ast
import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.

def extract_logic_from_code(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    # ------------------------------------------
    
    tree = ast.parse(source_code)
    module_docstring = ast.get_docstring(tree)

    function_docstrings = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            function_docstrings[node.name] = ast.get_docstring(node)

    comment_rule_lines = re.findall(r"#\s*(?:Business Logic Rule\s*\d+.*|WARNING:.*)", source_code)

    discrepancies = []
    if re.search(r"8%", source_code) and re.search(r"0\.10", source_code):
        discrepancies.append("Comment mentions 8% but implemented tax_rate is 10%.")

    key_rules = []
    for name, doc in function_docstrings.items():
        if doc:
            key_rules.append(f"{name}: {doc.strip()}")

    content_parts = []
    if module_docstring:
        content_parts.append(module_docstring.strip())
    content_parts.extend(key_rules)

    return {
        "document_id": "legacy-code-001",
        "content": "\n\n".join(content_parts)[:4000],
        "source_type": "Code",
        "author": "Senior Dev (retired)",
        "timestamp": None,
        "source_metadata": {
            "function_docstrings": function_docstrings,
            "comment_rules": comment_rule_lines,
            "discrepancies": discrepancies,
        },
    }

