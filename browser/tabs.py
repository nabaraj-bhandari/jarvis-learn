import asyncio
from playwright.async_api import async_playwright


# KEY CONCEPT: We use async because Playwright is async by nature.
# Every browser operation (listing tabs, clicking, switching) takes
# real time — async lets Python do other things while waiting.

CDP_URL = "http://localhost:9222"  # Where Chromium is listening


async def get_browser():
    """
    Connect to the already-running Chromium instance.
    connect_over_cdp = Chrome DevTools Protocol.
    This is how tools like DevTools, Playwright, and Puppeteer
    all talk to a running browser.
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp(CDP_URL)
    return playwright, browser


async def list_tabs() -> list[dict]:
    """
    Returns a list of all open tabs with index, title, and URL.

    KEY CONCEPT: browser.contexts gives you browser windows.
    Each context has pages (tabs). We flatten all of them.
    """
    playwright, browser = await get_browser()

    tabs = []
    for context in browser.contexts:
        for i, page in enumerate(context.pages):
            tabs.append(
                {
                    "index": i,
                    "title": await page.title(),  # reads the actual <title> tag
                    "url": page.url,
                }
            )

    await playwright.stop()
    return tabs


async def switch_to_tab(search: str) -> str:
    """
    Switch to a tab whose title contains the search string.
    Case-insensitive. Returns result message.

    KEY CONCEPT: page.bring_to_front() is the actual switch.
    It's like clicking a tab — brings it to focus.
    """
    playwright, browser = await get_browser()
    search_lower = search.lower()

    for context in browser.contexts:
        for page in context.pages:
            title = await page.title()
            if search_lower in title.lower():
                await page.bring_to_front()
                await playwright.stop()
                return f"Switched to: {title}"

    await playwright.stop()
    return f"No tab found matching: '{search}'"


async def close_tab(search: str) -> str:
    """Close a tab by title match."""
    playwright, browser = await get_browser()
    search_lower = search.lower()

    for context in browser.contexts:
        for page in context.pages:
            title = await page.title()
            if search_lower in title.lower():
                await page.close()
                await playwright.stop()
                return f"Closed: {title}"

    await playwright.stop()
    return f"No tab found matching: '{search}'"


# Run directly for quick testing
if __name__ == "__main__":

    async def main():
        tabs = await list_tabs()
        for tab in tabs:
            print(f"[{tab['index']}] {tab['title']}")
            print(f"     {tab['url']}\n")

    asyncio.run(main())
