# Python-Game
1) Nhóm Gameplay (programming game rules & feel)
**Học**

Pygame Sprite/Group, vòng lặp game, delta time.

Vật lý 2D cơ bản: vận tốc/gia tốc, gravity & jump; va chạm tách trục (X rồi Y).

Hệ trigger/hazard (bẫy trễ, one-hit kill), checkpoint/respawn.

State machine đơn giản (idle/run/jump/fall/hurt); timer (pygame.time.get_ticks).

Debug: overlay FPS, bật vẽ hitbox, phím reset/teleport.

**Chuẩn đầu ra (deliverables)**

Player(Sprite) chạy/nhảy mượt; coyote time & jump buffer (khuyến nghị).

Enemy(Sprite) tuần tra, bị stomp; chạm ngang gây damage.

Coin(Sprite) & HUD điểm.

Hazard/Trigger cho bẫy kiểu Trap Adventure (kích hoạt trễ, bẫy giả).

Checkpoint/Goal + respawn.

Tất cả nhận dt, không phụ thuộc FPS.

**Số liệu “thiết kế” (để phối hợp với Level)**

(theo set mặc định: RUN_SPEED=260, JUMP_SPEED=720, GRAVITY=1800)

Thời gian bay ≈ 0.8 s, độ cao tối đa ≈ 144 px (~3 tiles).

Nhảy xa tối đa (không gió) ≈ 208 px (~4.3 tiles).
⇒ Thiết kế “an toàn” cho gap: ≤ 3 tiles, “khó” 3.5–4 tiles.

Lối đi cao tối thiểu: 3 tiles trên đầu để không cạ trần khi nhảy.

**Checklist chất lượng (DoD)**

60 FPS ổn định; thoát bằng ESC; không traceback.

Tất cả va chạm không kẹt góc; không “xuyên tường”.

Bẫy/địch/coin đều qua Group và spritecollide.

2) Nhóm Level (thiết kế & dựng màn)
**Học**

Editor Tiled (TMX) hoặc CSV; layers: Solids, Decor, Entities.

Triển khai legend & spawn từ file (dùng object layer hoặc ký tự CSV).

Nguyên lý Trap Adventure: “dạy rồi phản bội”, bẫy trễ, checkpoint ngắn.

Nhịp độ & độ khó: giới hạn gap/độ cao theo số liệu gameplay ở trên.

**Chuẩn đầu ra**

Level 1 dạy điều khiển + 1–2 bẫy “nhẹ” + coin.

Level 2 có enemy + combo bẫy; add checkpoint.

Level 3 tổng hợp + goal rõ ràng.

File map + preview (ảnh/GIF 10–20s) + ghi chú “bẫy” (thời gian trễ, tín hiệu nhỏ).

Validator cơ bản (nếu Tools chưa xong): script kiểm tra ký tự lạ/điểm spawn thiếu.

**Quy tắc dựng trap (gợi ý)**

Bẫy trễ: đặt Trigger 0.3–0.6s sau khi người chơi đi qua mới sinh Spike.

Telegraph nhỏ: gạch hơi lệch màu, âm “tạch” nhỏ; đủ để người tinh ý né.

Checkpoint: sau mỗi “bài học” bẫy ~10–20s gameplay.

**DoD**

Mỗi màn clearable trong 2–5 phút; không softlock.

Tôn trọng metrics (gap/ceiling); checkpoint đúng chỗ; không nhảy mù ngoài màn.

3) Nhóm Artist (hình/animation + có thể kiêm audio cơ bản)
**Học**

Pixel art 48px grid; xuất PNG trong suốt; căn pivot thống nhất (nhân vật dùng rect.midbottom).

Sprite sheet vs. frame rời; naming theo quy ước.

Parallax BG (2–3 lớp); tối ưu: convert() cho ảnh nền, convert_alpha() cho sprite.

(Tuỳ) Âm thanh: WAV/OGG ngắn, loop nhạc.

**Chuẩn đầu ra**

Tileset 48px: ground/platform/brick/pipe; biến thể để “telegraph” bẫy.

Player: idle, run (6–8 frames), jump.

Enemy: walk (2–4 frames), death nhỏ.

Coin: spin (4–6 frames).

UI: số/biểu tượng đơn giản; title/pause/win.

BG: sky + layer xa (parallax), file lớn có thể tiling.

**Thông số/kỹ thuật**

Màu/độ tương phản cao; silhouette rõ.

Export: sprite rời name_0.png… hoặc sheet + .json mô tả frames (nếu coder cần).

Âm lượng: nhạc nền nhẹ, SFX ngắn; tránh clip.

**DoD**

Khung hình khớp 48px; mép khít (seamless) với tileset.

Tên file đúng chuẩn; pivot nhất quán; test hiển thị trong game.
