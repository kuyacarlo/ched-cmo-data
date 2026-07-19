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

def extract_cmo_no(cmo_ref: str) -> str:
    match = re.search(r'\b(?:No|NO)\.?\s*(\d+)', cmo_ref, re.IGNORECASE)
    if match:
        return str(int(match.group(1)))
    match2 = re.search(r'\b(\d+)\b', cmo_ref)
    if match2:
        return str(int(match2.group(1)))
    return ""

def classify_category(title: str, cmo_ref: str) -> str:
    title_upper = title.upper()
    ref_upper = cmo_ref.upper()
    combined = f"{title_upper} {ref_upper}"
    
    if any(k in combined for k in [
        "POLICIES, STANDARDS AND GUIDELINES", "POLICIES, STANDARDS, AND GUIDELINES", 
        "PSG FOR", "BACHELOR OF", "BACHELOR IN", "DOCTOR OF", "MASTER OF", "MASTER IN",
        "DEGREE PROGRAM", "UNDERGRADUATE PROGRAM", "GRADUATE PROGRAM", "CURRICULA FOR", 
        "INTEGRATION OF PEACE STUDIES", "INDIGENOUS PEOPLES STUDIES", "VETERINARY MEDICINE"
    ]) or re.search(r'\b(?:BS|BA|MS|MA|PHD|MD|DMD|DVM|PSG)\b', combined):
        if not any(k in title_upper for k in ["COMMON TO ALL", "ADMISSION OF"]):
            return "curriculum_program"
            
    if any(k in combined for k in [
        "HIGHER EDUCATION INSTITUTION", "HEI", "STATE UNIVERSITIES AND COLLEGES", "SUC", 
        "LOCAL COLLEGES AND UNIVERSITIES", "LCU", "AUTONOMOUS AND DEREGULATED", 
        "PRIVATE HIGHER EDUCATION", "COES CODS", "CENTERS OF EXCELLENCE", "CENTERS OF DEVELOPMENT",
        "INSTITUTIONAL DEVELOPMENT", "LEVELLING RESULTS", "UNIVERSITY LEVEL"
    ]):
        return "curriculum_college"
        
    if any(k in combined for k in [
        "SCHOLARSHIP", "STUDENT INTERNSHIP", "DRUG TESTING", "ADMISSION OF", 
        "GRANTS-IN-AID", "STUFAPS", "TUITION", "ASSISTANCE TO STUDENTS", 
        "STUDENTS'", "FINANCIAL ASSISTANCE", "BAYANIHAN", "SIKAP"
    ]):
        return "scholarship_student_services"
        
    if any(k in combined for k in [
        "FACULTY TRAINING", "CONTINUING PROFESSIONAL EDUCATION", "CPE GRANTS", 
        "SCHOLARSHIPS FOR GRADUATE STUDIES", "IRSE GRANTS", "TEACHING PERSONNEL",
        "NON-TEACHING PERSONNEL", "RESEARCH CHAIR", "TRAINING OF TRAINORS", "TRAINING OF GE"
    ]):
        return "faculty_development"
        
    if any(k in combined for k in [
        "RECOGNIZED JOURNALS", "CHED JIP", "JOURNAL RECOGNITION"
    ]):
        return "research_journals"
        
    return "administrative_governance"

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
