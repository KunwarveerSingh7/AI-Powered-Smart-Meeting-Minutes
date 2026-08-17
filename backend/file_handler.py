# Source 1
# https://pypdf.readthedocs.io/en/6.12.0/user/extract-text.html
# extract text from pdf file
# Source 2 & 3
# https://www.w3schools.com/python/python_file_open.asp , https://www.geeksforgeeks.org/python/reading-writing-text-files-python
# extract text from .txt
# Source 4 & 5
# https://www.geeksforgeeks.org/python/python-working-with-docx-module/ , https://etienned.github.io/posts/extract-text-from-word-docx-simply/
# how to extract text from docx



from pathlib import Path

# document comes python-docx package
# this helps pyhton read the .docx file
from docx import Document
# this comes from pypdf package
#helps read the pdf file
from pypdf import PdfReader

# Text File Extraction
#open the file and returns its contents
def extract_txt(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()

# docx file extraction
# open the doc and go through each para
def extract_docx(file_path):
    document = Document(file_path)
    #store the extracted para's here
    text_parts = []
    #if para is empty not needed, only add para with text
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text)
    #join and return all para as one doc
    return "\n".join(text_parts)

# pdf file extraction
# read pdf each page at a time
def extract_pdf(file_path):
    reader = PdfReader(file_path)
    #store text from each page
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        #some pdf might not have readable text
        if page_text:
            text_parts.append(page_text)
    #combine all pages to one
    return "\n".join(text_parts)

# extraction function decider
# this would choose which extraction path to choose based on the file

def extract_text(file_path):
    # get the file extension
    extension = Path(file_path).suffix.lower()

    if extension == ".txt":
        return extract_txt(file_path)

    if extension == ".docx":
        return extract_docx(file_path)

    if extension == ".pdf":
        return extract_pdf(file_path)
    #if the uploaded file is not of the supported format, stop and send error message
    raise ValueError(
        "Unsupported meeting file type"
    )
