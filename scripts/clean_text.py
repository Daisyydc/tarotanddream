from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Any, List

from tqdm import tqdm


INPUT_DIR = Path("data/processed/extracted")
OUTPUT_DIR = Path("data/processed/cleaned")
REPORT_DIR = Path("data/processed/reports")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


NOISE_PATTERNS = [
    r"http[s]?://\S+",
    r"www\.\S+",
    r"微信[:：]?\s*\S+",
    r"QQ[:：]?\s*\d+",
    r"获取更多好书.*",
    r"扫一扫.*",
    r"二维码.*",
    r"二維碼.*",
    r"strc\.taobao\.com",
    r"上万套周易教程请加微信[:：]?\s*\S+",
    r"也可直接进入\s*\S+",
    r"猫鼬魔法仪式小铺",
    r"图片取自http\S+",
]


LOW_VALUE_PATTERNS = [
    r"^猫鼬魔法仪式小铺$",
    r"^Quote:?$",
    r"^STEPHANIE$",
    r"^BARBARA$",
    r"^Shadowscapes Tarot$",
    r"^Companion$",
    r"^St\. Royal College$",
    r"^第[一二三四五六七八九十0-9]+课$",
    r"^\(完\)$",
]


def clean_line(text: str) -> str:
    text = text.strip()

    extra_patterns = [
        r"上万套周易教程请加微信[:：]?\s*\S+\s*也可直接进入\s*\S+",
        r"上万套周易教程请加微信[:：]?\s*\S*",
        r"也可直接进入\s*\S*",
        r"www\.265zhouyiw\.com",
        r"http[s]?://\S+",
        r"www\.\S+",
        r"微信[:：]?\s*\S+",
        r"QQ[:：]?\s*\d+",
        r"猫鼬魔法仪式小铺",
        r"图片取自http\S+",
        r"strc\.taobao\.com",
    ]

    for pattern in extra_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    text = re.sub(r"[\u0000-\u001f]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def has_enough_content(text: str) -> bool:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    punctuation = len(re.findall(r"[，。！？；：]", text))
    return chinese_chars >= 12 or (chinese_chars >= 8 and punctuation >= 2)


def is_mostly_noise(text: str) -> bool:
    if not text:
        return True
    if len(text) < 12:
        return True
    if re.fullmatch(r"[\W_]+", text):
        return True

    for pattern in LOW_VALUE_PATTERNS:
        if re.fullmatch(pattern, text, flags=re.IGNORECASE):
            return True

    return False


def clean_pdf_pages(data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned_pages: List[Dict[str, Any]] = []

    for page in data.get("pages", []):
        raw = page.get("text", "")
        cleaned_text = clean_line(raw)

        if is_mostly_noise(cleaned_text):
            continue
        if not has_enough_content(cleaned_text):
            continue

        cleaned_pages.append({
            "page_num": page["page_num"],
            "text": cleaned_text
        })

    return {
        "source_file": data["source_file"],
        "file_type": data["file_type"],
        "book_id": data["book_id"],
        "accepted": data.get("accepted", False),
        "quality": data.get("quality", "unknown"),
        "quality_stats": data.get("quality_stats", {}),
        "pages": cleaned_pages
    }


def clean_docx_paragraphs(data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned_paras: List[Dict[str, Any]] = []

    for para in data.get("paragraphs", []):
        raw = para.get("text", "")
        cleaned_text = clean_line(raw)

        if is_mostly_noise(cleaned_text):
            continue
        if not has_enough_content(cleaned_text):
            continue

        cleaned_paras.append({
            "para_num": para["para_num"],
            "text": cleaned_text
        })

    return {
        "source_file": data["source_file"],
        "file_type": data["file_type"],
        "book_id": data["book_id"],
        "accepted": data.get("accepted", False),
        "quality": data.get("quality", "unknown"),
        "quality_stats": data.get("quality_stats", {}),
        "paragraphs": cleaned_paras
    }


def main() -> None:
    json_files = list(INPUT_DIR.glob("*.json"))

    summary = {
        "processed": 0,
        "skipped_unaccepted": 0,
        "saved": 0,
        "details": []
    }

    for path in tqdm(json_files, desc="Cleaning extracted text"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data.get("accepted", False):
            summary["skipped_unaccepted"] += 1
            summary["details"].append({
                "source_file": data.get("source_file", path.name),
                "status": "skipped",
                "reason": data.get("reject_reason", "not_accepted")
            })
            continue

        summary["processed"] += 1

        if data["file_type"] == "pdf":
            cleaned = clean_pdf_pages(data)
            kept_units = len(cleaned["pages"])
        else:
            cleaned = clean_docx_paragraphs(data)
            kept_units = len(cleaned["paragraphs"])

        if kept_units == 0:
            summary["details"].append({
                "source_file": data.get("source_file", path.name),
                "status": "dropped_after_cleaning",
                "reason": "no_valid_units_left"
            })
            continue

        out_path = OUTPUT_DIR / path.name
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)

        summary["saved"] += 1
        summary["details"].append({
            "source_file": data.get("source_file", path.name),
            "status": "saved",
            "kept_units": kept_units
        })

    report_path = REPORT_DIR / "cleaning_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Saved cleaning report to: {report_path}")


if __name__ == "__main__":
    main()