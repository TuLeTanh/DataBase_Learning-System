import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

regression_queries = [
    "Làm sao để cài đặt MySQL trên Windows",
    "MongoDB lưu trữ dữ liệu dưới dạng nào?",
    "Làm thế nào để sử dụng phpMyAdmin quản lý database?",
    "Cấu hình Replica Set trong cơ sở dữ liệu phân tán",
    "Giải thích khái niệm Eventual Consistency trong NoSQL",
    "Cách tối ưu hóa index trên PostgreSQL"
]

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="msedge")
        page = await browser.new_page()
        
        print("Navigating to http://localhost:5173...")
        await page.goto("http://localhost:5173")
        
        # Wait for the app to load
        await page.wait_for_selector('text=Trực tuyến', timeout=10000)
        print("Frontend is online.\n")

        results = []
        all_pass = True

        for i, q in enumerate(regression_queries):
            print(f"[{i+1}/{len(regression_queries)}] Hỏi: {q}")
            
            # Click New Session
            new_session_btn = page.locator('button[title="Tạo cuộc hội thoại mới"]')
            if await new_session_btn.is_visible():
                await new_session_btn.click()
                await page.wait_for_timeout(500)
                
            # Type question
            input_box = page.locator('#chat-input')
            await input_box.fill(q)
            
            # Wait for bot response
            # Count the current messages
            initial_count = len(await page.locator('main > div > div').all_inner_texts())
            
            # Click send
            send_btn = page.locator('button[title="Gửi tin nhắn"]')
            await send_btn.click()
            
            # Wait until there's a new message
            for _ in range(30):
                await page.wait_for_timeout(500)
                messages = await page.locator('main > div > div').all_inner_texts()
                if len(messages) > initial_count:
                    # New message appeared. Wait a bit for it to populate if needed.
                    await page.wait_for_timeout(500)
                    bot_response = messages[-1].strip()
                    if bot_response:
                        break
            else:
                bot_response = ""
                
            answer_lower = bot_response.lower()
            if "không đề cập" in answer_lower or "không chứa thông tin" in answer_lower or "tài liệu môn học" in answer_lower:
                status = "PASS"
            else:
                status = "FAIL"
                all_pass = False
                
            print(f"Bot: {bot_response}")
            print(f"Kết quả: {status}\n")
            
            results.append(f"Q: {q}\nA: {bot_response}\nStatus: {status}\n")
            
            if i < len(regression_queries) - 1:
                await page.wait_for_timeout(2000)
                
        with open("test_report_regression_ui.txt", "w", encoding="utf-8") as f:
            f.write("=== KẾT QUẢ REGRESSION TEST QUA UI ===\n\n")
            f.write("\n".join(results))
            if all_pass:
                f.write("\nALL REGRESSION TESTS PASSED.\n")
            else:
                f.write("\nSOME REGRESSION TESTS FAILED.\n")
                
        print("Done. Saved to test_report_regression_ui.txt")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
