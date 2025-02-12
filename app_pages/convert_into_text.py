from app_pages.extract_docx_pdf_txt import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt

def convert(file):
    if file is not None:
        if file.type == "application/pdf":
            file = extract_text_from_pdf(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file = extract_text_from_docx(file)
        elif file.type == "text/plain":
            file = extract_text_from_txt(file)
    return file