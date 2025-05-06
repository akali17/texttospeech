import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + "\n"
                else:
                    # OCR nâng cao nếu không trích xuất được text
                    zoom_x = 3.0
                    zoom_y = 3.0
                    matrix = fitz.Matrix(zoom_x, zoom_y)
                    pix = page.get_pixmap(matrix=matrix)

                    img_data = pix.tobytes("ppm")
                    image = Image.open(io.BytesIO(img_data)).convert("L")

                    # Tiền xử lý ảnh
                    image = image.filter(ImageFilter.MedianFilter())
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(2)
                    image = image.point(lambda x: 0 if x < 128 else 255, '1')

                    custom_config = r'--oem 3 --psm 4'
                    ocr_text = pytesseract.image_to_string(image, lang='eng+vie', config=custom_config)
                    text += ocr_text + "\n"
    except Exception as e:
        print(f"Lỗi đọc file PDF: {str(e)}")
    return text.strip() if text else "Không trích xuất được text từ file PDF"
