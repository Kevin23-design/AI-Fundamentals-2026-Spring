import sys
pdf_path = r"f:\code\AI_Fundamentals\Assignments\Assignment2\Assignment2.pdf"

def read_pdf():
    try:
        import fitz
        doc = fitz.open(pdf_path)
        for page in doc:
            print(page.get_text())
        return
    except ImportError:
        pass

    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            print(page.extract_text())
        return
    except ImportError:
        pass
        
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        for page in reader.pages:
            print(page.extract_text())
        return
    except ImportError:
        print("No PDF module found")

read_pdf()
