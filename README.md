# Trap Adventure / Bird Adventure (Pygame Platformer)
<img src="Trap%20Adventure%20Game%20App/pygame_assets/running-effect-sheet.png" width="500">

<video width="640" controls>
  <source src="Trap Adventure Game App/pygame_assets/Giới thiệu cách chơi.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## 1. Giới thiệu project

### 1.1. Mục tiêu

Dự án được xây dựng với mục tiêu chính là áp dụng và thực hành **lập trình hướng đối tượng (OOP)** trong một môi trường thực tế — cụ thể là một trò chơi platformer 2D sử dụng Python và thư viện Pygame. Toàn bộ cấu trúc game được thiết kế xoay quanh mô hình OOP nhằm phát triển:

- **Phân rã hệ thống** thành các lớp rõ ràng: `Player`, `World`, `Tile`, `HUD`, `MenuManager`, `GameSettings`, v.v.
- **Tách biệt trách nhiệm (Single Responsibility)**:  
  - `Player` chỉ quản lý chuyển động, va chạm, animation, âm thanh nhân vật.  
  - `World` chịu trách nhiệm đọc ASCII map, sinh vật thể, quản lý bẫy, cập nhật môi trường.  
  - `HUD` và `MenuManager` xử lý giao diện.  
  - `GameSettings` quản lý độ khó và thông số gameplay.  
- **Tính đóng gói (Encapsulation)**: mỗi lớp tự xử lý dữ liệu và logic của chính nó; ví dụ, `Player` tự kiểm soát velocity, gravity, sound channel, frame animation.  
- **Tính kế thừa và mở rộng (Extensibility)**: hệ thống tile/trap trong `tiles.py` được thiết kế để dễ dàng thêm loại bẫy mới chỉ bằng cách tạo class mới.  
- **Tính tái sử dụng (Reusability)**: các module như `load_frames()` dùng lại cho mọi animation.  
- **Tách tài nguyên (Separation of Assets & Logic)** thông qua `config.py` và thư mục `pygame_assets/`.

Bên cạnh yêu cầu kỹ thuật OOP, dự án còn hướng tới:

- Rèn luyện cách tổ chức một project game hoàn chỉnh, chia module đúng chuẩn.
- Hiểu quy trình phát triển game: vòng lặp game, xử lý input, cập nhật trạng thái, render khung hình.
- Kết hợp nhiều thành phần: AI đơn giản (bẫy), vật lý (gravity, va chạm), âm thanh, animation, HUD.
- Tạo ra một sản phẩm game có thể chơi được, có nhiều level, có độ thử thách và tính giáo dục.

Mục tiêu cuối cùng là **vận dụng kiến thức OOP theo cách trực quan nhất**, nhìn thấy ngay kết quả bằng hình ảnh/âm thanh thay vì chỉ qua lý thuyết hoặc các ví dụ console đơn giản.

### 1.2. Tổng quan lối chơi

Người chơi điều khiển một nhân vật di chuyển trong môi trường 2D dạng tile, né bẫy và tìm cách đến được checkpoint hoặc cổng thoát để sang màn tiếp theo. Toàn bộ level được mô tả bằng **ASCII map**, mỗi ký tự tương ứng với một loại ô (block, gai, checkpoint, nước, đá, tường, v.v.). 

Vòng lặp chính của game:

- Khởi tạo Pygame, tạo cửa sổ kích thước `960x480`, đặt FPS = 60.  
- Hiển thị **menu chính**, cho phép:
  - Bắt đầu game (`START GAME`)
  - Chọn độ khó (`DIFFICULTY`)
  - Thoát (`QUIT`) 
- Khi vào chơi:
  - Tải level tương ứng, sinh `World` từ dữ liệu `LEVELS` và background `LEVEL_BGS`. 
  - Tạo nhân vật `Player` tại vị trí ký tự `P` với số máu phụ thuộc vào độ khó. 
  - Mỗi frame: xử lý input, áp dụng gravity, xử lý va chạm, cập nhật trap, kiểm tra thắng/thua và vẽ lại màn hình. 

Khi người chơi mất hết máu, game chuyển sang màn hình `GAME OVER`. Nếu vượt qua hết level ứng với độ khó hiện tại, game chuyển sang trạng thái `WIN`.  

### 1.3. Các tính năng chính

#### Hệ thống menu và độ khó

- **Menu chính**:
  - Hiển thị tiêu đề game, các lựa chọn `START GAME`, `DIFFICULTY`, `QUIT`.
  - Hỗ trợ điều khiển bằng cả phím và chuột (di chuyển, enter, hover & click). 
