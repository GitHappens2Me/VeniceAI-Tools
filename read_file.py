import ast
import json
import textwrap

def sanitize_code_from_file(filename: str) -> str:
    """Read, normalize and sanitize code from file for HTTP transmission"""
    with open(filename, 'r', encoding='utf-8') as file:
        code = file.read()
    
    try:
        parsed = ast.parse(code)
        cleaned = ast.unparse(parsed)
    except SyntaxError:
        cleaned = code  # Fallback for invalid syntax
    
    # Normalization pipeline
    cleaned = textwrap.dedent(cleaned)
    cleaned = cleaned.replace('\t', '    ')
    cleaned = '\n'.join(line.rstrip() for line in cleaned.split('\n'))
    
    return json.dumps(cleaned)[1:-1]  # Safe for JSON embedding