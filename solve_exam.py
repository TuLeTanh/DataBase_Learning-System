import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright
import os

EXAM_FILE = os.path.join(os.path.dirname(__file__), "data", "2025_2026_HK1_DE THI GIUA KY_CSDL_DE01.pdf")
OUTPUT_FILE = "giai-de-thi-01.md"

queries = [
    "Dựa vào nội dung file đính kèm, hãy giải Câu 1 (Vẽ ERD). Nếu không vẽ được sơ đồ, hãy liệt kê chi tiết các thực thể, thuộc tính và mối kết hợp.",
    "Bây giờ hãy viết SQL cụ thể cho từng câu 2.1.a, 2.1.b, 2.1.c và viết biểu thức đại số quan hệ cụ thể cho các câu từ 2.2.a đến 2.2.f theo đúng schema đã cho trong file đính kèm (KHACHHANG, HOPDONG, LSDONGTIEN, CHITIETHD, YEUCAUBAOHIEM). Phải dùng đúng tên bảng và tên cột thật trong đề thi (ví dụ: phương thức 'Chuyển khoản', năm 2025, mã 'LBH202'...), tuyệt đối không dùng placeholder trừu tượng kiểu table1, column1.\n\nLưu ý để tránh sai sót:\n- Câu 2.2.b: Mã loại bảo hiểm là 'LBH202' (tuyệt đối không thêm dấu gạch ngang phía trước).\n- Câu 2.2.d: Bảng YEUCAUBAOHIEM và HOPDONG liên kết với nhau thông qua bảng CHITIETHD (YEUCAUBAOHIEM.MaCTHD = CHITIETHD.MaCTHD và CHITIETHD.SoHD = HOPDONG.SoHD). 'không có yêu cầu giải quyết bảo hiểm nào' nên dùng mệnh đề NOT IN hoặc NOT EXISTS. Điều kiện trạng thái 'Đã hủy' thuộc về Hợp đồng (HOPDONG.TrangThai = 'Đã hủy').",
    "Follow-up: Nếu trong bảng YEUCAUBAOHIEM (câu 2), công ty muốn bổ sung thêm trường 'NguoiDuyet' để ghi nhận nhân viên nào duyệt yêu cầu, ta nên thiết kế thêm bảng nào và thêm khóa ngoại như thế nào?"
]

async def solve_exam():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="msedge")  # Headless=False to see it work
        page = await browser.new_page()
        
        print("Mở trang web http://localhost:5173...")
        await page.goto("http://localhost:5173")
        
        # Wait for app load
        await page.wait_for_selector('text=Trực tuyến', timeout=30000)
        
        # Tạo session mới
        new_session_btn = page.locator('button[title="Tạo cuộc hội thoại mới"]')
        if await new_session_btn.is_visible():
            await new_session_btn.click()
            await page.wait_for_timeout(1000)
            
        print("Bắt đầu đính kèm file đề thi...")
        # Đính kèm file
        file_input = page.locator('input[type="file"]')
        await file_input.set_input_files(EXAM_FILE)
        
        # Chờ file upload hiển thị trên giao diện (có thể là hình ảnh hoặc icon)
        await page.wait_for_timeout(2000)
        
        results = []
        
        for i, q in enumerate(queries):
            print(f"[{i+1}/{len(queries)}] Đang gửi yêu cầu: {q}")
            
            initial_count = len(await page.locator('main > div > div').all_inner_texts())
            
            input_box = page.locator('#chat-input')
            await input_box.fill(q)
            
            send_btn = page.locator('button[title="Gửi tin nhắn"]')
            await send_btn.click()
            
            print(f"[{i+1}/{len(queries)}] Đang chờ bot trả lời...")
            
            # Wait for bounce to appear and disappear
            try:
                await page.wait_for_selector('.animate-skeleton', timeout=2000)
            except:
                pass
            await page.wait_for_selector('.animate-skeleton', state='hidden', timeout=120000)
            
            # Wait until a new message arrives
            bot_response = ""
            for _ in range(60): # 30 seconds max wait for text
                await page.wait_for_timeout(500)
                messages = await page.locator('main > div > div').all_inner_texts()
                if len(messages) > initial_count:
                    await page.wait_for_timeout(1000) # Let it render fully
                    bot_response = messages[-1].strip()
                    if bot_response:
                        break
            else:
                bot_response = "[Lỗi: Bot không phản hồi hoặc trả về rỗng]"
            
            print(f"[{i+1}/{len(queries)}] Đã nhận được câu trả lời.")
            
            results.append(f"**USER:**\n{q}\n\n**BOT:**\n{bot_response}\n")
            
            # Remove file after first query so we don't upload again and again, it's a RAG session so context is kept.
            if i == 0:
                # Xóa file đính kèm trên thanh chat
                remove_btn = page.locator('button.absolute.-top-2.-right-2')
                if await remove_btn.count() > 0:
                    await remove_btn.nth(0).click()
            
            await page.wait_for_timeout(2000)

        # Xuất file kết quả
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("# Giải Đề Thi Giữa Kỳ CSDL (2025-2026) - Đề 01\n\n")
            f.write("---\n\n".join(results))
            
        print(f"Đã xuất kết quả ra file {OUTPUT_FILE}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(solve_exam())
