from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="Pinterest Scraper API")

def crawl_pinterest_links(keyword: str, max_results: int = 20):
    search_query = keyword.replace(" ", "%20")
    url = f"https://www.pinterest.com/search/pins/?q={search_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/pin/" in href:
            full_link = f"https://www.pinterest.com{href.split('?')[0]}"
            if full_link not in links:
                links.append(full_link)
        if len(links) >= max_results:
            break

    return links

@app.get("/")
def root():
    return {"message": "Pinterest Scraper API. Use /search?q=your+keyword"}

@app.get("/search")
def search(q: str = Query(..., description="Từ khóa tìm kiếm trên Pinterest")):
    results = crawl_pinterest_links(q)
    return JSONResponse(content={
        "keyword": q,
        "total": len(results),
        "results": results
    })
