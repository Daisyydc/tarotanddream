from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

APP_DIR = Path(r"E:\Desktop\AIDM\project\tarot_dream_app")
OUTPUT_DIR = APP_DIR / "frontend" / "assets" / "cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://commons.wikimedia.org/wiki/Special:FilePath/"

FILES = [
    ("愚人", "RWS Tarot 00 Fool.jpg"),
    ("魔术师", "RWS Tarot 01 Magician.jpg"),
    ("女祭司", "RWS Tarot 02 High Priestess.jpg"),
    ("皇后", "RWS Tarot 03 Empress.jpg"),
    ("皇帝", "RWS Tarot 04 Emperor.jpg"),
    ("教皇", "RWS Tarot 05 Hierophant.jpg"),
    ("恋人", "RWS Tarot 06 Lovers.jpg"),
    ("战车", "RWS Tarot 07 Chariot.jpg"),
    ("力量", "RWS Tarot 08 Strength.jpg"),
    ("隐士", "RWS Tarot 09 Hermit.jpg"),
    ("命运之轮", "RWS Tarot 10 Wheel of Fortune.jpg"),
    ("正义", "RWS Tarot 11 Justice.jpg"),
    ("倒吊人", "RWS Tarot 12 Hanged Man.jpg"),
    ("死神", "RWS Tarot 13 Death.jpg"),
    ("节制", "RWS Tarot 14 Temperance.jpg"),
    ("恶魔", "RWS Tarot 15 Devil.jpg"),
    ("高塔", "RWS Tarot 16 Tower.jpg"),
    ("星星", "RWS Tarot 17 Star.jpg"),
    ("月亮", "RWS Tarot 18 Moon.jpg"),
    ("太阳", "RWS Tarot 19 Sun.jpg"),
    ("审判", "RWS Tarot 20 Judgement.jpg"),
    ("世界", "RWS Tarot 21 World.jpg"),
]


def safe_name(cn_name: str) -> str:
    return (
        cn_name.replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .strip()
    )


def download_one(item: tuple[str, str]) -> tuple[str, bool, str]:
    cn_name, commons_name = item
    url = BASE + quote(commons_name, safe="")
    out_path = OUTPUT_DIR / f"{safe_name(cn_name)}.jpg"

    if out_path.exists() and out_path.stat().st_size > 0:
        return cn_name, True, f"已存在，跳过: {out_path.name}"

    try:
        with requests.get(
            url,
            stream=True,
            timeout=60,
            headers={"User-Agent": "tarot-dream-app/1.0"}
        ) as resp:
            resp.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return cn_name, True, f"下载成功: {out_path.name}"
    except Exception as e:
        return cn_name, False, f"下载失败: {commons_name} -> {e}"


def main():
    print(f"[INFO] 输出目录: {OUTPUT_DIR}")
    success = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = [ex.submit(download_one, item) for item in FILES]
        for fut in as_completed(futures):
            cn_name, ok, msg = fut.result()
            print(f"[{'OK' if ok else 'ERR'}] {cn_name} - {msg}")
            if ok:
                success += 1
            else:
                failed += 1

    print("\n========================")
    print(f"[DONE] 成功: {success}")
    print(f"[DONE] 失败: {failed}")
    print(f"[DONE] 保存位置: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()