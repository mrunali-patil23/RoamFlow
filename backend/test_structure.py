#!/usr/bin/env python3
"""
Simple test to verify the backend structure is correct
"""

import sys
from pathlib import Path

def test_structure():
    """Test that all required files and directories exist"""
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.example",
        "app/__init__.py",
        "app/models/__init__.py",
        "app/services/__init__.py",
        "app/api/__init__.py",
        "tests/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ All required backend files exist")
        return True

def test_imports():
    """Test that main.py can be imported (basic syntax check)"""
    try:
        import ast
        with open("main.py", "r") as f:
            content = f.read()
        ast.parse(content)
        print("✅ main.py syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in main.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking main.py: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend structure...")
    
    structure_ok = test_structure()
    syntax_ok = test_imports()
    
    if structure_ok and syntax_ok:
        print("\n✅ Backend structure is ready!")
        sys.exit(0)
    else:
        print("\n❌ Backend structure has issues")
        sys.exit(1)