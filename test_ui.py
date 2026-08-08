import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("http://localhost:5173")
        await page.wait_for_selector("#chat-input")
        
        # 1. Take a screenshot of the empty input area
        input_area = await page.query_selector("footer")
        await input_area.screenshot(path="screenshot_1_empty_input.png")
        
        # 2. Type multiple lines to test auto-resize
        textarea = await page.query_selector("#chat-input")
        await textarea.fill("Dòng 1\nDòng 2\nDòng 3\nDòng 4")
        await page.wait_for_timeout(500)
        await input_area.screenshot(path="screenshot_2_multiline.png")
        
        # 3. Simulate paste image
        # Note: Playwright doesn't easily allow pasting system clipboard images without complex permissions, 
        # so we inject a mock paste event using evaluate
        await page.evaluate("""() => {
            const dt = new DataTransfer();
            const canvas = document.createElement('canvas');
            canvas.width = 100;
            canvas.height = 100;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = 'red';
            ctx.fillRect(0, 0, 100, 100);
            canvas.toBlob(blob => {
                const file = new File([blob], 'pasted_image.png', { type: 'image/png' });
                dt.items.add(file);
                
                const pasteEvent = new ClipboardEvent('paste', {
                    clipboardData: dt,
                    bubbles: true,
                    cancelable: true
                });
                document.getElementById('chat-input').dispatchEvent(pasteEvent);
            });
        }""")
        
        await page.wait_for_timeout(1000) # Wait for preview to render
        await input_area.screenshot(path="screenshot_3_pasted_image.png")
        
        # 4. Click Send
        send_btn = await page.query_selector("footer button[title='Gửi tin nhắn']")
        is_disabled = await send_btn.get_attribute("disabled")
        print(f"Send button disabled before click? {is_disabled}")
        await send_btn.click()
        
        await page.wait_for_timeout(3000) # Wait for response
        
        # Screenshot the whole chat
        await page.screenshot(path="screenshot_4_after_send.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
