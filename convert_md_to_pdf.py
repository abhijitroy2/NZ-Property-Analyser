"""
Convert Markdown file to PDF
"""
import sys
import os

try:
    from markdown import markdown
    from weasyprint import HTML, CSS
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "weasyprint"])
    from markdown import markdown
    from weasyprint import HTML, CSS


def convert_md_to_pdf(md_file: str, pdf_file: str):
    """
    Convert Markdown file to PDF.
    
    Args:
        md_file: Path to input Markdown file
        pdf_file: Path to output PDF file
    """
    try:
        # Read markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown(md_content, extensions=['extra', 'codehilite'])
        
        # Add CSS styling
        html_with_style = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    border-bottom: 2px solid #95a5a6;
                    padding-bottom: 5px;
                    margin-top: 30px;
                }}
                h3 {{
                    color: #7f8c8d;
                    margin-top: 20px;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 5px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        HTML(string=html_with_style).write_pdf(pdf_file)
        
        print(f"PDF created successfully: {pdf_file}")
        return True
        
    except Exception as e:
        print(f"Error converting MD to PDF: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    pdf_file = sys.argv[2]
    
    if not os.path.exists(md_file):
        print(f"Error: Markdown file not found: {md_file}")
        sys.exit(1)
    
    success = convert_md_to_pdf(md_file, pdf_file)
    sys.exit(0 if success else 1)

