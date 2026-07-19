import csv
import json
import os
from pathlib import Path
from pypdf import PdfReader

def scan_file(path: Path) -> dict:
    try:
        file_size = os.path.getsize(path)
        reader = PdfReader(path)
        page_count = len(reader.pages)
        
        # Extract text from the first 3 pages to check if it's searchable
        text_sample = ""
        pages_to_check = min(3, page_count)
        for i in range(pages_to_check):
            try:
                page_text = reader.pages[i].extract_text() or ""
                text_sample += page_text
            except Exception:
                pass
                
        # If total characters extracted across sample pages is very low, it needs OCR
        is_ocr_needed = len(text_sample.strip()) < 100
        
        return {
            "file_size_bytes": file_size,
            "page_count": page_count,
            "is_ocr_needed": is_ocr_needed,
            "is_corrupted": False,
            "status": "downloaded"
        }
    except Exception as e:
        print(f"Error scanning {path.name}: {e}")
        return {
            "file_size_bytes": os.path.getsize(path) if path.exists() else None,
            "page_count": None,
            "is_ocr_needed": None,
            "is_corrupted": True,
            "status": "corrupted"
        }

def main():
    csv_path = Path("out.csv")
    jsonl_path = Path("out.jsonl")
    download_dir = Path("downloads")
    
    if not csv_path.exists():
        print("Error: out.csv not found.")
        return
        
    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
            
    print(f"Scanning downloaded files for {len(records)} entries...")
    
    updated_records = []
    scanned_count = 0
    ocr_count = 0
    searchable_count = 0
    corrupt_count = 0
    not_downloaded_count = 0
    
    for r in records:
        url = r["url"]
        year = r["year"]
        filename = url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"
            
        file_path = download_dir / str(year) / filename
        
        # Default empty fields
        file_size_bytes = None
        page_count = None
        is_ocr_needed = None
        is_corrupted = None
        status = "not_downloaded"
        
        if file_path.exists():
            scan_res = scan_file(file_path)
            file_size_bytes = scan_res["file_size_bytes"]
            page_count = scan_res["page_count"]
            is_ocr_needed = scan_res["is_ocr_needed"]
            is_corrupted = scan_res["is_corrupted"]
            status = scan_res["status"]
            
            scanned_count += 1
            if is_corrupted:
                corrupt_count += 1
            elif is_ocr_needed:
                ocr_count += 1
            else:
                searchable_count += 1
        else:
            not_downloaded_count += 1
            
        updated_records.append({
            "year": r["year"],
            "cmo_no": r["cmo_no"],
            "cmo_reference": r["cmo_reference"],
            "title": r["title"],
            "category": r["category"],
            "url": r["url"],
            "file_size_bytes": file_size_bytes,
            "page_count": page_count,
            "is_ocr_needed": is_ocr_needed,
            "is_corrupted": is_corrupted,
            "status": status
        })
        
    # Write to CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "year", "cmo_no", "cmo_reference", "title", "category", "url",
            "file_size_bytes", "page_count", "is_ocr_needed", "is_corrupted", "status"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_records)
        
    # Write to JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in updated_records:
            f.write(json.dumps(r) + "\n")
            
    print("\n--- Scan Summary ---")
    print(f"Total entries: {len(records)}")
    print(f"Downloaded and scanned: {scanned_count}")
    print(f"  - Searchable (Text copyable): {searchable_count}")
    print(f"  - Scanned (Needs OCR): {ocr_count}")
    print(f"  - Corrupt or invalid PDFs: {corrupt_count}")
    print(f"Not downloaded: {not_downloaded_count}")
    print("--------------------")

if __name__ == "__main__":
    main()
