import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
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

for url in urls:
    print(f"Scraping: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

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

            output.append({
                "title": title,
                "image_url": img_url
            })

            print(f"  ✓ {title} -> {img_url}")

    except Exception as e:
        print(f"  ✗ Failed to scrape {url}: {e}")

with open("output_kma.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "image_url"])
    writer.writeheader()
    writer.writerows(output)

print("\n✅ Done! Saved to output_kma.csv")