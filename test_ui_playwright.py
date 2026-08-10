import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from playwright.async_api import async_playwright

QUESTIONS = [
    # 4 questions in-scope
    "Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?",
    "So sánh UNION và UNION ALL trong SQL",
    "Cho ví dụ về vi phạm dạng chuẩn BCNF",
    "Transaction là gì và ACID gồm những gì",
    # 6 questions out-of-scope
    "asdkjaskjd",
    "làm sao để cài đặt MySQL trên Windows",
    "MongoDB lưu trữ dữ liệu dưới dạng nào?",
    "Làm thế nào để sử dụng phpMyAdmin quản lý database?",
    "Cấu hình Replica Set trong cơ sở dữ liệu phân tán",
    "Giải thích khái niệm Eventual Consistency trong NoSQL"
]

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="msedge")
        page = await browser.new_page()
        
        print("Navigating to http://localhost:5173...")
        await page.goto("http://localhost:5173")
        
        # Wait for the app to load and server to be OK
        await page.wait_for_selector('text=Trực tuyến', timeout=10000)
        print("Frontend is online.")

        results = []

        for i, q in enumerate(QUESTIONS):
            print(f"\n[{i+1}/{len(QUESTIONS)}] Testing: {q}")
            
            # Create new session to be stateless
            new_session_btn = page.locator('button[title="Tạo cuộc hội thoại mới"]')
            if await new_session_btn.is_visible():
                await new_session_btn.click()
                await page.wait_for_timeout(1000)
                
            # Wait for bot response
            # Count the current messages
            initial_count = len(await page.locator('main > div > div').all_inner_texts())
            
            # Type question
            input_box = page.locator('#chat-input')
            await input_box.fill(q)
            
            # Click send
            send_btn = page.locator('button[title="Gửi tin nhắn"]')
            await send_btn.click()
            
            # Wait for bot response to appear
            # Wait for loading indicator to appear (may happen too fast)
            try:
                await page.wait_for_selector('.animate-bounce', timeout=2000)
            except:
                pass
            # Wait for loading indicator to disappear
            await page.wait_for_selector('.animate-bounce', state='hidden', timeout=60000)
            
            # Get the last message
            messages = await page.locator('main > div > div').all_inner_texts()
            # The last one should be the bot response
            bot_response = messages[-1]
            
            print(f"Bot response: {bot_response.strip()[:100]}...")
            
            results.append({
                "question": q,
                "response": bot_response.strip()
            })
            
            # Sleep to avoid rate limiting
            if i < len(QUESTIONS) - 1:
                print("Sleeping 7 seconds to respect API limits...")
                await page.wait_for_timeout(7000)
                
        # Save results
        with open("test_report_ui_playwright.txt", "w", encoding="utf-8") as f:
            f.write("=== KẾT QUẢ TEST QUA UI ===\n\n")
            for i, r in enumerate(results):
                f.write(f"Câu {i+1}: {r['question']}\n")
                f.write(f"Trả lời: {r['response']}\n")
                
                # Determine PASS/FAIL loosely
                if i >= 4: # Out of scope
                    if "Tài liệu môn học hiện tại không đề cập" in r['response'] or "Mình chưa hiểu rõ ý bạn" in r['response']:
                        f.write("Đánh giá: PASS (Bị chặn đúng)\n")
                    else:
                        f.write("Đánh giá: FAIL (Lẽ ra phải bị chặn)\n")
                else: # In scope
                    if "Tài liệu môn học hiện tại không đề cập" not in r['response']:
                        f.write("Đánh giá: PASS (Trả lời bình thường)\n")
                    else:
                        f.write("Đánh giá: FAIL (Bị chặn sai)\n")
                
                f.write("-" * 40 + "\n")
                
        print("\nFinished 10 tests! Results saved to test_report_ui_playwright.txt")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
