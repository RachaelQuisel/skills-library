import sys
import os
import base64
import re
import requests
import json
import subprocess
import tempfile
import html

try:
    import markdown
except ImportError:
    print("Error: The 'markdown' library is required. Please install it with 'pip install markdown'.")
    sys.exit(1)

def render_mermaid_blocks(html_content):
    """Finds mermaid code blocks in the generated HTML and replaces them with base64 img tags."""
    # Pattern to match <pre><code class="language-mermaid">...</code></pre>
    mermaid_pattern = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL)
    
    # Path to the styles (self-contained within skill assets)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(os.path.dirname(script_dir), 'assets', 'mermaid_styles.css')
    
    # Ensure mmdc is available
    try:
        subprocess.run(['mmdc', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: mmdc (Mermaid CLI) not found. Mermaid diagrams will not be rendered.")
        return html_content

    def replace_with_png(match):
        # Unescape HTML entities that might have been added by the markdown parser
        mermaid_code = html.unescape(match.group(1)).strip()
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_mmd = os.path.join(tmp_dir, 'diagram.mmd')
            output_png = os.path.join(tmp_dir, 'diagram.png')
            
            with open(input_mmd, 'w') as f:
                f.write(mermaid_code)
            
            # Command to render mermaid as PNG
            cmd = [
                'mmdc',
                '-i', input_mmd,
                '-o', output_png,
                '-t', 'neutral',
                '-b', 'transparent',
                '--scale', '1.0' 
            ]
            
            # Add CSS if it exists
            if os.path.exists(css_path):
                cmd.extend(['-C', css_path])
            
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                
                with open(output_png, 'rb') as f:
                    png_data = f.read()
                    encoded_png = base64.b64encode(png_data).decode('utf-8')
                    # Return a styled div to center the image and add padding
                    return f'<p style="text-align: center; margin-top: 32pt; margin-bottom: 32pt; padding: 20pt; background-color: #ffffff; border: 1pt solid #e1ded8; border-radius: 18pt;"><img src="data:image/png;base64,{encoded_png}" alt="Mermaid Diagram" style="max-width: 100%;"></p>'
            except subprocess.CalledProcessError as e:
                print(f"Error rendering mermaid diagram: {e.stderr.decode()}")
                return match.group(0) 

    return mermaid_pattern.sub(replace_with_png, html_content)

def embed_images_as_base64(html_content, base_dir):
    """Finds image tags and replaces their src with base64 data URIs."""
    # Regex to find <img src="..."> tags
    img_tag_pattern = re.compile(r'<img\s+[^>]*src="([^"]+)"[^>]*>')
    
    def replace_with_base64(match):
        img_src = match.group(1)
        # Skip absolute URLs
        if img_src.startswith('http') or img_src.startswith('data:'):
            return match.group(0)
            
        # Try relative to MD file
        img_path = os.path.normpath(os.path.join(base_dir, img_src))
        
        # If not found, try relative to project root (current working directory)
        if not os.path.exists(img_path):
            img_path = os.path.normpath(os.path.join(os.getcwd(), img_src))

        if os.path.exists(img_path) and os.path.isfile(img_path):
            ext = os.path.splitext(img_path)[1].lower().replace('.', '')
            if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                with open(img_path, 'rb') as f:
                    encoded_string = base64.b64encode(f.read()).decode('utf-8')
                    mime_type = f'image/{ext}' if ext != 'svg' else 'image/svg+xml'
                    return match.group(0).replace(img_src, f'data:{mime_type};base64,{encoded_string}')
        
        return match.group(0)

    return img_tag_pattern.sub(replace_with_base64, html_content)

def inline_styles(html_content):
    """Injects inline styles for elements to ensure branding survives GDoc import."""
    # Definitions
    fonts_header = "'Urbanist', sans-serif"
    fonts_body = "'Figtree', sans-serif"
    gray_900 = "#0e1c2d"
    gray_600 = "#686f76"
    blue_500 = "#1566b9"

    style_map = {
        r'<h1>': f'<h1 style="font-family: {fonts_header}; font-size: 42pt; line-height: 1.15; color: {gray_900}; font-weight: 700; letter-spacing: -1pt; margin-top: 36pt; margin-bottom: 24pt;">',
        r'<h2>': f'<h2 style="font-family: {fonts_header}; font-size: 30pt; line-height: 1.2; color: {gray_900}; font-weight: 700; letter-spacing: -1pt; margin-top: 32pt; margin-bottom: 18pt;">',
        r'<h3>': f'<h3 style="font-family: {fonts_header}; font-size: 24pt; line-height: 1.2; color: {gray_900}; font-weight: 700; letter-spacing: -1pt; margin-top: 24pt; margin-bottom: 12pt;">',
        r'<h4>': f'<h4 style="font-family: {fonts_header}; font-size: 18pt; line-height: 1.2; color: {gray_900}; font-weight: 700; letter-spacing: -0.5pt; margin-top: 18pt; margin-bottom: 12pt;">',
        r'<h5>': f'<h5 style="font-family: {fonts_header}; font-size: 14pt; line-height: 1.2; color: {gray_900}; font-weight: 700; letter-spacing: -0.5pt; margin-top: 16pt; margin-bottom: 12pt;">',
        r'<p>': f'<p style="font-family: {fonts_body}; font-size: 12pt; line-height: 1.5; color: {gray_600}; letter-spacing: -0.5pt; margin-bottom: 16pt;">',
        r'<ul>': f'<ul style="font-family: {fonts_body}; color: {gray_600}; margin-bottom: 16pt; padding-left: 24pt;">',
        r'<ol>': f'<ol style="font-family: {fonts_body}; color: {gray_600}; margin-bottom: 16pt; padding-left: 24pt;">',
        r'<li>': f'<li style="margin-bottom: 8pt; font-size: 12pt;">',
        r'<a>': f'<a style="color: {blue_500}; text-decoration: none;">',
        r'<blockquote>': f'<blockquote style="border-left: 4pt solid {blue_500}; padding-left: 18pt; margin: 24pt 0; font-style: italic; color: {gray_900};">',
        r'<table>': f'<table style="width: 100%; border-collapse: collapse; margin: 24pt 0; font-family: {fonts_body};">',
        r'<th>': f'<th style="border: 1pt solid #e1ded8; padding: 12pt; text-align: left; background-color: #f8f8f8; color: {gray_900}; font-weight: 700;">',
        r'<td>': f'<td style="border: 1pt solid #e1ded8; padding: 12pt; text-align: left; color: {gray_600};">',
    }

    for tag, styled_tag in style_map.items():
        html_content = html_content.replace(tag, styled_tag)
    
    return html_content

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 convert_to_gdoc.py <input_md> <template_html>")
        sys.exit(1)

    input_md_path = sys.argv[1]
    template_path = sys.argv[2]
    
    # Base directory for relative image paths
    base_dir = os.path.dirname(os.path.abspath(input_md_path))

    if not os.path.exists(input_md_path):
        print(f"Error: Input file {input_md_path} not found.")
        sys.exit(1)

    with open(input_md_path, 'r') as f:
        md_content = f.read()

    # Standardize Markdown formatting before conversion
    try:
        import mdformat
        md_content = mdformat.text(md_content, extensions=["gfm"])
    except Exception as e:
        print(f"Warning: Could not format markdown before conversion: {e}")

    # Get title from first H1 or filename, then STRIP that H1 from the body.
    # Google Docs renders the documentName as its own title bar; leaving the H1
    # in the body causes the title to appear twice. The conversion endpoint reads
    # the title from `documentName` in the payload, not from the body HTML.
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # Remove the first occurrence of the H1 line (and a trailing newline if present).
        md_content = re.sub(r'^#\s+.+\n?', '', md_content, count=1, flags=re.MULTILINE)
    else:
        title = os.path.splitext(os.path.basename(input_md_path))[0]

    # Convert MD to HTML with extensions for tables and fenced code
    html_body = markdown.markdown(md_content, extensions=['fenced_code', 'tables', 'attr_list'])

    # Render Mermaid blocks to base64 images within the generated HTML
    html_body = render_mermaid_blocks(html_body)

    # Embed images from repo as Base64
    html_body = embed_images_as_base64(html_body, base_dir)

    # Inject inline styles for GDoc preservation
    html_body = inline_styles(html_body)

    # Read template
    if not os.path.exists(template_path):
        print(f"Error: Template file {template_path} not found.")
        sys.exit(1)
        
    with open(template_path, 'r') as f:
        template = f.read()

    # Inject title and content into template
    full_html = template.replace('{{title}}', title).replace('{{content}}', html_body)

    # Prepare payload
    payload = {
        "documentString": full_html,
        "documentName": title
    }

    # Send POST request
    url = "https://eo3nite61ktdbkn.m.pipedream.net"
    print(f"Sending payload for '{title}' to {url}...")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        # Output the response (expected to contain gdocURL)
        print(response.text)
        print("\n✅ Document successfully converted and uploaded!")
        print("💡 TIP: For the best display (especially for diagrams), switch the Google Doc to 'Pageless' mode: File > Page setup > Pageless.")
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
