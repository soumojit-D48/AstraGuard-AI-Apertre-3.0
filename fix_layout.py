
import re

path = r'frontend/as_lp/app/layout.tsx'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
found = False
for line in lines:
    if 'import' in line and 'RateLimitNotification' in line:
        new_lines.append('import dynamic from "next/dynamic"\n')
        new_lines.append('\n')
        new_lines.append('const RateLimitNotification = dynamic(\n')
        new_lines.append('  () => import("@/components/rate-limit-notification").then((mod) => mod.RateLimitNotification),\n')
        new_lines.append('  { ssr: false }\n')
        new_lines.append(')\n')
        found = True
        print(f"Replaced line: {line.strip()}")
    else:
        new_lines.append(line)

if found:
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Fixed layout.tsx")
else:
    print("Target import not found in layout.tsx")
