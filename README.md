# Trap Adventure / Bird Adventure (Pygame Platformer)

## 1. Giới thiệu project

### Mục tiêu
- Xây dựng một game platformer 2D đơn giản bằng Python/Pygame.
- Thể hiện đầy đủ vòng đời một game: menu, lựa chọn độ khó, gameplay nhiều màn, thắng/thua, âm thanh – hiệu ứng – HUD. 

### Tính năng chính
- Màn hình menu:
  - Tiêu đề game, lựa chọn: `START GAME`, `DIFFICULTY`, `QUIT`.
  - Menu phụ chọn độ khó: `EASY`, `NORMAL`, `HARD`, kèm mô tả số mạng và số level tương ứng. 
- Hệ thống độ khó:
  - Thay đổi số lượng level tối đa và số máu ban đầu của nhân vật theo `EASY / NORMAL / HARD`.   
- Nhiều loại địa hình và bẫy:
  - Block thường, block nửa ô, block kết nối, tường dọc, platform di chuyển.
  - Gai thường, gai ẩn, mũi tên trap, tường đổ – vỡ, đá lăn, nước – sóng, bong bóng đẩy nhân vật, switch kích hoạt,… 
- Checkpoint & fake checkpoint:
  - Checkpoint thật giúp sang level mới.
  - Fake checkpoint và fake block tạo hiệu ứng “bẫy tâm lý”, biến mất khi chạm.
- Nhiều level được mô tả bằng ASCII map:
  - Mỗi ký tự biểu diễn một loại ô/bẫy: `#`, `P`, `C`, `F`, `N`, `M`, `L`, `^`, `v`, `<`, `>`, `+`, `~`, `W`, `S`, `X`, `Q`, `R`, `E`, `A`,… 
- HUD & âm thanh:
  - Hiển thị Health, Level, Difficulty, nút Settings.
  - Nhạc menu, nhạc gameplay, nhạc thắng, thua, âm thanh trap, bước chân, nhảy, bơi, rung màn hình khi đá lăn,… 

### Cách hoạt động tổng quát

- Khi chạy `main.py`, game khởi tạo cửa sổ kích thước `960 x 480`, FPS 60. 
- Vào menu chính:
  - Chọn `START GAME` để bắt đầu.
  - Chọn `DIFFICULTY` để đổi độ khó, sau đó `ENTER` để áp dụng.
  - Chọn `QUIT` để thoát.
- Khi vào game:
  - `World` đọc ASCII map, sinh ra block, trap, checkpoint, nước, đá lăn, tường, mũi tên,… và tạo `Player` tại vị trí ký tự `P`. 
  - Mỗi frame:
    - Xử lý input (di chuyển, nhảy,…), áp dụng gravity, kiểm tra va chạm với các vật thể rắn.
    - Cập nhật trap, stone, moving wall, tide, water, switch, bubble, arrow trap.
    - Kiểm tra checkpoint/level gate để sang level tiếp theo hoặc Win nếu là level cuối theo độ khó hiện tại.
    - Nếu máu về 0: phát animation chết, chuyển sang màn `GAME OVER`. 
- Trạng thái game chính:
  - `menu` → `playing` → `win` hoặc `game_over`, có thể quay lại menu bằng `ESC`. 

---

## 2. Đóng góp của từng thành viên


| STT | Họ và tên           | Phần công việc chính                                                                                 | Tỷ lệ đóng góp (%)  |
|-----|---------------------|------------------------------------------------------------------------------------------------------|---------------------|
| 1   | Ngô Tuấn Bách       | Thiết kế HUD, menu, hiển thị, xây dựng loop chính trong `main.py`, xây dựng trap level 1,5 và Player |  17.5 %             |
| 2   | Đỗ Quang Huy        | Thiết kế ý tưởng game, xử lý va chạm, xây dựng trap level 2, 3, 4 và Player                          |  17.5 %             |
| 3   | Dương Hồng Ánh      | Xây dựng trap level 5                                                                                |  16.1 %             |
| 4   | Nguyễn Minh Thư     | Thiết kế HUD, menu, hệ thống độ khó, hiển thị, tạo app                                               |  16.1 %             |
| 5   | Trần Diệp Đình Anh  | Xây dựng hệ thống World/Map, Làm slide trình bày dự án                                               |  16.1 %             |
| 6   | Vũ Anh Dũng         | Thiết kế đồ họa, âm thanh, hiệu ứng chuyển động Player. Thiết kế slide                               |  16.7 %             |
|     | **Tổng cộng**       |                                                                                                      | **100%**            |


---

## 3. Hướng dẫn cài đặt và chạy code

### 3.1. Yêu cầu môi trường

- Python: khuyến nghị **Python 3.10**.
- Đã cài `pip`.
- Đã cài các dependency hệ thống cơ bản của Pygame.

Cấu trúc thư mục quan trọng:
- `config.py` trỏ thư mục assets tới `pygame_assets/`, vì vậy cần giữ nguyên cấu trúc:
  - Thư mục cùng cấp `main.py`
    - `config.py`
    - `game/` (source code)
    - `pygame_assets/` (ảnh, font, âm thanh). 

### 3.2. Cài đặt thư viện

Trong file `requirements.txt`:

```txt
pygame
pyinstaller

