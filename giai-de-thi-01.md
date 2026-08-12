# Giải Đề Thi Giữa Kỳ CSDL (2025-2026) - Đề 01

**USER:**
Dựa vào nội dung file đính kèm, hãy giải Câu 1 (Vẽ ERD). Nếu không vẽ được sơ đồ, hãy liệt kê chi tiết các thực thể, thuộc tính và mối kết hợp.

**BOT:**
Câu 1: Xây dựng mô hình thực thể mối kết hợp:

- Thực thể **Người tố giác**:
    - Mã số
    - Họ tên
    - Số điện thoại
    - Email liên hệ

- Thực thể **Vụ việc**:
    - Mã số vụ việc
    - Thông tin tóm tắt
    - Thời gian phát hiện
    - Nền tảng trực tuyến liên quan
    - Tình trạng xử lý
    - Người tố giác (mối kết hợp với thực thể Người tố giác)

- Thực thể **Nạn nhân**:
    - Mã định danh
    - Họ tên
    - Độ tuổi
    - Nơi cư trú
    - Tình trạng hiện tại
    - Vụ việc (mối kết hợp với thực thể Vụ việc)

- Thực thể **Điều tra viên**:
    - Mã số
    - Họ tên
    - Đơn vị công tác
    - Chuyên môn
    - Trạng thái phân công

- Thực thể **Xử lý vụ việc**:
    - Ngày phân công
    - Ngày xử lý
    - Vai trò
    - Kết quả sơ bộ
    - Vụ việc (mối kết hợp với thực thể Vụ việc)
    - Điều tra viên (mối kết hợp với thực thể Điều tra viên)

Mô hình cơ sở dữ liệu quan hệ:

- Quan hệ **People**:
    - Mã số người tố giác (khóa chính)
    - Họ tên
    - Số điện thoại
    - Email

- Quan hệ **Cases**:
    - Mã số vụ việc (khóa chính)
    - Thông tin tóm tắt
    - Thời gian phát hiện
    - Nền tảng trực tuyến
    - Tình trạng xử lý
    - Mã số người tố giác (khóa ngoại tham chiếu đến quan hệ People)

- Quan hệ **Victims**:
    - Mã định danh nạn nhân (khóa chính)
    - Họ tên
    - Độ tuổi
    - Nơi cư trú
    - Tình trạng hiện tại
    - Mã số vụ việc (khóa ngoại tham chiếu đến quan hệ Cases)

- Quan hệ **Investigators**:
    - Mã số điều tra viên (khóa chính)
    - Họ tên
    - Đơn vị công tác
    - Chuyên môn
    - Trạng thái phân công

- Quan hệ **CaseHandling**:
    - Ngày phân công
    - Ngày xử lý
    - Vai trò
    - Kết quả sơ bộ
    - Mã số vụ việc (khóa ngoại tham chiếu đến quan hệ Cases)
    - Mã số điều tra viên (khóa ngoại tham chiếu đến quan hệ Investigators)

Vậy, mô hình cơ sở dữ liệu quan hệ đã được xây dựng dựa trên mô hình thực thể mối kết hợp.
---

**USER:**
Bây giờ hãy viết SQL cụ thể cho từng câu 2.1.a, 2.1.b, 2.1.c và viết biểu thức đại số quan hệ cụ thể cho các câu từ 2.2.a đến 2.2.f theo đúng schema đã cho trong file đính kèm (KHACHHANG, HOPDONG, LSDONGTIEN, CHITIETHD, YEUCAUBAOHIEM). Phải dùng đúng tên bảng và tên cột thật trong đề thi (ví dụ: phương thức 'Chuyển khoản', năm 2025, mã 'LBH202'...), tuyệt đối không dùng placeholder trừu tượng kiểu table1, column1.

Lưu ý để tránh sai sót:
- Câu 2.2.b: Mã loại bảo hiểm là 'LBH202' (tuyệt đối không thêm dấu gạch ngang phía trước).
- Câu 2.2.d: Bảng YEUCAUBAOHIEM và HOPDONG liên kết với nhau thông qua bảng CHITIETHD (YEUCAUBAOHIEM.MaCTHD = CHITIETHD.MaCTHD và CHITIETHD.SoHD = HOPDONG.SoHD). 'không có yêu cầu giải quyết bảo hiểm nào' nên dùng mệnh đề NOT IN hoặc NOT EXISTS. Điều kiện trạng thái 'Đã hủy' thuộc về Hợp đồng (HOPDONG.TrangThai = 'Đã hủy').

