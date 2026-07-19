from pypdf import PdfReader

def main():
    pdf_path = "downloads/2021/CMO-No-25-series-2021-PSG-for-BS-Pharmacy.pdf"
    reader = PdfReader(pdf_path)
    print(f"Total Pages: {len(reader.pages)}")
    
    # We search for pages containing key words related to curriculum
    keywords = ["curriculum", "course outline", "program of study", "semester"]
    
    for page_num in range(len(reader.pages)):
        text = reader.pages[page_num].extract_text() or ""
        text_lower = text.lower()
        
        matches = [kw for kw in keywords if kw in text_lower]
        if len(matches) >= 2:
            print(f"\n--- Page {page_num + 1} matches keywords {matches} ---")
            # print first 600 characters of the page
            print(text[:600])

if __name__ == "__main__":
    main()
