# Trap Adventure / Bird Adventure (Pygame Platformer)

## 1. Giới thiệu project

### 1.1. Mục tiêu

Dự án xây dựng một game platformer 2D bằng Python và thư viện Pygame, với mục tiêu:

- Thực hành các khái niệm lập trình hướng đối tượng, xử lý sự kiện, vòng lặp game, quản lý trạng thái. :contentReference[oaicite:0]{index=0}  
- Minh họa cách tổ chức một project game tương đối hoàn chỉnh: tách module (core, world, entities, ui, utils), tách dữ liệu level và asset. :contentReference[oaicite:1]{index=1} :contentReference[oaicite:2]{index=2}  
- Xây dựng một trò chơi có chiều sâu vừa phải: nhiều loại bẫy, cơ chế “troll”, độ khó thay đổi theo chế độ chơi.

Game hướng tới việc vừa giải trí, vừa là minh chứng kỹ thuật cho môn học / đồ án lập trình game.

### 1.2. Tổng quan lối chơi

Người chơi điều khiển một nhân vật di chuyển trong môi trường 2D dạng tile, né bẫy và tìm cách đến được checkpoint hoặc cổng thoát để sang màn tiếp theo. Toàn bộ level được mô tả bằng **ASCII map**, mỗi ký tự tương ứng với một loại ô (block, gai, checkpoint, nước, đá, tường, v.v.). :contentReference[oaicite:3]{index=3}  

Vòng lặp chính của game:

- Khởi tạo Pygame, tạo cửa sổ kích thước `960x480`, đặt FPS = 60. :contentReference[oaicite:4]{index=4}  
- Hiển thị **menu chính**, cho phép:
  - Bắt đầu game (`START GAME`)
  - Chọn độ khó (`DIFFICULTY`)
  - Thoát (`QUIT`) :contentReference[oaicite:5]{index=5}  
- Khi vào chơi:
  - Tải level tương ứng, sinh `World` từ dữ liệu `LEVELS` và background `LEVEL_BGS`. :contentReference[oaicite:6]{index=6} :contentReference[oaicite:7]{index=7}  
  - Tạo nhân vật `Player` tại vị trí ký tự `P` với số máu phụ thuộc vào độ khó. :contentReference[oaicite:8]{index=8} :contentReference[oaicite:9]{index=9}  
  - Mỗi frame: xử lý input, áp dụng gravity, xử lý va chạm, cập nhật trap, kiểm tra thắng/thua và vẽ lại màn hình. :contentReference[oaicite:10]{index=10}  

Khi người chơi mất hết máu, game chuyển sang màn hình `GAME OVER`. Nếu vượt qua hết level ứng với độ khó hiện tại, game chuyển sang trạng thái `WIN`. :contentReference[oaicite:11]{index=11}  

### 1.3. Các tính năng chính

#### Hệ thống menu và độ khó

- **Menu chính**:
  - Hiển thị tiêu đề game, các lựa chọn `START GAME`, `DIFFICULTY`, `QUIT`.
  - Hỗ trợ điều khiển bằng cả phím và chuột (di chuyển, enter, hover & click). :contentReference[oaicite:12]{index=12}  
- **Menu độ khó**:
  - 3 mức: `EASY`, `NORMAL`, `HARD`, đi kèm mô tả (số level và số máu). :contentReference[oaicite:13]{index=13}  
  - Class `GameSettings` quyết định:
    - Số level tối đa được chơi (`get_max_levels`)
    - Số level hiển thị trên HUD (`get_display_max`)
    - Số máu ban đầu của nhân vật (`get_player_health`) :contentReference[oaicite:14]{index=14}  

#### Hệ thống level & bẫy

- Level được định nghĩa bằng list các chuỗi trong `LEVELS`, mỗi ký tự là một loại ô:
  - `#`: block cứng
  - `P`: vị trí spawn của Player
  - `C`: checkpoint
  - `F`: fake checkpoint
  - `N`: fake block
  - `M`, `L`: moving platform
  - `^`, `v`, `<`, `>`: spike theo hướng
  - `+`: sóng / tide
  - `~`: nước
  - `W`: tường
  - `S`: đá lăn
  - `X`: tường di chuyển
  - `Q`: switch
  - v.v. :contentReference[oaicite:15]{index=15}  
- Mỗi level có background riêng trong `LEVEL_BGS` để tạo cảm giác môi trường thay đổi (ví dụ: đất liền, biển, v.v.). :contentReference[oaicite:16]{index=16}  

#### Nhân vật người chơi (Player)

- Di chuyển trái/phải, nhảy, ngồi/cúi, bơi trong nước, tương tác với platform di chuyển. :contentReference[oaicite:17]{index=17}  
- Áp dụng gravity và giới hạn tốc độ rơi, có xử lý riêng khi ở dưới nước (gravity nhẹ hơn, rơi chậm hơn). :contentReference[oaicite:18]{index=18}  
- Hệ thống va chạm chi tiết:
  - Va chạm theo trục X, Y, xử lý đứng trên platform (kể cả platform di chuyển).
  - Theo dõi trạng thái `on_ground` để quyết định nhảy/animation. :contentReference[oaicite:19]{index=19}  
- Hệ thống animation:
  - Các trạng thái: `idle`, `run`, `jump`, `sit`, `die`, `swim_idle`, `swimming`, load từ sprite sheet. :contentReference[oaicite:20]{index=20} :contentReference[oaicite:21]{index=21}  
  - Flip trái/phải theo hướng di chuyển, cập nhật frame theo tốc độ khung hình. :contentReference[oaicite:22]{index=22}  
- Hệ thống âm thanh:
  - Âm chân chạy, âm nhảy, âm bơi, sử dụng channel riêng để không bị chồng chéo. :contentReference[oaicite:23]{index=23} :contentReference[oaicite:24]{index=24}  

#### HUD & âm thanh nền

- HUD hiển thị:
  - Health hiện tại
  - Level hiện tại / tổng level theo độ khó
  - Chế độ Difficulty đang dùng
- Có nút Settings (icon bánh răng) ở góc, được highlight khi hover, click để quay lại menu. :contentReference[oaicite:25]{index=25} :contentReference[oaicite:26]{index=26}  
- Hệ thống âm thanh:
  - Nhạc menu, nhạc gameplay, âm game over, âm thắng.
  - Âm trap (spear), điều khiển bằng nhiều `Channel` khác nhau để tránh đè âm. :contentReference[oaicite:27]{index=27}  

### 1.4. Điểm nhấn của project

- Tách bạch rõ ràng giữa:
  - Logic game (`game/core`, `game/world`, `game/entities`)
  - Giao diện người dùng (`game/ui`)
  - Asset (`pygame_assets/`)
- Sử dụng ASCII map để định nghĩa level → dễ mở rộng, chỉnh sửa, thêm bẫy mới.
- Có hệ thống độ khó ảnh hưởng trực tiếp đến số lượng level được chơi và sức khỏe nhân vật.
- Có đầy đủ vòng đời game:
  - Menu chính → Gameplay → Game Over / Win → quay lại menu.
- Tích hợp animation + âm thanh tương đối đầy đủ, giúp game có trải nghiệm trực quan và sống động hơn so với một demo console đơn giản.


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

