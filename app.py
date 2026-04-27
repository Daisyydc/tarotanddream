from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from services.tarot_service import (
    start_tarot_session,
    build_tarot_query,
    detect_question_domain,
)
from services.dream_service import start_dream_session, build_dream_query
from services.llm_service import generate_text
from rag.retriever import LocalRetriever

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Tarot Dream App API")
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

retriever = LocalRetriever()

class TarotConfirmRequest(BaseModel):
    session_id: str
    question: str
    group: str
    cards_text: str

class TarotStartRequest(BaseModel):
    question: str


class TarotSelectRequest(BaseModel):
    session_id: str
    question: str
    group: str
    cards_text: str


class DreamAnalyzeRequest(BaseModel):
    dream_text: str


@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/tarot/start")
def tarot_start(req: TarotStartRequest):
    session = start_tarot_session(req.question)
    session_id = str(uuid4())

    tarot_refs = {}
    for group_name, group_data in session["groups"].items():
        query = build_tarot_query(group_data["cards_text"])
        results = retriever.search_tarot(query, top_k=2)
        tarot_refs[group_name] = results

    system_prompt = """
你是一位温和、友好、有仪式感的塔罗引导者。
你的任务是在用户提出问题后，向用户展示三组指示牌，并邀请他们凭第一直觉做出选择。

要求：
1. 语气温和、自然，不要吓人，不要过度神秘化。
2. 不要直接下结论，不要提前解读完整牌意。
3. 不要使用过于绝对或负面的表达。
4. 让用户感到被陪伴、被引导，而不是被命令。
5. 输出简洁，有一点仪式感，但不要太夸张。
"""

    user_prompt = f"""
用户的问题是：
{session["question"]}

现在前端会展示三张不同的牌面图片，对应 A、B、C 三组。
请不要透露任何具体牌名，也不要暗示是哪张牌。

请生成一段温和自然的引导文案，邀请用户凭第一直觉从 A、B、C 三组中选择一组。

要求：
1. 不要出现任何具体牌名。
2. 不要说“某组对应什么牌”。
3. 只强调“第一眼感受”“哪一张更吸引你”“先别分析”。
4. 保持一点仪式感，但不要夸张。
"""

    assistant_message = generate_text(system_prompt, user_prompt, temperature=0.7)

    return {
        "session_id": session_id,
        "mode": "tarot",
        "stage": session["stage"],
        "question": session["question"],
        "groups": {
            "A": {
                "signpost": session["groups"]["A"]["signpost"],
                "cards_text": session["groups"]["A"]["cards_text"],
                "references": tarot_refs["A"],
            },
            "B": {
                "signpost": session["groups"]["B"]["signpost"],
                "cards_text": session["groups"]["B"]["cards_text"],
                "references": tarot_refs["B"],
            },
            "C": {
                "signpost": session["groups"]["C"]["signpost"],
                "cards_text": session["groups"]["C"]["cards_text"],
                "references": tarot_refs["C"],
            },
        },
        "assistant_message": assistant_message
    }


@app.post("/api/tarot/select")
def tarot_select(req: TarotSelectRequest):
    domain = detect_question_domain(req.question)

    query = build_tarot_query(req.cards_text)
    results = retriever.search_tarot(query, top_k=4)

    reference_text = "\n\n".join(
        [f"{i+1}. {item['text']}" for i, item in enumerate(results)]
    )

    system_prompt = """
你是一位温和、细腻、很会做“信息对应验证”的塔罗解读者。

你的任务不是做最终解牌，而是帮助用户快速判断：
“这组牌是不是在描述我当前的现实状态？”

请严格遵守以下规则：
1. 语气温和、友好，不要吓人，不要过于绝对。
2. 不要写成大段抽象分析，不要大量使用“能量、课题、宇宙、命运”等空泛词。
3. 必须优先贴近用户问题所属领域来写，不要跑题到别的领域。
4. 输出格式固定为三部分：

【整体感觉】
用1到2句话概括，这组牌更像在回应什么状态。

【可能的现实表现】
列出 3 到 4 条，尽量生活化、具体、容易判断。
每条都用“你最近可能会……”“比如……”“有些人会表现为……”这种自然说法。

【收口引导】
最后用1句话温和收尾：
如果这些描述让你有共鸣，我们再继续深入；如果不太像，也可以换一组看看。

5. 如果用户问题是：
- love：只能优先写感情、暧昧、关系推进、拉扯、联系、距离感、态度变化，不要跑到工作学业。
- career：只能优先写工作、方向、机会、选择、压力、节奏、合作，不要跑到感情。
- study：只能优先写学习状态、考试、论文、申请、推进，不要跑到感情工作。
- family：只能优先写家庭互动、沟通、距离感、责任分配。
- self：只能优先写情绪、状态、内耗、恢复、边界、自我整理。
- general：写通用现实表现，但也不要乱跳主题。
6. 验证阶段不要给最终结论，不要说“就是这样”，只说“更像”“可能”“常见表现为”。
"""

    user_prompt = f"""
用户最初的问题：
{req.question}

问题主题类别：
{domain}

用户当前选中的牌组：
{req.group}组：{req.cards_text}

检索到的参考内容：
{reference_text}

请生成一段“信息对应验证”文案。

额外要求：
1. 严格围绕【{domain}】这个主题写，不要串到别的主题。
2. 如果主题是 love，就绝对不要写工作、事业、职场、项目、升职这类内容。
3. 如果主题是 career，就绝对不要写恋爱、关系、暧昧、前任这类内容。
4. 不要写太长，总长度尽量控制在 250 到 400 字左右。
5. 不要用小标题以外的 markdown，不要加星号，不要输出 \\n 这样的转义感写法。
6. 让用户看完后能快速判断“像不像我现在的情况”。
"""


    verification_message = generate_text(system_prompt, user_prompt, temperature=0.7)

    return {
        "session_id": req.session_id,
        "mode": "tarot",
        "stage": "verify_group",
        "selected_group": req.group,
        "domain": domain,
        "cards_text": req.cards_text,
        "references": results,
        "verification_message": verification_message
    }


