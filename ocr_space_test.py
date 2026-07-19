import fitz  # PyMuPDF
import httpx

def main():
    # Load the BSCPE CMO PDF (scanned)
    pdf_path = "downloads/2017/CMO-87-s.-2017-BS-Computer-Engineering.pdf"
    print(f"Loading {pdf_path}...")
    doc = fitz.open(pdf_path)
    
    # Let's target page 18 (0-indexed: 17) where the BSCPE curriculum might start
    page_num = 17
    page = doc.load_page(page_num)
    print(f"Rendering page {page_num + 1} as PNG...")
    
    # Render page to high-res image (300 DPI for better OCR)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    png_data = pix.tobytes("png")
    
    print("Sending image to OCR.space free API using public 'helloworld' key...")
    
    url = "https://api.ocr.space/parse/image"
    files = {"file": ("page.png", png_data, "image/png")}
    data = {
        "apikey": "helloworld",
        "language": "eng",
        "isOverlayRequired": "false"
    }
    
    try:
        r = httpx.post(url, files=files, data=data, timeout=60.0)
        res = r.json()
        
        if res.get("OCRExitCode") == 1:
            print("\n--- OCR.space Successful Parse Results ---")
            parsed_text = res["ParsedResults"][0]["ParsedText"]
            print(parsed_text[:2000])
            print("\n------------------------------------------")
        else:
            print("OCR.space API Error:", res.get("ErrorMessage") or res)
    except Exception as e:
        print("Error calling OCR.space API:", e)

if __name__ == "__main__":
    main()
