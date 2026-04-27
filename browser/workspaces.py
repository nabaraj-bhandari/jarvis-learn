import asyncio
import json
from browser.tabs import get_browser, async_playwright
from db.connection import get_connection  # your context manager


async def save_workspace(name: str) -> str:
    """
    Save all current tabs as a named workspace in SQLite.
    Stores title + URL as JSON array.
    """
    playwright, browser = await get_browser()

    tabs = []
    for context in browser.contexts:
        for page in context.pages:
            tabs.append({"title": await page.title(), "url": page.url})

    await playwright.stop()

    # KEY CONCEPT: json.dumps() converts Python list → JSON string
    # SQLite stores it as TEXT, we parse it back with json.loads() later
    tabs_json = json.dumps(tabs)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO browser_workspaces (name, tabs_json)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET
                tabs_json = excluded.tabs_json,
                updated_at = CURRENT_TIMESTAMP
        """,
            (name, tabs_json),
        )

    return f"Saved workspace '{name}' with {len(tabs)} tabs"


async def restore_workspace(name: str) -> str:
    """
    Open all tabs from a saved workspace.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT tabs_json FROM browser_workspaces WHERE name = ?", (name,)
        ).fetchone()

    if not row:
        return f"No workspace named '{name}'"

    tabs = json.loads(row[0])  # JSON string → Python list

    playwright, browser = await get_browser()
    context = browser.contexts[0]

    for tab in tabs:
        page = await context.new_page()
        await page.goto(tab["url"])

    await playwright.stop()
    return f"Restored workspace '{name}' — opened {len(tabs)} tabs"
