import os
import re

html_dir = r"c:\Users\AK\Documents\infosys internship\Insight Extractor\templates"
js_file = r"c:\Users\AK\Documents\infosys internship\Insight Extractor\static\js\main.js"

replacements = [
    (r'\bindigo-', 'emerald-'),
    (r'\bpurple-', 'cyan-'),
    (r'\bfrom-indigo-', 'from-emerald-'),
    (r'\bto-purple-', 'to-cyan-'),
    (r'rgba\(79, 70, 229', 'rgba(16, 185, 129') # Indigo HEX mapping to Emerald for the Tret Widget shadow
]

def apply_replacements(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    for old, new in replacements:
        content = re.sub(old, new, content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Process all HTML files
for file in os.listdir(html_dir):
    if file.endswith(".html"):
        apply_replacements(os.path.join(html_dir, file))

# Process main.js (contains some dynamic tailwind class strings)
apply_replacements(js_file)

print("Color swap complete!")
