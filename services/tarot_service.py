import random
from typing import Dict, List


MAJOR_ARCANA_CN = [
    "愚人", "魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人", "战车", "力量", "隐士",
    "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳",
    "审判", "世界"
]

CARD_NAME_MAP = {
    "愚人": "The Fool",
    "魔术师": "The Magician",
    "女祭司": "The High Priestess",
    "皇后": "The Empress",
    "皇帝": "The Emperor",
    "教皇": "The Hierophant",
    "恋人": "The Lovers",
    "战车": "The Chariot",
    "力量": "Strength",
    "隐士": "The Hermit",
    "命运之轮": "Wheel of Fortune",
    "正义": "Justice",
    "倒吊人": "The Hanged Man",
    "死神": "Death",
    "节制": "Temperance",
    "恶魔": "The Devil",
    "高塔": "The Tower",
    "星星": "The Star",
    "月亮": "The Moon",
    "太阳": "The Sun",
    "审判": "Judgement",
    "世界": "The World",
}


def make_card(card_name_cn: str) -> str:
    orientation = "逆位" if random.randint(0, 1) == 1 else "正位"
    return f"{orientation}{card_name_cn}"


def extract_base_name(card_text: str) -> str:
    return card_text.replace("正位", "").replace("逆位", "").strip()


def translate_card_name(card_text: str) -> str:
    base_name = extract_base_name(card_text)
    orientation = "Reversed" if card_text.startswith("逆位") else "Upright"
    en_name = CARD_NAME_MAP.get(base_name, base_name)
    return f"{orientation} {en_name}"


def build_group(cards_3: List[str]) -> Dict[str, str]:
    cards = [make_card(card) for card in cards_3]
    return {
        "signpost": cards[0],
        "cards": cards,
        "cards_text": "，".join(cards)
    }


def draw_tarot_groups() -> Dict[str, Dict[str, str]]:
    shuffled = random.sample(MAJOR_ARCANA_CN, 9)

    group_a = build_group(shuffled[0:3])
    group_b = build_group(shuffled[3:6])
    group_c = build_group(shuffled[6:9])

    return {
        "A": group_a,
        "B": group_b,
        "C": group_c
    }


def build_signposts(groups: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    return {
        "A": groups["A"]["signpost"],
        "B": groups["B"]["signpost"],
        "C": groups["C"]["signpost"],
    }


def build_tarot_query(cards_text: str) -> str:
    cards = [c.strip() for c in cards_text.split("，") if c.strip()]
    translated = [translate_card_name(c) for c in cards]

    cn_part = "；".join(cards)
    en_part = "；".join(translated)

    query = (
        f"塔罗三张牌解读：{cn_part}\n"
        f"Tarot three-card reading: {en_part}\n"
        f"请关注单牌含义、正逆位、三张牌组合关系。"
    )
    return query


def detect_question_domain(question: str) -> str:
    q = question.lower().strip()

    love_keywords = [
        "感情", "情感", "爱情", "恋爱", "暧昧", "复合", "关系", "对象", "喜欢",
        "前任", "桃花", "脱单", "告白", "分手", "在一起", "他", "她", "我们"
    ]
    career_keywords = [
        "工作", "事业", "职业", "offer", "面试", "跳槽", "升职", "发展",
        "创业", "职场", "项目", "上班", "同事", "老板"
    ]
    study_keywords = [
        "学业", "考试", "成绩", "学习", "论文", "毕业", "申请", "留学",
        "复习", "老师", "读书"
    ]
    family_keywords = [
        "家庭", "家人", "父母", "亲人", "家里", "相处", "沟通"
    ]
    self_keywords = [
        "自己", "状态", "情绪", "内耗", "焦虑", "迷茫", "成长", "压力",
        "恢复", "低落", "我怎么了", "我最近怎么"
    ]

    if any(k in q for k in love_keywords):
        return "love"
    if any(k in q for k in career_keywords):
        return "career"
    if any(k in q for k in study_keywords):
        return "study"
    if any(k in q for k in family_keywords):
        return "family"
    if any(k in q for k in self_keywords):
        return "self"
    return "general"


def start_tarot_session(question: str) -> Dict:
    groups = draw_tarot_groups()
    signposts = build_signposts(groups)

    return {
        "mode": "tarot",
        "stage": "choose_group",
        "question": question,
        "signposts": signposts,
        "groups": {
            "A": {
                "signpost": groups["A"]["signpost"],
                "cards_text": groups["A"]["cards_text"]
            },
            "B": {
                "signpost": groups["B"]["signpost"],
                "cards_text": groups["B"]["cards_text"]
            },
            "C": {
                "signpost": groups["C"]["signpost"],
                "cards_text": groups["C"]["cards_text"]
            },
        },
        "selected_group": "",
        "tried_groups": []
    }