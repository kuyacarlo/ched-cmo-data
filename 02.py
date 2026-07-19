import os
import json
import httpx
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

INPUT_JSONL = Path("out.jsonl")
DOWNLOAD_DIR = Path("downloads")
MAX_CONCURRENT_DOWNLOADS = 5

async def download_file(client, url, dest_path, semaphore):
    async with semaphore:
        print(f"Downloading {url} to {dest_path}...")
        temp_path = dest_path.with_suffix(".tmp")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            # Direct httpx stream (Removed Gaffa API Key leakage)
            async with client.stream("GET", url, headers=headers) as response:
                if response.status_code == 200:
                    with open(temp_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                    # Rename to final destination upon success
                    temp_path.rename(dest_path)
                    print(f"  Saved: {dest_path.name}")
                else:
                    print(f"  Failed: HTTP {response.status_code} for {url}")
        except Exception as e:
            print(f"  Error downloading {url}: {e}")
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

async def main():
    if not INPUT_JSONL.exists():
        print(f"Input file '{INPUT_JSONL}' not found. Please run 01.py first.")
        return
        
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    
    with open(INPUT_JSONL, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
        
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=15)
    
    async with httpx.AsyncClient(limits=limits, timeout=60.0) as client:
        tasks = []
        for r in records:
            year_dir = DOWNLOAD_DIR / str(r["year"])
            year_dir.mkdir(exist_ok=True)
            
            url = r["url"]
            filename = url.split("/")[-1]
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            dest_path = year_dir / filename
            
            if dest_path.exists():
                print(f"Skipping {filename} (already exists)")
                continue
                
            tasks.append(download_file(client, url, dest_path, semaphore))
            
        if tasks:
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
