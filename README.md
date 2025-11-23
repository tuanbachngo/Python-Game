# Trap Adventure / Bird Adventure (Pygame Platformer)

## 1. Giới thiệu project

### Mục tiêu
- Xây dựng một game platformer 2D đơn giản bằng Python/Pygame, phù hợp cho môn học lập trình/game dev cơ bản.
- Thể hiện đầy đủ vòng đời một game: menu, lựa chọn độ khó, gameplay nhiều màn, thắng/thua, âm thanh – hiệu ứng – HUD. :contentReference[oaicite:0]{index=0}  

### Tính năng chính
- Màn hình menu:
  - Tiêu đề game, lựa chọn: `START GAME`, `DIFFICULTY`, `QUIT`.
  - Menu phụ chọn độ khó: `EASY`, `NORMAL`, `HARD`, kèm mô tả số mạng và số level tương ứng. :contentReference[oaicite:1]{index=1}  
- Hệ thống độ khó:
  - Thay đổi số lượng level tối đa và số máu ban đầu của nhân vật theo `EASY / NORMAL / HARD`. :contentReference[oaicite:2]{index=2}  
- Nhiều loại địa hình và bẫy:
  - Block thường, block nửa ô, block kết nối, tường dọc, platform di chuyển.
  - Gai thường, gai ẩn, mũi tên trap, tường đổ – vỡ, đá lăn, nước – sóng, bong bóng đẩy nhân vật, switch kích hoạt,… :contentReference[oaicite:3]{index=3} :contentReference[oaicite:4]{index=4}  
- Checkpoint & fake checkpoint:
  - Checkpoint thật giúp sang level mới.
  - Fake checkpoint và fake block tạo hiệu ứng “bẫy tâm lý”, biến mất khi chạm. :contentReference[oaicite:5]{index=5}  
- Nhiều level được mô tả bằng ASCII map:
  - Mỗi ký tự biểu diễn một loại ô/bẫy: `#`, `P`, `C`, `F`, `N`, `M`, `L`, `^`, `v`, `<`, `>`, `+`, `~`, `W`, `S`, `X`, `Q`, `R`, `E`, `A`,… :contentReference[oaicite:6]{index=6}  
- HUD & âm thanh:
  - Hiển thị Health, Level, Difficulty, nút Settings.
  - Nhạc menu, nhạc gameplay, nhạc thắng, thua, âm thanh trap, bước chân, nhảy, bơi, rung màn hình khi đá lăn,… :contentReference[oaicite:7]{index=7} :contentReference[oaicite:8]{index=8}  

### Cách hoạt động tổng quát

- Khi chạy `main.py`, game khởi tạo cửa sổ kích thước `960 x 480`, FPS 60. :contentReference[oaicite:9]{index=9}  
- Vào menu chính:
  - Chọn `START GAME` để bắt đầu.
  - Chọn `DIFFICULTY` để đổi độ khó, sau đó `ENTER` để áp dụng.
  - Chọn `QUIT` để thoát. :contentReference[oaicite:10]{index=10}  
- Khi vào game:
  - `World` đọc ASCII map, sinh ra block, trap, checkpoint, nước, đá lăn, tường, mũi tên,… và tạo `Player` tại vị trí ký tự `P`. :contentReference[oaicite:11]{index=11}  
  - Mỗi frame:
    - Xử lý input (di chuyển, nhảy,…), áp dụng gravity, kiểm tra va chạm với các vật thể rắn.
    - Cập nhật trap, stone, moving wall, tide, water, switch, bubble, arrow trap.
    - Kiểm tra checkpoint/level gate để sang level tiếp theo hoặc Win nếu là level cuối theo độ khó hiện tại.
    - Nếu máu về 0: phát animation chết, chuyển sang màn `GAME OVER`. :contentReference[oaicite:12]{index=12} :contentReference[oaicite:13]{index=13}  
- Trạng thái game chính:
  - `menu` → `playing` → `win` hoặc `game_over`, có thể quay lại menu bằng `ESC`. :contentReference[oaicite:14]{index=14}  

---

## 2. Đóng góp của từng thành viên

Bảng dưới chỉ là khung để điền; các tên và tỷ lệ (%) bạn tự chỉnh lại sao cho tổng = 100%.

| STT | Họ và tên           | Phần công việc chính                                                                 | Tỷ lệ đóng góp (%) |
|-----|---------------------|--------------------------------------------------------------------------------------|---------------------|
| 1   | Thành viên 1        | Thiết kế ý tưởng game, xây dựng loop chính trong `main.py`, quản lý trạng thái game |  … %                |
| 2   | Thành viên 2        | Xây dựng hệ thống World/Map, xử lý va chạm, quản lý trap & checkpoint               |  … %                |
| 3   | Thành viên 3        | Lập trình nhân vật Player (di chuyển, nhảy, bơi, animation, âm thanh bước chân…)   |  … %                |
| 4   | Thành viên 4        | Thiết kế HUD, menu, hệ thống độ khó, hiển thị thông tin và điều khiển trong game    |  … %                |
| 5   | Thành viên 5        | Thiết kế level (ASCII map), bố trí bẫy/nước/stone/moving wall, cân bằng độ khó      |  … %                |
| 6   | Thành viên 6        | Thiết kế đồ họa, âm thanh, viết tài liệu (README, báo cáo), hỗ trợ debug & tối ưu   |  … %                |
|     | **Tổng cộng**       |                                                                                      | **100%**           |

Bạn có thể đổi mô tả công việc cho sát đúng thực tế nhóm.

---

## 3. Hướng dẫn cài đặt và chạy code

### 3.1. Yêu cầu môi trường

- Python: khuyến nghị **Python 3.10** (3.9+ đều có thể, tùy thư viện).
- Đã cài `pip`.
- Đã cài các dependency hệ thống cơ bản của Pygame (tùy hệ điều hành).

Cấu trúc thư mục quan trọng:
- `config.py` trỏ thư mục assets tới `pygame_assets/`, vì vậy cần giữ nguyên cấu trúc:
  - Thư mục cùng cấp `main.py`
    - `config.py`
    - `game/` (source code)
    - `pygame_assets/` (ảnh, font, âm thanh). :contentReference[oaicite:15]{index=15}  

### 3.2. Cài đặt thư viện

Tạo file `requirements.txt` (nếu chưa có), tối thiểu:

```txt
pygame

