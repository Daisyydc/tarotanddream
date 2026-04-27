from pathlib import Path
import json
import pandas as pd


APP_DIR = Path(r"E:\Desktop\AIDM\project\tarot_dream_app")
DATA_PACK_DIR = APP_DIR / "data" / "tarot_dream_data_pack" / "tarot_dream_data_pack"

CLEANED_DIR = DATA_PACK_DIR / "cleaned"

OUTPUT_DIR = APP_DIR / "data" / "dream"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "dream_chunks.json"


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


def load_dream_csv(csv_path: Path):
    df = pd.read_csv(csv_path)
    chunks = []

    cols = normalize_columns(df)

    dream_col = pick_column(cols, ["dream", "title", "keyword", "term", "symbol", "梦境", "关键词"])
    decode_col = pick_column(cols, ["decode", "interpretation", "meaning", "content", "text", "解读", "解释"])

    if not all([dream_col, decode_col]):
        print("[ERROR] Dream CSV 列名不符合预期。")
        print("[ERROR] 当前列名如下：")
        for c in df.columns:
            print(" -", c)
        raise ValueError("请根据真实列名调整脚本中的候选列名。")

    for i, row in df.iterrows():
        dream = str(row[dream_col]).strip()
        decode = str(row[decode_col]).strip()

        if not dream or dream.lower() == "nan":
            continue
        if not decode or decode.lower() == "nan":
            continue

        chunk_text = (
            f"梦境关键词：{dream}\n"
            f"解梦解释：{decode}"
        )

        chunks.append({
            "id": f"dream_{i}",
            "source": "dream_decoder",
            "type": "dream_symbol",
            "keyword": dream,
            "text": chunk_text
        })

    return chunks


def main():
    csv_path = CLEANED_DIR / "dream_decoder_data_clean.csv"

    print(f"[INFO] APP_DIR = {APP_DIR}")
    print(f"[INFO] DATA_PACK_DIR = {DATA_PACK_DIR}")
    print(f"[INFO] CLEANED_DIR = {CLEANED_DIR}")

    all_chunks = []

    if csv_path.exists():
        print(f"[OK] 找到 {csv_path}")
        all_chunks.extend(load_dream_csv(csv_path))
    else:
        print(f"[WARN] 未找到 {csv_path}")

    OUTPUT_PATH.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[OK] 已生成 {OUTPUT_PATH}")
    print(f"[OK] 共 {len(all_chunks)} 个 dream chunks")


if __name__ == "__main__":
    main()