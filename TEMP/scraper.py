from playwright.async_api import async_playwright, Error
import asyncio
from .models import RawPageData


# async def fetch_html_with_playwright(url: str) -> Optional[str]:
#     """Fetch HTML content with Playwright (handles dynamic content)."""
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch()  # Or p.firefox.launch() or p.webkit.launch()
#             page = await browser.new_page()
#             await page.goto(url, timeout=30000) # 30 seconds timeout
#             html = await page.content()
#             await browser.close()
#             return html
#     except Error as e:
#         print(f"Playwright error fetching {url}: {e}")
#         return None
#     except Exception as e: # Catch any other exceptions
#         print(f"An unexpected error occurred: {e}")
#         return None




async def fetch_html_with_playwright(url: str, scroll_timeout: int = 10000, scroll_pause_time: int = 500) -> RawPageData:
    """Fetch HTML content with Playwright, handling dynamic scrolling."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=30000)

            await page.wait_for_url(url)

            # Scroll to the bottom of the page repeatedly
            scroll_height = await page.evaluate('() => document.body.scrollHeight')
            viewport_height = await page.evaluate('() => window.innerHeight')
            total_scroll_height = 0

            while total_scroll_height < scroll_height:
                await page.evaluate('() => window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(scroll_pause_time / 1000)  # Pause to allow content to load
                new_scroll_height = await page.evaluate('() => document.body.scrollHeight')

                if new_scroll_height > scroll_height: # content was loaded
                  scroll_height = new_scroll_height
                total_scroll_height += viewport_height
            page_title = await page.title()
            html = await page.content()
            await browser.close()
            return RawPageData(
                url=url,
                title=page_title,
                html = html
            )
    except Error as e:
        print(f"Playwright error fetching {url}: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