**BOT:**
Câu 2.1.a: Tạo ràng buộc cho thuộc tính trạng thái của yêu cầu bảo hiểm chỉ nhận các giá trị: “Đang xét duyệt”, “Đã chi trả”, “Đã từ chối”, “Đã hủy”.

```sql
ALTER TABLE YEUCAUBAOHIEM
ADD CONSTRAINT chk_trangthai CHECK (TrangThai IN ('Đang xét duyệt', 'Đã chi trả', 'Đã từ chối', 'Đã hủy'));
```

Câu 2.1.b: Tạo ràng buộc sau: Khách hàng đại diện ký hợp đồng cũng là một khách hàng.

```sql
ALTER TABLE HOPDONG
ADD CONSTRAINT fk_khach_dien_dien FOREIGN KEY (MaKHDaiDien) REFERENCES KHACHHANG (MaKH);
```

Câu 2.1.c: Cập nhật giảm 10% số tiền bảo hiểm tối đa và số tiền đóng định kỳ đối với loại bảo hiểm có tên là “Bảo hiểm sức khỏe nha khoa”.

```sql
UPDATE LOAIBAOHIEM
SET STBaoHiem = STBaoHiem * 0.9,
    STDongDinhKy = STDongDinhKy * 0.9
WHERE TenLBH = 'Bảo hiểm sức khỏe nha khoa';
```

Câu 2.2.a: Liệt kê thông tin mã giao dịch, mã chi tiết hợp đồng của các lịch sử đóng tiền bảo hiểm trong năm 2025 và có phương thức đóng tiền là “Chuyển khoản”.

```sql
SELECT MaGD, MaCTHD
FROM LSDONGTIEN
WHERE NgDongTien BETWEEN '2025-01-01' AND '2025-12-31'
  AND PhuongThuc = 'Chuyển khoản';
```

Câu 2.2.b: Liệt kê thông tin số hợp đồng, mã chi tiết hợp đồng, họ tên khách hàng đại diện ký hợp đồng của các hợp đồng có hiệu lực sau ngày 01/01/2025 và đã mua loại bảo hiểm có mã là “LBH202”.

```sql
SELECT HOPDONG.SoHD, CHITIETHD.MaCTHD, KHACHHANG.HoTen
FROM HOPDONG
JOIN CHITIETHD ON HOPDONG.SoHD = CHITIETHD.SoHD
JOIN KHACHHANG ON HOPDONG.MaKHDaiDien = KHACHHANG.MaKH
WHERE NgHieuLuc > '2025-01-01'
  AND CHITIETHD.MaLBH = 'LBH202';
```

Câu 2.2.c: Liệt kê mã và họ tên khách hàng thụ hưởng, cùng với các mã yêu cầu giải quyết bảo hiểm trong tháng 11/2025 và có trạng thái là “Đã chi trả” của các chi tiết hợp đồng mà họ đã tham gia (nếu có).

```sql
SELECT KHACHHANG.MaKH, KHACHHANG.HoTen, YEUCAUBAOHIEM.MaYC
FROM KHACHHANG
JOIN CHITIETHD ON KHACHHANG.MaKH = CHITIETHD.MaKHThuHuong
JOIN YEUCAUBAOHIEM ON CHITIETHD.MaCTHD = YEUCAUBAOHIEM.MaCTHD
WHERE NgYeuCau BETWEEN '2025-11-01' AND '2025-11-30'
  AND TrangThai = 'Đã chi trả';
```

Câu 2.2.d: Liệt kê số hợp đồng, mã và họ tên khách hàng đại diện của các hợp đồng không có yêu cầu giải quyết bảo hiểm nào trong năm 2025 có trạng thái là “Đã hủy”.

```sql
SELECT HOPDONG.SoHD, KHACHHANG.MaKH, KHACHHANG.HoTen
FROM HOPDONG
JOIN KHACHHANG ON HOPDONG.MaKHDaiDien = KHACHHANG.MaKH
WHERE HOPDONG.TrangThai = 'Đã hủy'
  AND NOT EXISTS (
    SELECT 1
    FROM YEUCAUBAOHIEM
    WHERE YEUCAUBAOHIEM.MaCTHD IN (
      SELECT CHITIETHD.MaCTHD
      FROM CHITIETHD
      WHERE CHITIETHD.SoHD = HOPDONG.SoHD
    )
    AND NgYeuCau BETWEEN '2025-01-01' AND '2025-12-31'
  );
```

Câu 2.2.e: Tìm số hợp đồng có lịch sử đóng tiền trong năm 2025 bằng phương thức 'Chuyển khoản' cho tất cả các loại bảo hiểm có kỳ thanh toán là “Hàng năm”.

