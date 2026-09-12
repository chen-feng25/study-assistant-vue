import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from database import get_grades, get_practice_records, get_mistakes, get_notes, get_summary_stats


def _to_dataframe(records: list) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


# ========== 成绩分析 ==========

def grade_trend_chart(grades: list):
    """成绩趋势折线图。"""
    if not grades:
        return None
    df = pd.DataFrame(grades)
    df["exam_date"] = pd.to_datetime(df["exam_date"])
    df["percentage"] = df["score"] / df["total_score"] * 100
    df = df.sort_values("exam_date")

    fig = px.line(
        df,
        x="exam_date",
        y="percentage",
        color="course_name",
        markers=True,
        title="成绩趋势图",
        labels={"exam_date": "日期", "percentage": "得分率 (%)", "course_name": "课程"},
    )
    fig.update_layout(height=400, hovermode="x unified")
    fig.update_yaxes(range=[0, 105])
    return fig


def grade_distribution_chart(grades: list):
    """各科成绩分布箱线图。"""
    if not grades:
        return None
    df = pd.DataFrame(grades)
    df["percentage"] = df["score"] / df["total_score"] * 100

    fig = px.box(
        df,
        x="course_name",
        y="percentage",
        color="course_name",
        title="各科成绩分布",
        labels={"course_name": "课程", "percentage": "得分率 (%)"},
    )
    fig.update_layout(height=400, showlegend=False)
    return fig


# ========== 刷题分析 ==========

def practice_accuracy_chart(records: list):
    """刷题正确率柱状图（按课程/专题）。"""
    if not records:
        return None
    df = pd.DataFrame(records)
    df["accuracy"] = df["correct_count"] / df["problem_count"] * 100
    df["accuracy"] = df["accuracy"].fillna(0)
    df["course_label"] = df["course_name"].fillna("通用")

    summary = df.groupby("course_label").agg(
        total_problems=("problem_count", "sum"),
        total_correct=("correct_count", "sum"),
    ).reset_index()
    summary["accuracy"] = summary["total_correct"] / summary["total_problems"] * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary["course_label"],
        y=summary["total_problems"],
        name="总题数",
        marker_color="lightblue",
    ))
    fig.add_trace(go.Bar(
        x=summary["course_label"],
        y=summary["total_correct"],
        name="正确题数",
        marker_color="green",
    ))
    fig.update_layout(
        title="各科刷题量与正确率",
        xaxis_title="课程",
        yaxis_title="题目数量",
        height=400,
        barmode="group",
    )
    return fig


def practice_heatmap(records: list):
    """刷题活跃度热力图（按周几和时段）。"""
    if not records:
        return None
    df = pd.DataFrame(records)
    df["practice_date"] = pd.to_datetime(df["practice_date"])
    df["weekday"] = df["practice_date"].dt.dayofweek
    df["weekday_name"] = df["weekday"].map({
        0: "周一", 1: "周二", 2: "周三", 3: "周四",
        4: "周五", 5: "周六", 6: "周日",
    })

    heatmap_data = df.groupby("weekday_name").agg(
        刷题次数=("id", "count"),
        总题量=("problem_count", "sum"),
    ).reindex(["周一", "周二", "周三", "周四", "周五", "周六", "周日"]).fillna(0)

    fig = px.imshow(
        [heatmap_data["总题量"].values],
        x=heatmap_data.index,
        y=["总题量"],
        title="每周刷题活跃度",
        labels={"x": "星期", "y": "", "color": "题量"},
        text_auto=True,
        aspect="auto",
    )
    fig.update_layout(height=200)
    return fig


# ========== 错题分析 ==========

def mistake_by_tag_chart(mistakes: list):
    """错题按标签分布饼图。"""
    if not mistakes:
        return None
    df = pd.DataFrame(mistakes)
    tag_counts = {}
    for tags_str in df["tags"].dropna():
        for tag in tags_str.replace("，", ",").split(","):
            tag = tag.strip()
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if not tag_counts:
        return None

    tag_df = pd.DataFrame({"标签": list(tag_counts.keys()), "数量": list(tag_counts.values())})
    tag_df = tag_df.sort_values("数量", ascending=False)

    fig = px.pie(
        tag_df,
        names="标签",
        values="数量",
        title="错题知识点分布",
        height=400,
    )
    return fig


def mistake_mastery_chart(mistakes: list):
    """错题掌握情况。"""
    if not mistakes:
        return None
    df = pd.DataFrame(mistakes)
    mastered = int((df["mastered"] == 1).sum())
    unmastered = int((df["mastered"] == 0).sum())

    fig = go.Figure(go.Pie(
        labels=["已掌握", "未掌握"],
        values=[mastered, unmastered],
        marker_colors=["green", "salmon"],
        hole=0.4,
    ))
    fig.update_layout(title="错题掌握情况", height=350)
    return fig


# ========== 周度摘要 ==========

def get_weekly_summary(user_id, days=7):
    """获取最近 N 天的摘要数据。"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    grades = get_grades(user_id, start_date, end_date)
    practice = get_practice_records(user_id, start_date, end_date)
    mistakes = get_mistakes(user_id, start_date, end_date)
    notes = get_notes(user_id, start_date, end_date)

    total_practice_problems = sum(r["problem_count"] for r in practice)
    total_practice_correct = sum(r["correct_count"] for r in practice)
    practice_accuracy = (
        total_practice_correct / total_practice_problems * 100
        if total_practice_problems > 0 else 0
    )

    return {
        "period": f"{start_date} ~ {end_date}",
        "grade_count": len(grades),
        "avg_score": (
            sum(g["score"] / g["total_score"] * 100 for g in grades) / len(grades)
            if grades else 0
        ),
        "practice_sessions": len(practice),
        "total_problems": total_practice_problems,
        "practice_accuracy": practice_accuracy,
        "new_notes": len(notes),
        "new_mistakes": len(mistakes),
        "unmastered_mistakes": sum(1 for m in mistakes if not m["mastered"]),
    }


# ========== 薄弱点文本摘要 ==========

def weak_points_summary(mistakes: list) -> str:
    """从错题中提取薄弱点文本摘要。"""
    if not mistakes:
        return "暂无错题数据，无法分析薄弱点。"

    df = pd.DataFrame(mistakes)
    unmastered = df[df["mastered"] == 0]

    lines = []
    lines.append(f"共 {len(mistakes)} 条错题记录，其中 {len(unmastered)} 条尚未掌握。")

    tag_counts = {}
    for tags_str in df["tags"].dropna():
        for tag in tags_str.replace("，", ",").split(","):
            tag = tag.strip()
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if tag_counts:
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        lines.append("\n高频错误知识点：")
        for tag, count in sorted_tags[:10]:
            lines.append(f"  - {tag}：{count} 次")

    return "\n".join(lines)