- **Menu độ khó**:
  - 3 mức: `EASY`, `NORMAL`, `HARD`, đi kèm mô tả (số level và số máu). 
  - Class `GameSettings` quyết định:
    - Số level tối đa được chơi (`get_max_levels`)
    - Số level hiển thị trên HUD (`get_display_max`)
    - Số máu ban đầu của nhân vật (`get_player_health`) 

#### Hệ thống level & bẫy

- Level được định nghĩa bằng list các chuỗi trong `LEVELS`, mỗi ký tự là một loại ô:
  - `#`: block cứng
  - `B`: half block
  - `P`: vị trí spawn của Player
  - `C`: checkpoint
  - `F`: fake checkpoint
  - `D`: delay checkpoint
  - `N`: fake block
  - `E`: level gate
  - `M`, `L`: moving platform theo hướng
  - `^`, `v`, `<`, `>`: spike theo hướng
  - `G`, `H`: delay spike
  - `+`: sóng 
  - `~`: nước
  - `W`: tường
  - `S`: đá lăn
  - `X`: tường di chuyển
  - `Q`: switch
  - `A`: arrow
  - `R`: bubble spout
  - `S`: stone
  - Mỗi level có background riêng trong `LEVEL_BGS` để tạo cảm giác môi trường thay đổi (ví dụ: đất liền, biển, v.v.). 

#### Nhân vật người chơi (Player)

- Di chuyển trái/phải, nhảy, ngồi/cúi, bơi trong nước, tương tác với platform di chuyển. 
- Áp dụng gravity và giới hạn tốc độ rơi, có xử lý riêng khi ở dưới nước (gravity nhẹ hơn, rơi chậm hơn).
- Hệ thống va chạm chi tiết:
  - Va chạm theo trục X, Y, xử lý đứng trên platform (kể cả platform di chuyển).
  - Theo dõi trạng thái `on_ground` để quyết định nhảy/animation.
- Hệ thống animation:
  - Các trạng thái: `idle`, `run`, `jump`, `sit`, `die`, `swim_idle`, `swimming`, load từ sprite sheet.   
  - Flip trái/phải theo hướng di chuyển, cập nhật frame theo tốc độ khung hình. 
- Hệ thống âm thanh:
  - Âm chân chạy, âm nhảy, âm bơi, sử dụng channel riêng để không bị chồng chéo.
 
#### Hệ thống điều khiển nhân vật (Controls)

- Di chuyển sang trái: `A` hoặc `←`
- Di chuyển sang phải: `D` hoặc `→`
- Nhảy: `W`, `↑` hoặc `Space`
- Ngồi / Cúi xuống: `Shift`, `S` hoặc `↓`
- Bơi trong nước: tự động kích hoạt khi nhân vật ở trong vùng nước; có thể nhảy nhẹ bằng `Space`
- Reset khi chết: `R`
- Mở menu / Thoát về Menu chính: `ESC`
- Chọn nút trong Menu: 
  - Dùng `↑ / ↓` để di chuyển
  - `Enter` để chọn
  - Hoặc bấm chuột trực tiếp vào nút

#### HUD & âm thanh nền

- HUD hiển thị:
  - Health hiện tại
  - Level hiện tại / tổng level theo độ khó
  - Chế độ Difficulty đang dùng
- Có nút Settings (icon bánh răng) ở góc, được highlight khi hover, click để quay lại menu.
- Hệ thống âm thanh:
  - Nhạc menu, nhạc gameplay, âm game over, âm thắng.
  - Âm trap (spear), điều khiển bằng nhiều `Channel` khác nhau để tránh đè âm. 

### 1.4. Điểm nhấn của project

- **Thiết kế theo hướng đối tượng, tách bạch rõ ràng các lớp và module:**
  - Logic game: `game/core`, `game/world`, `game/entities`  
    - Chứa các lớp như `GameSettings`, `World`, `Player`, các loại `Tile`/trap,… chịu trách nhiệm về luật chơi, va chạm, cập nhật trạng thái.
  - Giao diện người dùng: `game/ui`  
    - `HUD`, `MenuManager` tách riêng toàn bộ phần hiển thị, menu, HUD ra khỏi logic gameplay.
  - Tài nguyên: `pygame_assets/`  
    - Hình ảnh, âm thanh, font được truy cập gián tiếp qua `config.py` → logic không phụ thuộc đường dẫn cứng.

- **Khai thác OOP để dễ mở rộng và bảo trì:**
  - Mỗi loại đối tượng (nhân vật, block, trap, stone, moving wall, nước, sóng, checkpoint,…) được biểu diễn bằng class riêng hoặc nhóm class cùng “họ”.
  - Khi muốn thêm bẫy mới hoặc hiệu ứng mới, chỉ cần tạo class mới hoặc mở rộng class sẵn có, không phải sửa hàng loạt chỗ trong code.

