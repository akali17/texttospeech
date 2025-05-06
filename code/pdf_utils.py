import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Thử trích xuất text bình thường trước
            page_text = page.get_text()
            if page_text.strip():
                text += page_text + "\n"
            else:
                # Nếu không có text, thực hiện OCR nâng cao
                zoom_x = 2.0  # Phóng to theo chiều ngang
                zoom_y = 2.0  # Phóng to theo chiều dọc
                matrix = fitz.Matrix(zoom_x, zoom_y)
                pix = page.get_pixmap(matrix=matrix)

                img_data = pix.tobytes("ppm")
                image = Image.open(io.BytesIO(img_data)).convert("L")  # Chuyển ảnh sang grayscale

                custom_config = r'--oem 3 --psm 6'  # Cấu hình Tesseract
                ocr_text = pytesseract.image_to_string(image, lang='eng+vie', config=custom_config)
                text += ocr_text + "\n"
    return text