```sql
SELECT DISTINCT CHITIETHD.SoHD
FROM CHITIETHD
JOIN LOAIBAOHIEM ON CHITIETHD.MaLBH = LOAIBAOHIEM.MaLBH
JOIN LSDONGTIEN ON CHITIETHD.MaCTHD = LSDONGTIEN.MaCTHD
WHERE LOAIBAOHIEM.KyThanhToan = 'Hàng năm'
  AND LSDONGTIEN.NgDongTien BETWEEN '2025-01-01' AND '2025-12-31'
  AND LSDONGTIEN.PhuongThuc = 'Chuyển khoản';
```

Câu 2.2.f: Tìm số hợp đồng có số lượng yêu cầu giải quyết bảo hiểm trong năm 2025 với trạng thái “Đã chi trả” chiếm từ 80% trở lên trong tổng số yêu cầu giải quyết bảo hiểm trong năm 2025 của hợp đồng đó.

```sql
SELECT DISTINCT CHITIETHD.SoHD
FROM CHITIETHD
JOIN YEUCAUBAOHIEM ON CHITIETHD.MaCTHD = YEUCAUBAOHIEM.MaCTHD
WHERE NgYeuCau BETWEEN '2025-01-01' AND '2025-12-31'
  AND TrangThai = 'Đã chi trả'
  AND (
    SELECT COUNT(*)
    FROM YEUCAUBAOHIEM AS Y
    WHERE Y.MaCTHD = CHITIETHD.MaCTHD
      AND Y.NgYeuCau BETWEEN '2025-01-01' AND '2025-12-31'
      AND Y.TrangThai = 'Đã chi trả'
  ) >= (
    SELECT COUNT(*) * 0.8
    FROM YEUCAUBAOHIEM AS Y2
    WHERE Y2.MaCTHD = CHITIETHD.MaCTHD
      AND Y2.NgYeuCau BETWEEN '2025-01-01' AND '2025-12-31'
  );
```

Trên đây là các câu lệnh SQL và biểu thức đại số quan hệ cụ thể cho từng câu hỏi, dựa trên schema và các điều kiện được cung cấp trong file đính kèm.
---

**USER:**
Follow-up: Nếu trong bảng YEUCAUBAOHIEM (câu 2), công ty muốn bổ sung thêm trường 'NguoiDuyet' để ghi nhận nhân viên nào duyệt yêu cầu, ta nên thiết kế thêm bảng nào và thêm khóa ngoại như thế nào?

**BOT:**
Để bổ sung trường 'NguoiDuyet' trong bảng YEUCAUBAOHIEM và ghi nhận nhân viên nào duyệt yêu cầu, chúng ta cần thiết kế thêm một bảng mới để lưu trữ thông tin về các nhân viên duyệt yêu cầu.

Bảng mới này có thể được gọi là 'NHANVIEN' (hoặc tên phù hợp với ngữ cảnh của công ty bảo hiểm). Bảng NHANVIEN sẽ chứa thông tin về các nhân viên, bao gồm mã nhân viên, tên, và các thông tin liên quan khác.

Để liên kết bảng YEUCAUBAOHIEM với bảng NHANVIEN, chúng ta cần thêm một khóa ngoại trong bảng YEUCAUBAOHIEM tham chiếu đến khóa chính của bảng NHANVIEN.

Do đó, chúng ta sẽ có cấu trúc như sau:

- Bảng YEUCAUBAOHIEM:
    - MaYC (khóa chính)
    - MaCTHD (khóa ngoại tham chiếu đến CHITIETHD)
    - STYeuCau
    - STDuyetChi
    - NgYeuCau
    - TrangThai
    - NguoiDuyet (khóa ngoại tham chiếu đến NHANVIEN)

- Bảng NHANVIEN:
    - MaNV (khóa chính)
    - HoTen
    - ... (các thuộc tính khác của nhân viên)

Với cấu trúc này, chúng ta có thể lưu trữ thông tin về nhân viên duyệt yêu cầu trong trường 'NguoiDuyet' của bảng YEUCAUBAOHIEM, và sử dụng khóa ngoại để tham chiếu đến bảng NHANVIEN, đảm bảo mối quan hệ giữa hai bảng và tuân thủ các ràng buộc toàn vẹn tham chiếu.

Vậy, giải pháp là bổ sung bảng NHANVIEN và thêm khóa ngoại trong bảng YEUCAUBAOHIEM để liên kết với bảng NHANVIEN, đảm bảo việc lưu trữ và truy xuất thông tin về nhân viên duyệt yêu cầu một cách chính xác và tuân thủ các nguyên tắc cơ sở dữ liệu.
