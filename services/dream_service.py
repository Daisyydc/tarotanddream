from typing import Dict


def build_dream_query(dream_text: str) -> str:
    """
    把用户原始梦境描述整理成更适合检索的 query
    """
    query = (
        f"梦境描述：{dream_text}\n"
        f"请关注梦境关键词、象征意象、情绪状态与常见解释。"
    )
    return query


def start_dream_session(dream_text: str) -> Dict:
    return {
        "mode": "dream",
        "stage": "dream_analysis",
        "dream_text": dream_text,
    }