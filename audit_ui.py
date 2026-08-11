import asyncio
from playwright.async_api import async_playwright
import time

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="msedge")
        page = await browser.new_page()
        
        print("Navigating to http://localhost:5173...")
        await page.goto("http://localhost:5173")
        await page.wait_for_selector('text=Trực tuyến', timeout=10000)
        await page.wait_for_timeout(1000)
        
        print("1. Settings button in sidebar (Expanded)")
        await page.screenshot(path="screenshot_settings_sidebar_expanded.png")
        
        print("2. Settings button in sidebar (Collapsed)")
        # Click the collapse button (it has stroke="currentColor" and line x1="12" y1="5")
        # Let's just click the button with group class that contains the chevron
        await page.locator('button.w-12.h-12.p-3').first.click()
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_settings_sidebar_collapsed.png")
        
        print("3. Open Settings Modal")
        # Click settings button (has settings title or icon)
        # Using nth(1) or find by svg
        await page.locator('.cursor-pointer').filter(has_text='Settings').click()
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_settings_modal.png")
        
        print("4. Change accent color to Purple")
        await page.locator('.bg-purple-500').click()
        await page.wait_for_timeout(200)
        await page.screenshot(path="screenshot_settings_accent_purple.png")
        
        print("Reloading to check if color persists...")
        await page.reload()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_settings_accent_persists.png")
        
        print("5. Open Settings Modal again to change Language")
        await page.locator('.cursor-pointer').filter(has_text='Settings').click()
        await page.wait_for_timeout(500)
        # Change language to English
        await page.locator('button', has_text='English').click()
        await page.wait_for_timeout(200)
        await page.screenshot(path="screenshot_settings_lang_en.png")
        
        # Close settings modal (click outside or X button)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(500)
        
        print("6. Test question after language change")
        input_box = page.locator('#chat-input')
        await input_box.fill("Transaction là gì?")
        await page.locator('button[title="Send message"]').click()
        await page.wait_for_selector('.animate-bounce', state='hidden', timeout=30000)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_settings_lang_bot_response.png")
        
        print("7. Change Font Size")
        await page.locator('.cursor-pointer').filter(has_text='Settings').click()
        await page.wait_for_timeout(500)
        await page.locator('button', has_text='Large').click()
        await page.wait_for_timeout(200)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_settings_font_large.png")
        
        print("8. Clear History")
        # Open settings
        await page.locator('.cursor-pointer').filter(has_text='Settings').click()
        await page.wait_for_timeout(500)
        
        # We need to setup a dialog handler to check if there is a confirmation
        dialog_messages = []
        page.on("dialog", lambda dialog: (dialog_messages.append(dialog.message), dialog.accept()))
        
        # Click Clear History
        await page.locator('button', has_text='Clear Chat History').click()
        await page.wait_for_timeout(500)
        print(f"Dialog messages: {dialog_messages}")
        
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_settings_history_cleared.png")
        
        print("Done!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
