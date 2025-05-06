import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            if page_text.strip():
                text += page_text + "\n"
            else:
                # Tăng độ phân giải ảnh
                zoom_x = 3.0
                zoom_y = 3.0
                matrix = fitz.Matrix(zoom_x, zoom_y)
                pix = page.get_pixmap(matrix=matrix)

                # Chuyển thành mảng NumPy để xử lý với OpenCV
                img_data = pix.tobytes("ppm")
                pil_img = Image.open(io.BytesIO(img_data)).convert("L")
                np_img = np.array(pil_img)

                # Làm mịn và tăng độ tương phản với adaptive threshold
                blurred = cv2.GaussianBlur(np_img, (5, 5), 0)
                thresh = cv2.adaptiveThreshold(
                    blurred, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    11, 2
                )

                # Chuyển lại sang PIL để OCR
                processed_image = Image.fromarray(thresh)

                # Cấu hình OCR
                custom_config = r'--oem 3 --psm 4'  # layout theo đoạn văn
                ocr_text = pytesseract.image_to_string(
                    processed_image, lang='eng+vie', config=custom_config
                )
                text += ocr_text + "\n"
    return text.strip()