@app.post("/api/tarot/confirm")
def tarot_confirm(req: TarotConfirmRequest):
    domain = detect_question_domain(req.question)

    query = build_tarot_query(req.cards_text)
    results = retriever.search_tarot(query, top_k=4)

    reference_text = "\n\n".join(
        [f"{i+1}. {item['text']}" for i, item in enumerate(results)]
    )

    system_prompt = """
你是一位温和、细腻、具有现实感的塔罗解读者。
现在用户已经确认，这组牌与自己当前状态有共鸣。
你的任务是基于用户问题、牌组和参考内容，给出一段完整但不过度冗长的最终解读。

请严格遵守以下要求：
1. 语气温和、友好，不要吓人，不要太绝对。
2. 不要使用“注定”“一定会”“绝不会”这类表达。
3. 不要写得太满，不要过度拔高，也不要过度正能量。
4. 解读要贴近现实，少用空泛词，比如“宇宙、命运安排、课题”等。
5. 输出固定分成四部分：
   【当前状态】
   【这组牌想提醒你的重点】
   【接下来可能的发展】
   【给你的建议】
6. 每一部分控制在 2 到 4 句，总体简洁清楚。
7. “发展”要写成一种可能趋势，而不是命运宣判。
8. “建议”要温和、具体、可执行，给人安定感。
9. 尤其在感情相关内容中，避免刺激性、否定性、过度悲观的措辞。
"""

    user_prompt = f"""
用户最初的问题：
{req.question}

问题主题类别：
{domain}

用户已确认有共鸣的牌组：
{req.group}组：{req.cards_text}

检索到的参考内容：
{reference_text}

请基于这些内容，生成一段完整但温和的最终解读。

要求：
- 如果主题是 love，就围绕关系状态、互动方式、情绪变化、推进节奏来写；
- 如果主题是 career，就围绕工作状态、节奏、方向、选择、合作来写；
- 如果主题是 study，就围绕学习状态、推进、压力、方法调整来写；
- 如果主题是 family，就围绕家庭互动、沟通、责任与情绪来写；
- 如果主题是 self，就围绕情绪状态、自我整理、内耗、恢复来写；
- 如果主题是 general，就写成通用但贴近现实的解读；
- 整体控制在 300 到 500 字左右；
- 不要把结果说得太满，尽量保留“可能、逐渐、比较像、接下来有机会”这样的柔和表达。
"""

    final_reading = generate_text(system_prompt, user_prompt, temperature=0.7)

    return {
        "session_id": req.session_id,
        "mode": "tarot",
        "stage": "final_reading",
        "selected_group": req.group,
        "domain": domain,
        "cards_text": req.cards_text,
        "references": results,
        "final_reading": final_reading
    }




@app.post("/api/dream/analyze")
def dream_analyze(req: DreamAnalyzeRequest):
    session = start_dream_session(req.dream_text)
    query = build_dream_query(session["dream_text"])
    results = retriever.search_dream(query, top_k=3)

    reference_text = "\n\n".join(
        [f"{i+1}. {item['text']}" for i, item in enumerate(results)]
    )

    system_prompt = """
你是一位温和、友好、善于安抚情绪的解梦助手。
你的任务是基于提供的参考内容，对用户的梦境做一段自然、易懂、不过度绝对化的解释。

要求：
1. 语气要温和、友好，不要吓人，不要下很重的结论。
2. 不要使用“必然”“一定”“注定”等过于绝对的词。
3. 尽量把解释说得像一种可能的心理状态或情绪提醒。
4. 可以适度给出安抚性、引导性的表达。
5. 输出控制在一段到两段之间，不要太长。
"""

    user_prompt = f"""
用户梦境描述：
{session["dream_text"]}

检索到的参考内容：
{reference_text}

请基于这些内容，生成一段温和、自然、友好的解梦说明。
"""

    assistant_message = generate_text(system_prompt, user_prompt, temperature=0.7)

    return {
        "session_id": str(uuid4()),
        "mode": "dream",
        "stage": session["stage"],
        "dream_text": session["dream_text"],
        "references": results,
        "assistant_message": assistant_message
    }