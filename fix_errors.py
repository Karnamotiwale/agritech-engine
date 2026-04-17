import os
import re

TARGET_DIR = "api"

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Broad regex to catch all jsonify({"error": str(e)}) or {"success": False, "error": str(e)}
    # We want to replace str(e) with "An internal error occurred" when it's assigned to "error" or "message" in a dict
    new_content = re.sub(r'(["\']error["\']\s*:\s*)str\(e\)', r'\1"An internal error occurred"', content)
    new_content = re.sub(r'(["\']message["\']\s*:\s*)str\(e\)', r'\1"An internal error occurred"', new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

for root, _, files in os.walk(TARGET_DIR):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))

print("Done.")
