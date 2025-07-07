from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()

@app.get("/crawl")
def crawl_pins(keyword: str = "cake", limit: int = 10):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()
        page.goto(f"https://www.pinterest.com/search/pins/?q={keyword}")
        page.wait_for_timeout(3000)
        pins = page.locator("a[href*='/pin/']").all()
        links = []
        for pin in pins:
            href = pin.get_attribute("href")
            if href and "/pin/" in href:
                full_link = "https://www.pinterest.com" + href
                if full_link not in links:
                    links.append(full_link)
            if len(links) >= limit:
                break
        browser.close()
        return {"links": links}
