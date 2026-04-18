import re

# REVERT SCRIPT.js
with open('static/script.js', 'r') as f:
    text = f.read()

# Remove the BOT_SVG and USER_SVG definitions
text = re.sub(r'const BOT_SVG = .*?;\n', '', text)
text = re.sub(r'const USER_SVG = .*?;\n', '', text)

# Revert Avatar renderings
text = re.sub(r'<div class="message-avatar">\$\{BOT_SVG\}</div>', '<div class="message-avatar">🧠</div>', text)
text = re.sub(r'<div class="message-avatar">\$\{USER_SVG\}</div>', '<div class="message-avatar">👤</div>', text)

# Remove Theme management logic at the bottom
theme_logic_pattern = r'// ── Theme Management ──────────.*'
text = re.sub(theme_logic_pattern, '', text, flags=re.DOTALL)

with open('static/script.js', 'w') as f:
    f.write(text.strip() + "\n")


# REVERT HTML FILES Theme toggle
html_files = ['templates/index.html', 'templates/login.html', 'templates/chat.html', 'templates/result.html']
for hf in html_files:
    with open(hf, 'r') as f:
        html = f.read()
    # Remove the themeToggle li
    html = re.sub(r'<li>\s*<button id="themeToggle"[\s\S]*?</button>\s*</li>\s*', '', html)
    with open(hf, 'w') as f:
        f.write(html)

print("Reverted scripts and HTML")
