import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import csv

urls = [
    "https://cendikia.kemenag.go.id/publik/kategori/1/36/81?page=1",
    "https://cendikia.kemenag.go.id/publik/kategori/1/36/81?page=2",
    "https://cendikia.kemenag.go.id/publik/kategori/1/36/55?page=1",
    "https://cendikia.kemenag.go.id/publik/kategori/1/36/57?page=1",
    "https://cendikia.kemenag.go.id/publik/kategori/1/36/57?page=2",
    "https://cendikia.kemenag.go.id/publik/kategori/1/36/57?page=3",
    
]

output = []

pdf_url_pattern = re.compile(r'pdfUrl\s*:\s*"([^"]+)"')

headers = {
    "User-Agent": "Mozilla/5.0"
}

items_to_fetch = []  

for url in urls:
    print(f"Scraping list: {url}")
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        for container in soup.select("div.bs-shelf-image"):
            img_tag = container.find("img")
            if not img_tag or not img_tag.get("src"):
                continue

            img_url = urljoin(url, img_tag["src"])
            filename = img_url.split("?")[0].split("/")[-1]
            if not filename.startswith("cover_"):
                continue

            textbox_div = container.select_one("div.bs-textbox > p")
            if not textbox_div:
                continue

            raw_html = str(textbox_div)
            before_br = raw_html.split("<br")[0]
            title = ' '.join(BeautifulSoup(before_br, "html.parser").get_text().strip().split())

            a_tag = container.find("a", href=True)
            if not a_tag:
                continue

            pdf_url = urljoin(url, a_tag["href"])

            items_to_fetch.append({
                "title": title,
                "image_url": img_url,
                "pdf_url": pdf_url
            })
    except Exception as e:
        print(f"  ✗ Failed to scrape {url}: {e}")

async def fetch_detail(session, item):
    try:
        async with session.get(item["pdf_url"]) as res:
            html = await res.text()
            soup = BeautifulSoup(html, "html.parser")

            pdf_url = ""
            for script in soup.find_all("script"):
                if script.string and "pdfUrl" in script.string:
                    match = pdf_url_pattern.search(script.string)
                    if match:
                        pdf_url = match.group(1)
                        break

            item["pdf_url"] = pdf_url
            print(f"  ✓ {item['title']} -> {item['pdf_url'] or 'N/A'}")
            output.append(item)
    except Exception as e:
        print(f"  ✗ Error fetching {item['pdf_url']}: {e}")

async def main():
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [fetch_detail(session, item) for item in items_to_fetch]
        await asyncio.gather(*tasks)

asyncio.run(main())

with open("output_kma.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "image_url", "pdf_url"])
    writer.writeheader()
    writer.writerows(output)

print("\n✅ Done! Data with PDF links saved to output_kma.csv")