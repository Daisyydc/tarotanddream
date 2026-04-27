from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Any, List

from tqdm import tqdm


INPUT_DIR = Path("data/processed/cleaned")
OUTPUT_DIR = Path("data/processed/chunks")
REPORT_DIR = Path("data/processed/reports")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "books_chunks.jsonl"

MIN_CHARS = 120
MAX_CHARS = 650


def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def infer_category(text: str) -> str:
    if any(k in text for k in ["牌阵", "塞尔特十字", "开牌法", "展开"]):
        return "spread_method"
    if any(k in text for k in ["如何提问", "写一个问题", "问题解读", "开放性解读"]):
        return "questioning"
    if any(k in text for k in ["环境", "每天的解读", "内在指引", "洗牌", "切牌"]):
        return "reading_process"
    if any(k in text for k in ["愚人", "魔术师", "女祭司", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]):
        return "major_arcana"
    if any(k in text for k in ["权杖", "圣杯", "宝剑", "星币", "钱币", "ACE", "王牌", "宫廷牌", "随从", "骑士", "皇后牌", "国王牌"]):
        return "minor_arcana"
    if any(k in text for k in ["塔罗简介", "塔罗牌介绍", "阿尔克那", "塔罗颜色意义"]):
        return "foundation"
    return "general"


def is_valid_chunk_text(text: str) -> bool:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    if chinese_chars < 20:
        return False

    banned_patterns = [
        r"上万套周易教程请加微信",
        r"也可直接进入",
        r"www\.265zhouyiw\.com",
        r"猫鼬魔法仪式小铺",
        r"strc\.taobao\.com",
        r"图片取自http",
        r"http[s]?://\S+",
        r"www\.\S+",
    ]
    for pattern in banned_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return False

    return True


def split_by_punctuation(text: str, max_chars: int = MAX_CHARS) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []

    if len(text) <= max_chars:
        return [text] if len(text) >= MIN_CHARS and is_valid_chunk_text(text) else []

    parts = re.split(r'(?<=[。！？；])', text)
    chunks = []
    current = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if len(current) + len(part) <= max_chars:
            current += part
        else:
            if current.strip():
                chunks.append(current.strip())

            if len(part) > max_chars:
                for i in range(0, len(part), max_chars):
                    sub = part[i:i + max_chars].strip()
                    if sub:
                        chunks.append(sub)
                current = ""
            else:
                current = part

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) >= MIN_CHARS and is_valid_chunk_text(c)]


def build_pdf_chunks(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    pages = data.get("pages", [])
    book_id = data["book_id"]

    chunk_idx = 0
    buffer_text = ""
    buffer_start_page = None
    buffer_end_page = None

    for page in pages:
        page_num = page["page_num"]
        text = normalize_text(page.get("text", ""))

        if not text:
            continue

        if buffer_start_page is None:
            buffer_start_page = page_num

        if len(buffer_text) + len(text) <= MAX_CHARS:
            buffer_text += (" " + text) if buffer_text else text
            buffer_end_page = page_num
        else:
            for piece in split_by_punctuation(buffer_text):
                chunk_idx += 1
                results.append({
                    "chunk_id": f"{book_id}_chunk_{chunk_idx:04d}",
                    "book_id": book_id,
                    "source_file": data["source_file"],
                    "file_type": "pdf",
                    "quality": data.get("quality", "unknown"),
                    "category": infer_category(piece),
                    "page_start": buffer_start_page,
                    "page_end": buffer_end_page,
                    "content": piece
                })

            buffer_text = text
            buffer_start_page = page_num
            buffer_end_page = page_num

    if buffer_text:
        for piece in split_by_punctuation(buffer_text):
            chunk_idx += 1
            results.append({
                "chunk_id": f"{book_id}_chunk_{chunk_idx:04d}",
                "book_id": book_id,
                "source_file": data["source_file"],
                "file_type": "pdf",
                "quality": data.get("quality", "unknown"),
                "category": infer_category(piece),
                "page_start": buffer_start_page,
                "page_end": buffer_end_page,
                "content": piece
            })

    return results


def build_docx_chunks(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    paras = data.get("paragraphs", [])
    book_id = data["book_id"]

    chunk_idx = 0
    buffer_text = ""
    buffer_start_para = None
    buffer_end_para = None

    for para in paras:
        para_num = para["para_num"]
        text = normalize_text(para.get("text", ""))

        if not text:
            continue

        if buffer_start_para is None:
            buffer_start_para = para_num

        if len(buffer_text) + len(text) <= MAX_CHARS:
            buffer_text += ("\n" + text) if buffer_text else text
            buffer_end_para = para_num
        else:
            for piece in split_by_punctuation(buffer_text):
                chunk_idx += 1
                results.append({
                    "chunk_id": f"{book_id}_chunk_{chunk_idx:04d}",
                    "book_id": book_id,
                    "source_file": data["source_file"],
                    "file_type": "docx",
                    "quality": data.get("quality", "unknown"),
                    "category": infer_category(piece),
                    "para_start": buffer_start_para,
                    "para_end": buffer_end_para,
                    "content": piece
                })

            buffer_text = text
            buffer_start_para = para_num
            buffer_end_para = para_num

    if buffer_text:
        for piece in split_by_punctuation(buffer_text):
            chunk_idx += 1
            results.append({
                "chunk_id": f"{book_id}_chunk_{chunk_idx:04d}",
                "book_id": book_id,
                "source_file": data["source_file"],
                "file_type": "docx",
                "quality": data.get("quality", "unknown"),
                "category": infer_category(piece),
                "para_start": buffer_start_para,
                "para_end": buffer_end_para,
                "content": piece
            })

    return results


def main() -> None:
    json_files = list(INPUT_DIR.glob("*.json"))
    total_docs = 0
    total_chunks = 0
    summary = []

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out_f:
        for path in tqdm(json_files, desc="Chunking cleaned text"):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            total_docs += 1

            if data["file_type"] == "pdf":
                chunks = build_pdf_chunks(data)
            else:
                chunks = build_docx_chunks(data)

            for chunk in chunks:
                out_f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

            total_chunks += len(chunks)
            summary.append({
                "source_file": data["source_file"],
                "book_id": data["book_id"],
                "file_type": data["file_type"],
                "num_chunks": len(chunks)
            })

    report = {
        "total_docs": total_docs,
        "total_chunks": total_chunks,
        "output_path": str(OUTPUT_PATH),
        "files": summary
    }

    report_path = REPORT_DIR / "chunking_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Saved chunks to: {OUTPUT_PATH}")
    print(f"Saved chunking report to: {report_path}")


if __name__ == "__main__":
    main()