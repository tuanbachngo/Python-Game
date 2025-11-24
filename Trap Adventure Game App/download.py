import os
import zipfile
from pathlib import Path
from urllib.request import urlopen

ZIP_URL = "https://drive.google.com/uc?export=download&id=1LkpQ06SvA3hTFEr08yn7D5hzb-oSVjMx"

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "pygame_assets"
ZIP_PATH = BASE_DIR / "pygame_assets.zip"

def download_zip():
    print(f"Đang tải assets từ: {ZIP_URL}")
    with urlopen(ZIP_URL) as resp, open(ZIP_PATH, "wb") as out_file:
        out_file.write(resp.read())
    print("Tải xong:", ZIP_PATH)

def extract_zip():
    if not ZIP_PATH.exists():
        raise FileNotFoundError("Không tìm thấy pygame_assets.zip")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Đang giải nén vào: {ASSETS_DIR}")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(ASSETS_DIR)

    print("Giải nén xong.")
    ZIP_PATH.unlink(missing_ok=True)

def main():
    if ASSETS_DIR.exists() and any(ASSETS_DIR.iterdir()):
        print("pygame_assets đã tồn tại. Xóa thủ công nếu muốn tải lại.")
        return

    download_zip()
    extract_zip()
    print("Hoàn tất cài đặt assets. Bây giờ chạy: python main.py")

if __name__ == "__main__":
    main()
