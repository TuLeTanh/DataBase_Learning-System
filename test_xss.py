import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright
import os

async def run_xss_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="msedge")
        page = await browser.new_page()
        
        print("Navigating to http://localhost:5173...")
        await page.goto("http://localhost:5173")
        
        # Wait for the app to load
        await page.wait_for_selector('text=Trực tuyến', timeout=10000)
        print("Frontend is online.")

        # Click SQL Sandbox button
        await page.click('button:has-text("SQL Sandbox")')
        await page.wait_for_selector('button:has-text("Run (F5)")')

        # Type query 1: CREATE TABLE
        await page.fill('textarea', 'CREATE TABLE xss(payload TEXT);')
        await page.click('button:has-text("Run (F5)")')
        await page.wait_for_timeout(1000)

        # Type query 2: INSERT
        await page.fill('textarea', 'INSERT INTO xss VALUES (\'<script>alert(1)</script>\');')
        await page.click('button:has-text("Run (F5)")')
        await page.wait_for_timeout(1000)

        # Type query 3: SELECT
        await page.fill('textarea', 'SELECT * FROM xss;')
        await page.click('button:has-text("Run (F5)")')
        await page.wait_for_timeout(2000)

        # Take screenshot
        await page.screenshot(path="xss_test_screenshot.png")
        print("Screenshot saved to xss_test_screenshot.png")

        # Get HTML of the results table to prove it's escaped
        # In SqlSandbox.jsx, results are displayed in a table.
        html_content = await page.inner_html('table')
        
        with open("xss_html_output.txt", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("HTML output saved to xss_html_output.txt")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_xss_test())
