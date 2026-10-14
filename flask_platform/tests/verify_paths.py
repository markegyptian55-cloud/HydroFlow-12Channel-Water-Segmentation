import os
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check all src and href links pointing to flask_platform
matches = re.findall(r'(?:href|src)=["\'](\./flask_platform/[^"\'?]+)', content)
missing = []
for m in matches:
    clean_path = m.lstrip('./').replace('/', os.sep)
    if not os.path.exists(clean_path):
        missing.append(clean_path)

print(f"Total flask_platform links found: {len(matches)}")
print(f"Missing files: {missing}")
assert len(missing) == 0, f"Some files were not found: {missing}"
print("ALL PATHS VERIFIED 100% OK!")
