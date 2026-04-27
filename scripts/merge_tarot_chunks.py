from __future__ import annotations

import json
import re
from pathlib import Path

APP_DIR = Path(r"E:\Desktop\AIDM\project\tarot_dream_app")
TAROT_DIR = APP_DIR / "data" / "tarot"

OLD_CHUNKS_PATH = TAROT_DIR / "tarot_chunks.json"
NEW_BOOKS_PATH = APP_DIR / "books_chunks_cleaned.jsonl"
OUTPUT_PATH = TAROT_DIR / "tarot_chunks_merged.json"


def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def load_old_chunks(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"未找到旧 chunks 文件: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    docs = []

    for item in data:
        text = item.get("text", "").strip()
        if not text:
            continue

        doc = {
            "id": item.get("id"),
            "source": item.get("source", "old_rag"),
            "type": item.get("type", "unknown"),
            "text": text
        }

        if "cards" in item:
            doc["cards"] = item["cards"]

        docs.append(doc)

    return docs


def load_new_book_chunks(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"未找到新书籍 chunks 文件: {path}")

    docs = []

    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            item = json.loads(line)
            text = item.get("content", "").strip()
            if not text:
                continue

            docs.append({
                "id": item.get("chunk_id", f"book_chunk_{i}"),
                "source": item.get("source_file", "tarot_books"),
                "type": "tarot_book_chunk",
                "text": text,
                "book_id": item.get("book_id"),
                "category": item.get("category"),
                "file_type": item.get("file_type"),
                "page_start": item.get("page_start"),
                "page_end": item.get("page_end"),
                "para_start": item.get("para_start"),
                "para_end": item.get("para_end"),
            })

    return docs


def deduplicate_docs(docs: list[dict]) -> list[dict]:
    seen = set()
    unique_docs = []

    for doc in docs:
        key = normalize_text(doc["text"])
        if key in seen:
            continue
        seen.add(key)
        unique_docs.append(doc)

    return unique_docs


def main():
    print(f"[INFO] 旧 chunks: {OLD_CHUNKS_PATH}")
    print(f"[INFO] 新书籍 chunks: {NEW_BOOKS_PATH}")
    print(f"[INFO] 输出路径: {OUTPUT_PATH}")

    old_docs = load_old_chunks(OLD_CHUNKS_PATH)
    new_docs = load_new_book_chunks(NEW_BOOKS_PATH)

    merged = old_docs + new_docs
    merged = deduplicate_docs(merged)

    OUTPUT_PATH.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[OK] old_docs = {len(old_docs)}")
    print(f"[OK] new_docs = {len(new_docs)}")
    print(f"[OK] merged_unique_docs = {len(merged)}")
    print(f"[OK] 已保存到: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()