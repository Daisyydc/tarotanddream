from pathlib import Path
import json
import pandas as pd


# ===== 项目目录 =====
APP_DIR = Path(r"E:\Desktop\AIDM\project\tarot_dream_app")

# ===== 真实数据包目录（已根据你的实际搜索结果确认） =====
DATA_PACK_DIR = APP_DIR / "data" / "tarot_dream_data_pack" / "tarot_dream_data_pack"

RAW_DIR = DATA_PACK_DIR / "raw"
CLEANED_DIR = DATA_PACK_DIR / "cleaned"

# ===== 输出目录 =====
OUTPUT_DIR = APP_DIR / "data" / "tarot"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "tarot_chunks.json"


def load_card_relations(md_path: Path):
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    chunks = []

    raw_parts = [part.strip() for part in text.split("\n\n") if part.strip()]

    for i, part in enumerate(raw_parts, start=1):
        if len(part) < 20:
            continue

        chunks.append({
            "id": f"relations_{i}",
            "source": "card_relations",
            "type": "tarot_relations",
            "text": part
        })

    return chunks


def normalize_columns(df: pd.DataFrame):
    normalized = {}
    for c in df.columns:
        key = c.strip().lower().replace(" ", "_")
        normalized[key] = c
    return normalized


def pick_column(cols_map, candidates):
    for name in candidates:
        if name in cols_map:
            return cols_map[name]
    return None


def load_tarot_readings(csv_path: Path):
    df = pd.read_csv(csv_path)
    chunks = []

    cols = normalize_columns(df)

    card1_col = pick_column(cols, ["card1", "card_1", "first_card", "第一张"])
    card2_col = pick_column(cols, ["card2", "card_2", "second_card", "第二张"])
    card3_col = pick_column(cols, ["card3", "card_3", "third_card", "第三张"])
    reading_col = pick_column(cols, ["reading", "interpretation", "text", "content", "解读"])

    if not all([card1_col, card2_col, card3_col, reading_col]):
        print("[ERROR] CSV 列名不符合预期。")
        print("[ERROR] 当前列名如下：")
        for c in df.columns:
            print(" -", c)
        raise ValueError("请根据真实列名调整脚本中的候选列名。")

    for i, row in df.iterrows():
        card1 = str(row[card1_col]).strip()
        card2 = str(row[card2_col]).strip()
        card3 = str(row[card3_col]).strip()
        reading = str(row[reading_col]).strip()

        if not reading or reading.lower() == "nan":
            continue

        chunk_text = (
            f"三张牌案例：\n"
            f"第一张：{card1}\n"
            f"第二张：{card2}\n"
            f"第三张：{card3}\n"
            f"解读：{reading}"
        )

        chunks.append({
            "id": f"reading_{i}",
            "source": "dendory_tarot_readings",
            "type": "tarot_case",
            "cards": [card1, card2, card3],
            "text": chunk_text
        })

    return chunks


def main():
    md_path = RAW_DIR / "card-relations.md"
    csv_path = CLEANED_DIR / "Dendory_tarot_readings_clean.csv"

    print(f"[INFO] APP_DIR = {APP_DIR}")
    print(f"[INFO] DATA_PACK_DIR = {DATA_PACK_DIR}")
    print(f"[INFO] RAW_DIR = {RAW_DIR}")
    print(f"[INFO] CLEANED_DIR = {CLEANED_DIR}")

    all_chunks = []

    if md_path.exists():
        print(f"[OK] 找到 {md_path}")
        all_chunks.extend(load_card_relations(md_path))
    else:
        print(f"[WARN] 未找到 {md_path}")

    if csv_path.exists():
        print(f"[OK] 找到 {csv_path}")
        all_chunks.extend(load_tarot_readings(csv_path))
    else:
        print(f"[WARN] 未找到 {csv_path}")

    OUTPUT_PATH.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[OK] 已生成 {OUTPUT_PATH}")
    print(f"[OK] 共 {len(all_chunks)} 个 tarot chunks")


if __name__ == "__main__":
    main()