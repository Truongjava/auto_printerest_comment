from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from playwright.sync_api import sync_playwright
import urllib.parse

app = FastAPI()

def crawl_pinterest_with_login(keyword: str, limit: int = 10):
    results = []
    search_url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(keyword)}"

    with sync_playwright() as p:
        # Dùng cookie để đăng nhập
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="cookie_pinterest.json")
        page = context.new_page()
        page.goto(search_url, timeout=60000)

        # Chờ nội dung xuất hiện
        page.wait_for_selector("a[href*='/pin/']", timeout=15000)

        # Lấy các link pin
        anchors = page.query_selector_all("a[href*='/pin/']")
        for a in anchors:
            href = a.get_attribute("href")
            if href and '/pin/' in href:
                full_link = urllib.parse.urljoin("https://www.pinterest.com", href)
                if full_link not in results:
                    results.append(full_link)
            if len(results) >= limit:
                break

        browser.close()
    return results

@app.get("/crawl")
def crawl_pins(
    keyword: str = Query(..., description="Từ khóa cần tìm kiếm"),
    limit: int = Query(10, description="Số lượng link bài viết muốn lấy")
):
    links = crawl_pinterest_with_login(keyword, limit)
    filename = f"pins_{keyword.replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")
    return FileResponse(filename, media_type='text/plain', filename=filename)
