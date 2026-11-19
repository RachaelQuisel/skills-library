import sys
import os
import argparse
import subprocess
import mdformat
from pymarkdown.main import PyMarkdownLint

def format_markdown(file_path):
    """Formats the markdown file using mdformat with GFM support."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Format the content
        formatted_content = mdformat.text(content, extensions=["gfm"])
        
        # Write back if changed
        if content != formatted_content:
            with open(file_path, 'w') as f:
                f.write(formatted_content)
            print(f"✅ Formatted {file_path}")
        else:
            print(f"ℹ️ {file_path} is already well-formatted")
            
    except Exception as e:
        print(f"❌ Error formatting {file_path}: {e}")
        return False
    return True

def lint_markdown(file_path):
    """Lints the markdown file using pymarkdownlnt."""
    print(f"🔍 Linting {file_path}...")
    try:
        # We use the CLI-like interface of PyMarkdownLint
        # 'scan' command followed by the file path
        linter = PyMarkdownLint()
        # direct_args=['scan', file_path] mimics 'pymarkdown scan file.md'
        # We disable MD013 (line-length) by default as it's often too restrictive
        linter.main(direct_args=['-d', 'MD013', 'scan', file_path])
    except SystemExit as e:
        if e.code == 0:
            print(f"✅ No linting issues found in {file_path}")
            return True
        else:
            print(f"⚠️ Linting issues found in {file_path} (Exit code: {e.code})")
            return False
    except Exception as e:
        print(f"❌ Error linting {file_path}: {e}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Format and lint Markdown files.")
    parser.add_argument("files", nargs="+", help="Markdown files to process")
    parser.add_argument("--check-only", action="store_true", help="Only check formatting without applying changes")
    
    args = parser.parse_args()
    
    success = True
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            success = False
            continue
            
        if not args.check_only:
            if not format_markdown(file_path):
                success = False
        
        if not lint_markdown(file_path):
            success = False
            
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
