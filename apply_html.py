import os
import re

html_dir = r"c:\Users\AK\Documents\infosys internship\Insight Extractor\templates"
files = ["index.html", "dashboard.html", "analysis.html", "about.html", "contact.html"]

class_to_add = "slide-in-left "

for file in files:
    path = os.path.join(html_dir, file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply body animation class if not there
    if "<body class=\"" in content and class_to_add not in content:
        content = content.replace("<body class=\"", f"<body class=\"{class_to_add}")
        
    # Remove existing <nav> to </nav> and replace with {% include 'navbar.html' %}
    # Use re.sub to match across newlines lazily
    content = re.sub(r'<nav.*?</nav>', "{% include 'navbar.html' %}", content, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Patching complete!")
