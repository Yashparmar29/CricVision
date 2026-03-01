import os

template_dir = r"d:\CricVision\templates"

# Read original index.html
with open(os.path.join(template_dir, 'index.html'), 'r', encoding='utf-8') as f:
    orig_html = f.read()

import re

# Extract style
style_match = re.search(r'<style>(.*?)</style>', orig_html, re.DOTALL)
css = style_match.group(1) if style_match else ''

# Extract sections
# For index, we want the <section class="hero"> and <div class="live-dash">
# Features is <section id="features" class="section">
# Upload is <div class="upload-wrapper">

hero_match = re.search(r'(<section class="hero">.*?</section>)', orig_html, re.DOTALL)
hero_html = hero_match.group(1) if hero_match else ''

live_dash_match = re.search(r'(<div class="live-dash">.*?</div>\s*</div>)', orig_html, re.DOTALL)
live_dash_html = live_dash_match.group(1) if live_dash_match else ''
# Wait, the closing div for live-dash is tricky. It's inside <div class="container">
# Let's just manually slice or use simpler regex.
# <div class="live-dash"> ends before <section id="features"

features_match = re.search(r'(<section id="features" class="section">.*?</section>)', orig_html, re.DOTALL)
features_html = features_match.group(1) if features_match else ''

upload_match = re.search(r'(<div class="upload-wrapper">.*?</div>\s*</section>\s*</div>)', orig_html, re.DOTALL)
# Upload script
script_match = re.search(r'<script>(.*?)</script>', orig_html, re.DOTALL)
script_js = script_match.group(1) if script_match else ''

