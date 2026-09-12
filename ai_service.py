import json
from openai import OpenAI


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"


def get_client(api_key):
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


def build_data_context(data: dict) -> str:
    """将数据库摘要转换为 AI 可读的文本上下文。"""
    parts = []

    parts.append("===== 数据总览 =====")
    s = data.get("summary", {})
    parts.append(f"课程数: {s.get('total_courses', 0)}")
    parts.append(f"成绩记录数: {s.get('total_grades', 0)}")
    parts.append(f"刷题记录数: {s.get('total_practice', 0)}")
    parts.append(f"总刷题量: {s.get('total_problems', 0)}，正确: {s.get('total_correct', 0)}")
    parts.append(f"笔记数: {s.get('total_notes', 0)}")
    parts.append(f"错题数: {s.get('total_mistakes', 0)}（未掌握: {s.get('unmastered_mistakes', 0)}）")

    grades = data.get("grades", [])
    if grades:
        parts.append("\n===== 成绩记录 =====")
        for g in grades[:50]:
            parts.append(
                f"- [{g['exam_date']}] {g['course_name']} {g['exam_type']}: "
                f"{g['score']}/{g['total_score']} ({g['score']/g['total_score']*100:.1f}%)"
                + (f" | 备注: {g['notes']}" if g.get("notes") else "")
            )

    practice = data.get("practice", [])
    if practice:
        parts.append("\n===== 刷题记录 =====")
        for p in practice[:50]:
            course = p.get("course_name") or "通用"
            acc = f"{p['correct_count']/p['problem_count']*100:.0f}%" if p["problem_count"] > 0 else "N/A"
            parts.append(
                f"- [{p['practice_date']}] {course} | {p.get('platform', '')} | "
                f"题量: {p['problem_count']}, 正确率: {acc}, "
                f"耗时: {p['duration_minutes']}min"
                + (f" | 专题: {p['topic']}" if p.get("topic") else "")
            )

    notes = data.get("notes", [])
    if notes:
        parts.append("\n===== 学习笔记 =====")
        for n in notes[:30]:
            course = n.get("course_name") or "通用"
            parts.append(f"- [{n['note_date']}] {course} | {n['title']}")
            if n.get("content"):
                parts.append(f"  摘要: {n['content'][:200]}")

    mistakes = data.get("mistakes", [])
    if mistakes:
        parts.append("\n===== 错题记录 =====")
        for m in mistakes[:30]:
            course = m.get("course_name") or "通用"
            status = "已掌握" if m.get("mastered") else "未掌握"
            parts.append(
                f"- [{m['mistake_date']}] {course} [{status}] | {m['problem_description'][:100]}"
                + (f" | 标签: {m['tags']}" if m.get("tags") else "")
            )

    return "\n".join(parts)


def generate_weekly_report(api_key: str, data: dict) -> str:
    """调用 DeepSeek API 生成周度学习复盘报告。"""
    if not api_key:
        return "⚠️ 未配置 DeepSeek API Key，请前往「设置」页面填写后即可使用 AI 功能。"

    context = build_data_context(data)

    prompt = f"""你是一位专业的学习教练。请基于以下学生的学习数据，生成一份周度学习复盘报告。

报告需包含以下板块：

📊 本周学习概览
用 2-3 句话总结本周整体学习状态

📈 成绩分析
分析各科成绩变化趋势，指出进步或退步的科目

🎯 刷题情况
总结刷题量、正确率，评估刷题效率

⚠️ 薄弱环节
从错题中诊断出哪些知识点掌握不牢，分析可能的原因

📝 学习习惯评估
根据数据评估学习节奏、时间分配是否合理

💡 下周建议
给出 3-5 条具体可执行的学习建议，建议重点复习的知识点

重要：请使用纯文本格式输出，每个板块标题单独一行，内容用自然段落表达。不要使用任何 Markdown 语法（不要用 # 号标记标题层级，不要用 * 或 - 符号作为列表标记，不要用 ** 加粗）。

学生学习数据如下：
{context}

请用中文撰写，语气鼓励但客观。如果某些数据不足，诚实指出并建议补充。"""

    try:
        client = get_client(api_key)
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一位经验丰富的学习教练，擅长分析学习数据并给出建设性建议。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=3000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI 报告生成失败：{str(e)}"


def answer_question(api_key: str, data: dict, question: str, chat_history: list = None) -> str:
    """基于学习数据回答用户的自然语言问题。"""
    if not api_key:
        return "⚠️ 未配置 DeepSeek API Key，请前往「设置」页面填写后即可使用 AI 功能。"

    context = build_data_context(data)

    messages = [
        {
            "role": "system",
            "content": (
                "你是一位贴心的学习助理，拥有该学生完整的学习档案数据。"
                "请基于提供的数据诚实、准确地回答用户的问题。"
                "如果数据不足以回答某个问题，请明确指出缺少哪些数据。"
                "用中文回答，语气友好、鼓励。"
                "回答时尽量引用具体数据（日期、分数、正确率等）。"
            ),
        },
        {"role": "user", "content": f"以下是该学生的学习数据：\n\n{context}"},
    ]

    if chat_history:
        messages.extend(chat_history)

    messages.append({"role": "user", "content": question})

    try:
        client = get_client(api_key)
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI 问答失败：{str(e)}"


def generate_study_plan(api_key: str, data: dict) -> str:
    """基于学习数据生成下一周学习计划。"""
    if not api_key:
        return "⚠️ 未配置 DeepSeek API Key，请前往「设置」页面填写后即可使用 AI 功能。"

    context = build_data_context(data)

    prompt = f"""你是一位专业的学习规划师。请基于以下学生的学习数据，制定一份**下一周学习计划**。

计划需要包含：
1. 每日学习重点（周一到周日）
2. 各科目时间分配建议
3. 针对薄弱知识点的专项训练建议
4. 刷题目标（数量和正确率）
5. 复习错题的安排

学生学习数据：
{context}

请用中文撰写，计划要具体、可执行、有量化指标。"""

    try:
        client = get_client(api_key)
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一位专业的学习规划师，擅长制定个性化学习计划。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=3000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 学习计划生成失败：{str(e)}"


def diagnose_weaknesses(api_key: str, data: dict) -> str:
    """诊断薄弱知识点和学习习惯问题。"""
    if not api_key:
        return "⚠️ 未配置 DeepSeek API Key，请前往「设置」页面填写后即可使用 AI 功能。"

    context = build_data_context(data)

    prompt = f"""你是一位学习诊断专家。请基于以下学生的学习数据，进行**薄弱知识点和学习习惯诊断**。

请从以下维度分析：
1. 知识薄弱点：从错题和成绩中识别出哪些具体知识点存在问题
2. 错误模式：分析常见的错误类型（概念不清、计算失误、审题不仔细等）
3. 学习习惯问题：从学习频率、时间分配、复习规律等方面诊断
4. 效率评估：刷题效率和成绩提升之间的关系
5. 改进优先级：按紧急程度排列需要优先解决的问题

学生学习数据：
{context}

请用中文撰写，语言专业但易懂，每个问题都要有数据支撑。"""

    try:
        client = get_client(api_key)
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一位学习诊断专家，擅长发现学习问题并给出精准诊断。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=3000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 诊断失败：{str(e)}"
