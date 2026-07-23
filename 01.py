import os
import json
import csv
import httpx
import asyncio
import re
from bs4 import BeautifulSoup
from pathlib import Path

YEARS = range(2000, 2027)
OUTPUT_JSONL = Path("out.jsonl")
OUTPUT_CSV = Path("out.csv")

from classify import classify_category, extract_cmo_no


def parse_link_text(text: str, year: int) -> tuple[str, str]:
    parts = re.split(r'[–-]', text, maxsplit=1)
    if len(parts) == 2:
        ref_part, title_part = parts[0].strip(), parts[1].strip()
    else:
        ref_part, title_part = text.strip(), text.strip()
        
    if ref_part.upper().startswith("CMO"):
        cmo_reference = ref_part
    else:
        match = re.search(r'(CMO\s*(?:No\.?|NO\.?)?\s*\d+(?:,\s*series\s*of\s*\d+)?)', text, re.IGNORECASE)
        if match:
            cmo_reference = match.group(1)
            title_part = text.replace(cmo_reference, "").strip(" –-")
        else:
            cmo_reference = f"CMO {year} (unreferenced)"
            title_part = text
            
    return cmo_reference, title_part

async def fetch_year_cmos(client: httpx.AsyncClient, year: int) -> list[dict]:
    url = f"https://legacy.ched.gov.ph/{year}-ched-memorandum-orders/"
    print(f"Requesting page for year {year} via legacy domain...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        response = await client.get(url, headers=headers, timeout=30.0)
        if response.status_code != 200:
            print(f"  Failed: HTTP {response.status_code} for {url}")
            return []
            
        soup = BeautifulSoup(response.content, "html.parser")
        cmos = []
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if ".pdf" in href.lower() and ("cmo" in href.lower() or "cmo" in text.lower()):
                cmo_ref, title = parse_link_text(text, year)
                cmo_no = extract_cmo_no(cmo_ref)
                category = classify_category(title, cmo_ref)
                cmos.append({
                    "year": year,
                    "cmo_no": cmo_no,
                    "cmo_reference": cmo_ref,
                    "title": title,
                    "category": category,
                    "url": href
                })
        
        return cmos
        
    except Exception as e:
        print(f"  Error fetching year {year}: {e}")
        return []

async def main():
    all_cmos = []
    
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(limits=limits) as client:
        for year in YEARS:
            cmos = await fetch_year_cmos(client, year)
            print(f"  Found {len(cmos)} CMOs for {year}.")
            all_cmos.extend(cmos)
            await asyncio.sleep(1)
            
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for c in all_cmos:
            f.write(json.dumps(c) + "\n")
            
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["year", "cmo_no", "cmo_reference", "title", "category", "url"])
        writer.writeheader()
        writer.writerows(all_cmos)
        
    print(f"Housekeeping complete: processed {len(all_cmos)} entries.")
    print(f"Outputs saved to {OUTPUT_JSONL} and {OUTPUT_CSV}")

if __name__ == "__main__":
    asyncio.run(main())
