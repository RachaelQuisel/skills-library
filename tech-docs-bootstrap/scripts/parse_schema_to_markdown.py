#!/usr/bin/env python3
import os
import sys
import re

def parse_prisma(file_path):
    output = []
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Very basic regex to grab model blocks
    models = re.findall(r'model\s+(\w+)\s+{([^}]+)}', content)
    for model_name, fields_block in models:
        output.append(f"### Model: {model_name}\n")
        lines = fields_block.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('@@') and not line.startswith('//'):
                parts = line.split()
                if len(parts) >= 2:
                    field_name, field_type = parts[0], parts[1]
                    output.append(f"- **{field_name}**: `{field_type}`")
        output.append("\n")
    return "\n".join(output)

def parse_sql(file_path):
    output = []
    with open(file_path, 'r') as f:
        content = f.read()
        
    tables = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[\'"]?\w+[\'"]?\.)?[\'"]?(\w+)[\'"]?\s*\((.*?)\);', content, re.IGNORECASE | re.DOTALL)
    for table_name, fields_block in tables:
        output.append(f"### Table: {table_name}\n")
        lines = fields_block.strip().split('\n')
        for line in lines:
            line = line.strip().strip(',')
            if line and not line.upper().startswith('PRIMARY KEY') and not line.upper().startswith('FOREIGN KEY') and not line.upper().startswith('CONSTRAINT'):
                parts = line.split()
                if len(parts) >= 2:
                    field_name, field_type = parts[0], parts[1]
                    output.append(f"- **{field_name}**: `{field_type}`")
        output.append("\n")
    return "\n".join(output)

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    found_schemas = False
    
    for root, dirs, files in os.walk(target_dir):
        if "node_modules" in root or ".git" in root:
            continue
            
        for file in files:
            path = os.path.join(root, file)
            if file.endswith('.prisma'):
                print(f"## Prisma Schema: {file}\n")
                print(parse_prisma(path))
                found_schemas = True
            elif file.endswith('.sql') and 'migration' not in path.lower():
                print(f"## SQL Schema: {file}\n")
                print(parse_sql(path))
                found_schemas = True

    if not found_schemas:
        print("No Prisma or SQL schemas found to parse automatically. Manual inspection required.")

if __name__ == "__main__":
    main()
