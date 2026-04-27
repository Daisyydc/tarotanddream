from pathlib import Path
import json
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


APP_DIR = Path(r"E:\Desktop\AIDM\project\tarot_dream_app")

TAROT_DIR = APP_DIR / "data" / "tarot"
DREAM_DIR = APP_DIR / "data" / "dream"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class LocalRetriever:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

        self.tarot_index = faiss.read_index(str(TAROT_DIR / "tarot_index.faiss"))
        self.dream_index = faiss.read_index(str(DREAM_DIR / "dream_index.faiss"))

        self.tarot_meta = json.loads((TAROT_DIR / "tarot_index_meta.json").read_text(encoding="utf-8"))
        self.dream_meta = json.loads((DREAM_DIR / "dream_index_meta.json").read_text(encoding="utf-8"))

    def _embed_query(self, query: str):
        vec = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return np.asarray(vec, dtype="float32")

    def _build_tarot_item(self, score: float, item: dict) -> dict:
        return {
            "score": float(score),
            "id": item.get("id"),
            "source": item.get("source"),
            "type": item.get("type"),
            "text": item.get("text"),
            "cards": item.get("cards"),
            "book_id": item.get("book_id"),
            "category": item.get("category"),
            "file_type": item.get("file_type"),
            "page_start": item.get("page_start"),
            "page_end": item.get("page_end"),
            "para_start": item.get("para_start"),
            "para_end": item.get("para_end"),
        }

    def _domain_bonus(self, item: dict, domain: str) -> float:
        text = (item.get("text") or "").lower()
        category = (item.get("category") or "").lower()
        bonus = 0.0

        domain_keywords = {
            "love": ["感情", "关系", "恋爱", "暧昧", "复合", "桃花", "恋人", "圣杯", "伴侣"],
            "career": ["工作", "事业", "职场", "方向", "机会", "升职", "合作", "权杖", "星币", "皇帝", "战车"],
            "study": ["学业", "考试", "学习", "论文", "申请", "复习", "老师", "隐士", "女祭司", "宝剑"],
            "family": ["家庭", "家人", "父母", "沟通", "责任", "相处"],
            "self": ["自己", "状态", "情绪", "焦虑", "迷茫", "恢复", "边界", "月亮", "星星", "节制"],
        }

        if domain in domain_keywords:
            hit_count = sum(1 for kw in domain_keywords[domain] if kw.lower() in text)
            bonus += 0.03 * hit_count

        if domain == "love" and ("cups" in text or "圣杯" in text or "恋人" in text):
            bonus += 0.04
        if domain == "career" and ("wands" in text or "权杖" in text or "pentacles" in text or "星币" in text):
            bonus += 0.04
        if domain == "study" and ("swords" in text or "宝剑" in text or "隐士" in text):
            bonus += 0.04

        if category:
            if domain == "love" and category in {"questioning", "reading_process"}:
                bonus += 0.01
            if domain == "career" and category in {"reading_process", "foundation"}:
                bonus += 0.01

        return bonus

    def _balanced_select(self, items: list[dict], final_k: int) -> list[dict]:
        relations = [x for x in items if x.get("type") == "tarot_relations"]
        cases = [x for x in items if x.get("type") == "tarot_case"]
        books = [x for x in items if x.get("type") == "tarot_book_chunk"]
        others = [x for x in items if x.get("type") not in {"tarot_relations", "tarot_case", "tarot_book_chunk"}]

        selected = []

        # 先每类拿一点，保证混合
        selected.extend(relations[:2])
        selected.extend(cases[:2])
        selected.extend(books[:2])

        # 再按剩余高分补齐
        merged_rest = relations[2:] + cases[2:] + books[2:] + others
        merged_rest = sorted(merged_rest, key=lambda x: x["score"], reverse=True)

        seen = set()
        deduped = []

        for item in selected + merged_rest:
            text = (item.get("text") or "").strip()
            if not text:
                continue
            if text in seen:
                continue
            seen.add(text)
            deduped.append(item)

        return deduped[:final_k]

    def search_tarot(self, query: str, top_k: int = 5, domain: str = "general"):
        # 先取更大的候选池，再做重排
        initial_k = max(12, top_k * 3)

        q = self._embed_query(query)
        scores, indices = self.tarot_index.search(q, initial_k)

        candidates = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            raw_item = self.tarot_meta[idx]
            item = self._build_tarot_item(score, raw_item)

            # 轻量领域加权
            item["score"] = item["score"] + self._domain_bonus(item, domain)
            candidates.append(item)

        # 重新按加权分数排序
        candidates.sort(key=lambda x: x["score"], reverse=True)

        # 平衡选取
        results = self._balanced_select(candidates, final_k=top_k)
        return results

    def search_dream(self, query: str, top_k: int = 5):
        q = self._embed_query(query)
        scores, indices = self.dream_index.search(q, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            item = self.dream_meta[idx]
            item = {
                "score": float(score),
                "id": item.get("id"),
                "type": item.get("type"),
                "text": item.get("text")
            }
            results.append(item)
        return results


if __name__ == "__main__":
    retriever = LocalRetriever()

    print("=== Tarot Test ===")
    tarot_results = retriever.search_tarot(
        "塔罗三张牌解读：正位太阳；逆位月亮；正位恋人\n请关注单牌含义、正逆位、三张牌组合关系。",
        top_k=5,
        domain="love"
    )
    for r in tarot_results:
        print("\n---")
        print("score:", r["score"])
        print("type:", r["type"])
        print("source:", r.get("source"))
        print(r["text"][:300])

    print("\n=== Dream Test ===")
    dream_results = retriever.search_dream("梦见自己在水里迷路，很慌张", top_k=3)
    for r in dream_results:
        print("\n---")
        print("score:", r["score"])
        print(r["text"][:300])