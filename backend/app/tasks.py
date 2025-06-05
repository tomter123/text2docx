from celery import Celery
from docxtpl import DocxTemplate
from docx import Document  # <-- Add this import
import os
import markdown
from bs4 import BeautifulSoup

celery = Celery(
    "app.tasks",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

@celery.task
def convert_to_docx(input_path):
    ext = os.path.splitext(input_path)[1].lower()
    with open(input_path, 'r') as f:
        content = f.read()

    output_path = os.path.join("outputs", f"{os.path.basename(input_path)}.docx")

    if ext == '.md' or ext == '.html':
        template_path = "app/templates/default.docx"
        doc = DocxTemplate(template_path)
        if ext == '.md':
            html = markdown.markdown(content)
            soup = BeautifulSoup(html, 'html.parser')
            clean_html = str(soup)
            doc.render({'content': clean_html})
        else:  # HTML
            soup = BeautifulSoup(content, 'html.parser')
            clean_html = str(soup)
            doc.render({'content': clean_html})
        doc.save(output_path)
    elif ext == '.txt':
        # Use python-docx to create a new document and add each line as a paragraph
        doc = Document()
        for line in content.splitlines():
            doc.add_paragraph(line)
        doc.save(output_path)

    os.unlink(input_path)
    return output_path