base_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}CricVision AI - Next-Gen Cricket Analytics{{% endblock %}}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
{css}
        /* New animations and forms */
        .fade-in {{ animation: fadeInPage 0.5s ease-out forwards; }}
        @keyframes fadeInPage {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        .auth-container {{ max-width: 450px; margin: 8rem auto 4rem; background: var(--bg-panel); backdrop-filter: blur(16px); padding: 3rem 2rem; border-radius: 20px; border: 1px solid var(--border-color); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); position: relative; overflow: hidden; }}
        .auth-container::before {{ content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 50%); z-index: 0; pointer-events: none; }}
        .auth-container > * {{ position: relative; z-index: 1; }}
        .auth-container h1 {{ text-align: center; margin-bottom: 2rem; font-size: 2.2rem; background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .auth-form {{ display: flex; flex-direction: column; gap: 1.5rem; }}
        .form-group {{ position: relative; }}
        .form-group input {{ width: 100%; padding: 1rem; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: var(--text-main); font-size: 1rem; transition: all 0.3s; box-sizing: border-box; }}
        .form-group input:focus {{ outline: none; border-color: var(--accent-primary); box-shadow: 0 0 15px var(--accent-glow); background: rgba(0,0,0,0.5); }}
        .auth-btn {{ padding: 1rem; background: linear-gradient(135deg, var(--accent-primary), #059669); color: white; border: none; border-radius: 12px; font-weight: 600; font-size: 1.1rem; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 15px var(--accent-glow); margin-top: 1rem; }}
        .auth-btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6); }}
        .auth-links {{ text-align: center; margin-top: 1.5rem; color: var(--text-muted); }}
        .auth-links a {{ color: var(--accent-primary); text-decoration: none; font-weight: 600; transition: color 0.3s; }}
        .auth-links a:hover {{ color: var(--accent-secondary); text-decoration: underline; }}
        .error-msg {{ background: rgba(239, 68, 68, 0.1); color: #fca5a5; padding: 1rem; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.2); margin-bottom: 1.5rem; text-align: center; font-weight: 500; }}
        
        .page-header {{ text-align: center; padding: 8rem 2rem 4rem; }}
        .page-header h1 {{ font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, var(--text-main), var(--text-muted)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .page-header p {{ color: var(--text-muted); font-size: 1.2rem; max-width: 600px; margin: 0 auto; }}
        
        main {{ min-height: 80vh; }}
    </style>
    {{% block extra_head %}}{{% endblock %}}
</head>
<body class="fade-in">
    <header>
        <div class="logo">
            <span>🏏</span> CricVision AI
        </div>
        <nav>
            <a href="{{{{ url_for('index') }}}}">Home</a>
            <a href="{{{{ url_for('features') }}}}">Features</a>
            {{% if logged_in %}}
            <a href="{{{{ url_for('dashboard') }}}}">Dashboard</a>
            <span style="color: var(--accent-primary);">Hi, {{{{ username }}}}</span>
            <a href="{{{{ url_for('logout') }}}}" class="nav-btn" style="background: rgba(255,255,255,0.1); box-shadow: none;">Logout</a>
            {{% else %}}
            <a href="{{{{ url_for('login') }}}}">Login</a>
            <a href="{{{{ url_for('signup') }}}}" class="nav-btn">Sign Up</a>
            {{% endif %}}
        </nav>
    </header>

    <main>
    {{% block content %}}{{% endblock %}}
    </main>

    <footer>
        <p>&copy; 2026 CricVision AI Platform. All rights reserved.</p>
    </footer>

    {{% block scripts %}}{{% endblock %}}
</body>
</html>
"""

# Let's extract live_dash manually safely
try:
    live_start = orig_html.index('<div class="live-dash">')
    live_end = orig_html.index('<section id="features"', live_start)
    live_dash_html = orig_html[live_start:live_end].strip()
except ValueError:
    live_dash_html = ''

try:
    upload_start = orig_html.index('<div class="upload-wrapper">')
    upload_end = orig_html.index('<footer>', upload_start)
    # The div structure closes before footer.
    # We will just grab everything up to </div>\n    </div> that closes container.
    # Actually, simpler:
    upload_end = orig_html.index('</div>\n\n    <footer>', upload_start)
    upload_html = orig_html[upload_start:upload_end].strip()
except ValueError:
    upload_html = ''

new_index = f"""{{% extends "base.html" %}}
{{% block content %}}
{hero_html}

<div class="container">
    {live_dash_html}
</div>
{{% endblock %}}
"""

new_features = f"""{{% extends "base.html" %}}
{{% block title %}}Features - CricVision AI{{% endblock %}}
{{% block content %}}
<div class="page-header">
    <h1>Platform Features</h1>
    <p>Discover the cutting-edge technology powering your cricket analysis</p>
</div>
<div class="container" style="margin-top: 2rem;">
    {features_html}
</div>
{{% endblock %}}
"""

new_dashboard = f"""{{% extends "base.html" %}}
{{% block title %}}Dashboard - CricVision AI{{% endblock %}}
{{% block content %}}
<div class="page-header">
    <h1>Analysis Dashboard</h1>
    <p>Upload your shot videos and get instant biomechanical feedback</p>
</div>

<div class="container" style="margin-top: 2rem;">
    {upload_html}
</div>
{{% endblock %}}

{{% block scripts %}}
<script>
{script_js}
</script>
{{% endblock %}}
"""

login_html = """{% extends "base.html" %}
{% block title %}Login - CricVision AI{% endblock %}
{% block content %}
<div class="auth-container">
    <h1>Welcome Back</h1>
    {% if error %}
    <div class="error-msg">{{ error }}</div>
    {% endif %}
    <form method="POST" class="auth-form">
        <div class="form-group">
            <input type="text" name="username" placeholder="Username" required autocomplete="off">
        </div>
        <div class="form-group">
            <input type="password" name="password" placeholder="Password" required autocomplete="off">
        </div>
        <button type="submit" class="auth-btn">Sign In to Dashboard</button>
    </form>
    <div class="auth-links">
        Don't have an account? <a href="{{ url_for('signup') }}">Create one here</a>
    </div>
</div>
{% endblock %}
"""

signup_html = """{% extends "base.html" %}
{% block title %}Sign Up - CricVision AI{% endblock %}
{% block content %}
<div class="auth-container">
    <h1>Join CricVision AI</h1>
    <form method="POST" class="auth-form">
        <div class="form-group">
            <input type="text" name="username" placeholder="Choose a Username" required autocomplete="off">
        </div>
        <div class="form-group">
            <input type="password" name="password" placeholder="Create a Password" required autocomplete="off">
        </div>
        <button type="submit" class="auth-btn">Create Account</button>
    </form>
    <div class="auth-links">
        Already have an account? <a href="{{ url_for('login') }}">Sign In</a>
    </div>
</div>
{% endblock %}
"""

with open(os.path.join(template_dir, 'base.html'), 'w', encoding='utf-8') as f:
    f.write(base_html)
with open(os.path.join(template_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(new_index)
with open(os.path.join(template_dir, 'features.html'), 'w', encoding='utf-8') as f:
    f.write(new_features)
with open(os.path.join(template_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(new_dashboard)
with open(os.path.join(template_dir, 'login.html'), 'w', encoding='utf-8') as f:
    f.write(login_html)
with open(os.path.join(template_dir, 'signup.html'), 'w', encoding='utf-8') as f:
    f.write(signup_html)
print("Templates updated successfully!")
