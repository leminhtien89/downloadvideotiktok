import os
import re
import browser_cookie3
from yt_dlp import YoutubeDL

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def save_tiktok_cookies(cookie_path='tiktok_cookies.txt'):
    try:
        cj = browser_cookie3.load(domain_name='tiktok.com')
        with open(cookie_path, 'w', encoding='utf-8') as f:
            cookie_str = '; '.join([f"{c.name}={c.value}" for c in cj])
            f.write(cookie_str)
        print(f"✅ Đã lấy cookie TikTok và lưu vào {cookie_path}")
    except Exception as e:
        print(f"❌ Không thể lấy cookie từ trình duyệt: {e}")

def download_all_videos(username, base_dir="downloads"):
    save_tiktok_cookies()
    cookie_string = open('tiktok_cookies.txt', 'r', encoding='utf-8').read().strip()

    url = f"https://www.tiktok.com/@mrkhan123khn"
    print(f"\n🔍 Đang tải tất cả video từ: {url}")

    output_dir = os.path.join(base_dir, username)
    os.makedirs(output_dir, exist_ok=True)

    log_file = os.path.join(base_dir, f"{username}_log.txt")
    error_log_file = os.path.join(base_dir, f"{username}_error_log.txt")

    downloaded_ids = set()
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            downloaded_ids = set(line.strip().split("|")[0] for line in f)

    existing_files = set(os.listdir(output_dir))

    ydl_opts_list = {
        'extract_flat': True,
        'dump_single_json': True,
        'quiet': True,
        'http_headers': {
            'Cookie': cookie_string
        }
    }

    try:
        with YoutubeDL(ydl_opts_list) as ydl:
            result = ydl.extract_info(url, download=False)
            entries = result.get("entries", [])

        total = len(entries)
        success_count = 0
        error_count = 0

        for idx, entry in enumerate(entries, start=1):
            try:
                video_id = entry.get("id")
                raw_title = entry.get("title", f"video_{video_id}")
                title = sanitize_filename(raw_title)
                filename_check = f"{title[:50]}.mp4"

                print(f"\n📦 [{idx}/{total}] Đang xử lý: {title}")

                if video_id in downloaded_ids:
                    print(f"⏩ Video đã có trong log, bỏ qua.")
                    continue
                if filename_check in existing_files:
                    print(f"⏩ Video đã có trong thư mục, bỏ qua.")
                    continue

                video_url = entry["url"]
                output_path = os.path.join(output_dir, f"{title[:50]}.%(ext)s")

                ydl_opts_download = {
                    'outtmpl': output_path,
                    'quiet': False,
                    'format': 'mp4',
                    'ignoreerrors': True,
                    'http_headers': {
                        'Cookie': cookie_string
                    }
                }

                with YoutubeDL(ydl_opts_download) as ydl:
                    result = ydl.download([video_url])

                if result == 0:
                    success_count += 1
                    with open(log_file, "a", encoding="utf-8") as logf:
                        logf.write(f"{video_id}|{title}\n")  # ✅ dòng bị lỗi đã sửa đúng
                    print(f"✅ Đã tải: {title}")
                else:
                    raise Exception("yt-dlp trả về mã lỗi != 0")

            except Exception as ve:
                error_count += 1
                error_message = str(ve)
                video_id = entry.get("id", "unknown")
                title = sanitize_filename(entry.get("title", "unknown"))
                with open(error_log_file, "a", encoding="utf-8") as errf:
                    errf.write(f"{video_id}|{title}|{error_message}\n")
                print(f"❌ Lỗi khi tải: {title} | {error_message}")

        print(f"\n🎉 Hoàn tất. Đã tải {success_count}/{total} video. Lỗi: {error_count}.")

    except Exception as e:
        print(f"❌ Lỗi tổng khi lấy danh sách video: {e}")

# 👉 Gọi hàm
download_all_videos("mrkhan123khn")
