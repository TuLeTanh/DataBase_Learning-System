import asyncio
from playwright.async_api import async_playwright
import sqlite3

def get_stats():
    conn = sqlite3.connect('backend/chatbot.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages")
    messages = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sessions")
    sessions = c.fetchone()[0]
    conn.close()
    return sessions, messages

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto('http://localhost:5173')
        await page.wait_for_timeout(1000)
        
        print("--- TEST LOCAL STORAGE ---")
        val_before = await page.evaluate("window.localStorage.getItem('accentColor')")
        print(f"Before change: accentColor = {val_before}")
        
        # Click settings (Cài đặt)
        await page.locator('button', has_text='Cài đặt').click()
        await page.wait_for_timeout(500)
        
        # Click purple
        # The purple button has class 'bg-purple-500'
        await page.locator('button.bg-purple-500').click()
        await page.wait_for_timeout(500)
        
        val_after = await page.evaluate("window.localStorage.getItem('accentColor')")
        print(f"After change: accentColor = {val_after}")
        
        await page.reload()
        await page.wait_for_timeout(1000)
        
        val_reload = await page.evaluate("window.localStorage.getItem('accentColor')")
        print(f"After reload: accentColor = {val_reload}")
        
        print("\n--- TEST SCROLL (Item 3) ---")
        await page.screenshot(path='C:\\Users\\ADMIN\\.gemini\\antigravity-ide\\brain\\54928a13-6c6a-45a1-919c-229fd0b0c2ea\\screenshot_after_css_fix.png')
        print("Captured screenshot_after_css_fix.png")
        
        print("\n--- TEST CLEAR HISTORY (Item 2) ---")
        s_before, m_before = get_stats()
        print(f"DB before delete: Sessions = {s_before}, Messages = {m_before}")
        
        dialog_messages = []
        async def handle_dialog(dialog):
            dialog_messages.append(dialog.message)
            await dialog.accept()
        page.on("dialog", handle_dialog)
        
        # Need to open settings again after reload
        await page.locator('button', has_text='Cài đặt').click()
        await page.wait_for_timeout(500)
        
        # Click Delete All Chats (Xoá toàn bộ trò chuyện)
        await page.locator('button', has_text='Xoá toàn bộ lịch sử chat').click()
        await page.wait_for_timeout(1000)
        
        print(f"Intercepted Dialog Message: {dialog_messages}")
        
        s_after, m_after = get_stats()
        print(f"DB after delete: Sessions = {s_after}, Messages = {m_after}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
