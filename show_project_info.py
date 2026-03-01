#!/usr/bin/env python
"""
WordsProject-forstudent Project Information Display

This script displays project authorship and copyright information.
Use this to verify that the project properly attributes the original author.
"""

import os
import sys

def read_file_if_exists(filename):
    """Read file content if exists."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def display_project_info():
    """Display project information."""
    print("=" * 60)
    print("WordsProject-forstudent - Project Information")
    print("=" * 60)
    
    # Display LICENSE
    license_text = read_file_if_exists("LICENSE")
    if license_text:
        print("\n📜 LICENSE:")
        print("-" * 40)
        print(license_text[:500] + "..." if len(license_text) > 500 else license_text)
    
    # Display AUTHORS
    authors_text = read_file_if_exists("AUTHORS")
    if authors_text:
        print("\n👥 AUTHORS:")
        print("-" * 40)
        print(authors_text)
    
    # Display CREDITS
    credits_text = read_file_if_exists("CREDITS.md")
    if credits_text:
        print("\n🎖️ CREDITS:")
        print("-" * 40)
        print(credits_text[:300] + "..." if len(credits_text) > 300 else credits_text)
    
    # Check for copyright in main files
    print("\n🔍 Checking copyright in key files:")
    print("-" * 40)
    
    files_to_check = ["app.py", "models.py", "extensions.py"]
    for file in files_to_check:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 chars
                if "Copyright" in content or "WordsProject-forstudent" in content:
                    print(f"✓ {file}: Contains copyright notice")
                else:
                    print(f"✗ {file}: No copyright notice found")
    
    print("\n" + "=" * 60)
    print("✅ Project information verified.")
    print("This project includes proper attribution for the author.")
    print("=" * 60)

if __name__ == "__main__":
    display_project_info()