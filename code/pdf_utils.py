import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Trích xuất text từ PDF và bỏ qua ảnh"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:  
                        text += page_text + "\n\n"
                except Exception as page_error:
                    print(f"Bỏ qua ảnh hoặc trang lỗi: {str(page_error)}")
                    continue
    except Exception as e:
        print(f"Lỗi đọc file PDF: {str(e)}")
    return text.strip() if text else "Không trích xuất được text từ file PDF"