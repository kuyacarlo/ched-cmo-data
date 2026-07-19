import os
import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

def main():
    # Configure local Tesseract path and tessdata prefix
    tesseract_bin = os.path.abspath("bin/tesseract")
    tessdata_dir = os.path.abspath("tessdata")
    
    pytesseract.pytesseract.tesseract_cmd = tesseract_bin
    os.environ["TESSDATA_PREFIX"] = tessdata_dir
    
    print(f"Using local Tesseract binary: {tesseract_bin}")
    print(f"Using TESSDATA_PREFIX: {tessdata_dir}")
    
    # Load the BSCPE CMO PDF (scanned)
    pdf_path = "downloads/2017/CMO-87-s.-2017-BS-Computer-Engineering.pdf"
    print(f"Loading {pdf_path}...")
    doc = fitz.open(pdf_path)
    
    # Target page 18 (0-indexed: 17) where the BSCPE curriculum might start
    page_num = 17
    page = doc.load_page(page_num)
    print(f"Rendering page {page_num + 1} as PNG...")
    
    # Render page to image
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    png_data = pix.tobytes("png")
    
    # Load into PIL Image for pytesseract
    img = Image.open(io.BytesIO(png_data))
    
    print("Performing local OCR using pytesseract...")
    try:
        text = pytesseract.image_to_string(img, lang="eng")
        print("\n--- Local Tesseract OCR Successful Parse Results ---")
        print(text[:2000])
        print("\n-----------------------------------------------------")
    except Exception as e:
        print("OCR Failed:", e)

if __name__ == "__main__":
    main()
