import os
import docx

def extract_text_from_pdf(file_path):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        print(f"📄 PDF extracted {len(text)} characters")
        return text
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        print(f"📄 DOCX extracted {len(text)} characters")
        return text
    except Exception as e:
        print(f"❌ DOCX extraction error: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"📄 TXT extracted {len(text)} characters")
        return text
    except Exception as e:
        print(f"❌ TXT extraction error: {e}")
        return ""

def extract_text(file_path):
    print(f"🔍 Extracting text from: {file_path}")
    
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        print(f"❌ Unsupported file type: {file_path}")
        return ""