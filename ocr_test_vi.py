import pytesseract
from PIL import Image
import os

os.environ["TESSDATA_PREFIX"] = r'D:\All Code\New folder\RAG_CSDL\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\ADMIN\scoop\shims\tesseract.exe'

try:
    text = pytesseract.image_to_string(Image.open('screenshot_4_after_send.png'), lang='vie')
    with open('ocr_proof_utf8.txt', 'w', encoding='utf-8') as f:
        f.write("OCR SUCCESS!\n--- TEXT ---\n")
        f.write(text)
except Exception as e:
    with open('ocr_proof_utf8.txt', 'w', encoding='utf-8') as f:
        f.write("OCR ERROR: " + str(e))
