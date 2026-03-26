#!/usr/bin/env python
"""Validate master_attractions_clean.py structure"""

import ast
import sys

def validate_file(filepath):
    """Validate Python file syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # Try to parse it
        ast.parse(source)
        print("✓ File is syntactically valid")
        return True

    except SyntaxError as e:
        print(f"✗ Syntax Error:")
        print(f"  Line {e.lineno}: {e.msg}")
        if e.text:
            print(f"  Code: {e.text.strip()}")
        return False

if __name__ == "__main__":
    filepath = "data/master_attractions_clean.py"
    if validate_file(filepath):
        sys.exit(0)
    else:
        sys.exit(1)
