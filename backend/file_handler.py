from pathlib import Path

# document comes python-docx package
# this helps pyhton read the .docx file
from docx import Document
# this comes from pypdf package
#helps read the pdf file
from pypdf import PdfReader

# Text File Extraction

def extract_txt(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()

# docx file extraction

def extract_docx(file_path):
    document = Document(file_path)

    text_parts = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text)

    return "\n".join(text_parts)

# pdf file extraction

def extract_pdf(file_path):
    reader = PdfReader(file_path)

    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts)


# this would choose which extraction path to choose based on the file

def extract_text(file_path):
    extension = Path(file_path).suffix.lower()

    if extension == ".txt":
        return extract_txt(file_path)

    if extension == ".docx":
        return extract_docx(file_path)

    if extension == ".pdf":
        return extract_pdf(file_path)

    raise ValueError(
        "Unsupported meeting file type"
    )
