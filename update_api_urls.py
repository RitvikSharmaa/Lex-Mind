#!/usr/bin/env python3
"""
Script to update API URLs in frontend to use environment variable
"""

import re

# Read the App.tsx file
with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import for config at the top (after other imports)
if 'import { API_URL }' not in content:
    # Find the last import statement
    import_pattern = r"(import.*?;)\n\nfunction App"
    content = re.sub(
        import_pattern,
        r"\1\nimport { API_URL } from './config';\n\nfunction App",
        content
    )

# Replace all hardcoded localhost:5000 URLs with API_URL
replacements = [
    (r"'http://localhost:5000/api/", r"`${API_URL}/api/"),
    (r'"http://localhost:5000/api/', r'`${API_URL}/api/'),
]

for old, new in replacements:
    content = re.sub(old, new, content)

# Write back
with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated App.tsx to use API_URL from config")
print("📝 Next steps:")
print("1. Edit frontend/.env.production with your Railway URL")
print("2. Run: cd frontend && npm run build && vercel --prod")
