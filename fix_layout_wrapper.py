
import re

path = r'frontend/as_lp/app/layout.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace import
# It might involve dynamic from previous attempt, or standard import.
# I will assume I need to replace "const RateLimitNotification = dynamic(...)" block OR standard import.

# First, cleanup previous dynamic import if present
content = re.sub(r'const RateLimitNotification = dynamic\([^)]+\)\s*', '', content, flags=re.DOTALL)
content = re.sub(r'import dynamic from "next/dynamic"\s*', '', content)

# Add new import
new_import = 'import { ClientRateLimitNotification } from "@/components/ClientRateLimitNotification"'
if 'import { Toaster }' in content:
    content = content.replace('import { Toaster }', f'{new_import}\nimport {{ Toaster }}')
else:
    # Fallback append to imports
    content = new_import + '\n' + content

# Replace usage
content = content.replace('<RateLimitNotification />', '<ClientRateLimitNotification />')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated layout.tsx to use ClientRateLimitNotification")