- **Sử dụng ASCII map để định nghĩa level**, kết hợp với lớp `World` đọc map và sinh đối tượng:
  - Mỗi ký tự trong map tương ứng với một loại tile/class cụ thể.
  - Cách tổ chức này thể hiện rõ tính trừu tượng: level chỉ là “dữ liệu”, còn cách xử lý/trả về đối tượng đã được đóng gói trong code.

- **Hệ thống độ khó do lớp `GameSettings` quản lý tập trung:**
  - Quy định số level tối đa, số máu ban đầu theo từng chế độ `EASY / NORMAL / HARD`.
  - Dễ chỉnh, dễ mở rộng (chỉ sửa một nơi), thể hiện đúng tinh thần đóng gói & tái sử dụng của OOP.

- **Vòng đời game rõ ràng qua các trạng thái (state) được quản lý trong code:**
  - `menu` → `playing` → `game_over` / `win` → quay lại `menu`.
  - Mỗi trạng thái có phần xử lý input, update, render tách riêng → dễ đọc, dễ bảo trì.

- **Tích hợp animation + âm thanh theo từng đối tượng:**
  - `Player` tự quản lý animation và âm thanh di chuyển/nhảy/bơi.
  - `HUD`/`MenuManager` tự quản lý nhạc nền, âm thắng/thua.
  → Mỗi lớp chịu trách nhiệm cho “hành vi” của chính nó, giúp dự án là một ví dụ trực quan cho OOP chứ không chỉ là một game đơn thuần.

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
- Cấu trúc thư mục quan trọng:
```txt
├── main.py                 # File chạy chính của game
├── config.py               # Cấu hình BASE_DIR, ASSETS_DIR, hàm asset()
├── requirements.txt        # Danh sách thư viện cần cài (pygame, pyinstaller)

├── game/                   # Mã nguồn chính của game (theo OOP)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py    # Kích thước màn hình, FPS, GRAVITY, SPEED, ...
│   │   ├── settings.py     # Lớp GameSettings: EASY/NORMAL/HARD, máu, số level
│   │   └── levels.py       # Định nghĩa LEVELS, LEVEL_BGS (ASCII map và background)
│   │
│   ├── entities/
│   │   ├── __init__.py
│   │   └── player.py       # Lớp Player: di chuyển, nhảy, bơi, animation, âm thanh
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── hud.py          # HUD hiển thị Health, Level, Difficulty, nút Settings
│   │   └── menu.py         # MenuManager: menu chính, menu chọn độ khó
│   │
│   ├── utlis/
│   │   ├── __init__.py
│   │   └── load.py         # Hàm load_frames() cắt sprite sheet thành các frame animation
│   │
│   └── world/
│       ├── __init__.py
│       ├── world.py        # Lớp World: đọc map, sinh tile, trap, cập nhật thế giới
│       └── tiles.py        # Định nghĩa các loại Tile: block, spike, water, stone, ...

├── pygame_assets/          # Tài nguyên game (truy cập qua config.asset())
```

### 3.2. Cài đặt thư viện
Cài đặt toàn bộ thư viện bằng:

```txt
pip install -r requiremnts.txt
```

### 3.3. Cách tạo app
1. Mở file `main.py`
2. Tạo môi trường venv (không bắt buộc nhưng nên có để giữ cô lập thư viện của project) 
```txt
# Tạo venv
python -m venv venv (Win)
hoặc
python3 -m venv venv (macOs / Linux)
```
3. Kích hoạt venv
```
venv\Scripts\activate (Win)
source venv/bin/activate (macOs / Linux)
```
- Test lại: `python main.py` 
- Lỗi trong quá trình kích hoạt venv (nếu có với Win):
```
PowerShell bị khóa quyền chạy script nên không cho chạy activate.pps1(running scripts is disabled on this system) vì Python dùng bản toàn hệ thống (system Python) và Pygame không được cài trong system Python → game không chạy
Cách 1: mở cmd trong folder tổng r kích hoạt venv: venv\Scripts\activate.bat
Cách 2: mở powershell bằng quyền Administrator rồi chạy: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CururrentUser
```
4. Cài lại thư viện
```
pip install -r requirements.txt
```
5. Đóng gói bằng PyInstaller
```
pyinstaller --onefile --windowed --add-data "pygame_assets;pygame_assets”  main.py (Win)
pyinstaller --onefile --windowed --add-data "pygame_assets:pygame_assets”  main.py (macOs / Linux)
```
- trên Windows dùng dấu `;`, trên Mac/Linux dùng `:`
6. Chạy app game:
  - vào thư mục `dist` ấn `main.exe` hoặc `main.app`
