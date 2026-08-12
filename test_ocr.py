import os
import pytesseract
import pdf2image

PDF_FILE = r'D:\All Code\New folder\test data\2025_2026_HK1_DE THI GIUA KY_CSDL_DE01.pdf'
POPPLER_PATH = r'D:\All Code\New folder\RAG_CSDL\poppler\poppler-24.07.0\Library\bin'
TESSERACT_CMD = r'C:\Users\ADMIN\scoop\shims\tesseract.exe'
TESSDATA_PREFIX = r'D:\All Code\New folder\RAG_CSDL\tessdata'

def main():
    print("Testing OCR on PDF...")
    
    if not os.path.exists(PDF_FILE):
        print(f"Error: PDF not found at {PDF_FILE}")
        return

    os.environ['TESSDATA_PREFIX'] = TESSDATA_PREFIX
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    
    print(f"Using Tesseract: {TESSERACT_CMD}")
    print(f"Using Tessdata: {TESSDATA_PREFIX}")
    
    images = pdf2image.convert_from_path(PDF_FILE, poppler_path=POPPLER_PATH, first_page=1, last_page=1)
    if not images:
        print("No images extracted from PDF.")
        return
        
    img = images[0]
    print("Extracting text from page 1...")
    text = pytesseract.image_to_string(img, lang='vie')
    
    print("\n--- OCR TEXT START ---")
    with open("ocr_test_result.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("--- OCR TEXT END ---")

if __name__ == '__main__':
    main()
