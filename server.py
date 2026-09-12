"""学习档案助理 - FastAPI 后端（便携版）"""
import os
import sys

# 确保当前目录在 sys.path 中
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import uvicorn
import database as db
import ai_service

# 加载 .env 文件中的 API Key
load_dotenv(os.path.join(APP_DIR, '.env'))
API_KEY = os.getenv('DEEPSEEK_API_KEY', '')

app = FastAPI(title="学习档案助理 API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

db.init_database()

# ── Auth ──
@app.post("/api/auth/login")
def login(data: dict):
    ok, msg, uid, uname = db.login_user(data["username"], data["password"])
    if ok:
        return {"ok": True, "user_id": uid, "username": uname}
    return {"ok": False, "error": msg}

@app.post("/api/auth/register")
def register(data: dict):
    ok, msg, uid = db.register_user(data["username"], data["password"])
    if ok:
        return {"ok": True, "user_id": uid}
    return {"ok": False, "error": msg}

# ── Courses ──
@app.get("/api/courses")
def get_courses(user_id: int):
    return {"courses": db.get_all_courses(user_id)}

@app.post("/api/courses/add")
def add_course(data: dict):
    db.add_course(data["name"], data["user_id"])
    return {"ok": True}

# ── Records ──
@app.post("/api/records/grade")
def add_grade(data: dict):
    db.add_grade(data["user_id"], data["course_name"], data["score"],
                 data["total_score"], data["exam_type"], data["exam_date"],
                 data.get("notes", ""))
    return {"ok": True}

@app.post("/api/records/practice")
def add_practice(data: dict):
    db.add_practice(data["user_id"], data.get("course", ""),
                    data.get("platform", ""), data["count"],
                    data["correct"], data["duration"], data["date"],
                    data.get("topic", ""), data.get("notes", ""))
    return {"ok": True}

@app.post("/api/records/note")
def add_note(data: dict):
    db.add_note(data["user_id"], data.get("course", ""),
                data["title"], data["content"], data["date"])
    return {"ok": True}

@app.post("/api/records/mistake")
def add_mistake(data: dict):
    db.add_mistake(data["user_id"], data.get("course", ""),
                   data["question"], "",
                   data.get("correct_solution", ""), data.get("wrong_reason", ""),
                   "", data["date"], data.get("mastered", 0))
    return {"ok": True}

@app.get("/api/records")
def get_records(user_id: int):
    return {
        "grades": db.get_grades(user_id),
        "practices": db.get_practice_records(user_id),
        "notes": db.get_notes(user_id),
        "mistakes": db.get_mistakes(user_id),
    }

@app.delete("/api/records/{record_type}/{record_id}")
def delete_record(record_type: str, record_id: int):
    deleters = {
        "grade": db.delete_grade,
        "practice": db.delete_practice,
        "note": db.delete_note,
        "mistake": db.delete_mistake,
    }
    if record_type not in deleters:
        return {"ok": False, "error": f"未知记录类型: {record_type}"}
    deleters[record_type](record_id)
    return {"ok": True}

# ── Stats ──
def _parse_grade_ids(grade_ids_str: str = ""):
    if not grade_ids_str or not grade_ids_str.strip():
        return None
    ids = [int(x.strip()) for x in grade_ids_str.split(",") if x.strip().isdigit()]
    return ids if ids else None

@app.get("/api/stats")
def get_stats(user_id: int, grade_ids: str = ""):
    ids = _parse_grade_ids(grade_ids)
    return db.get_summary_stats(user_id, grade_ids=ids)

@app.get("/api/stats/report")
def get_report(user_id: int, grade_ids: str = ""):
    ids = _parse_grade_ids(grade_ids)
    data = db.get_all_data_for_ai(user_id, grade_ids=ids)
    return {"report": ai_service.generate_weekly_report(API_KEY, data)}

# ── AI ──
@app.get("/api/stats/diagnosis")
def get_diagnosis(user_id: int, grade_ids: str = ""):
    ids = _parse_grade_ids(grade_ids)
    data = db.get_all_data_for_ai(user_id, grade_ids=ids)
    return {"diagnosis": ai_service.diagnose_weaknesses(API_KEY, data)}

@app.get("/api/stats/plan")
def get_plan(user_id: int, grade_ids: str = ""):
    ids = _parse_grade_ids(grade_ids)
    data = db.get_all_data_for_ai(user_id, grade_ids=ids)
    return {"plan": ai_service.generate_study_plan(API_KEY, data)}

# ── Chat ──
@app.post("/api/chat")
def chat(data: dict):
    user_id = data.get("user_id", 1)
    all_data = db.get_all_data_for_ai(user_id)
    reply = ai_service.answer_question(API_KEY, all_data,
                                       data["message"],
                                       data.get("history", []))
    return {"reply": reply}

# ── Settings ──
ENV_PATH = os.path.join(APP_DIR, '.env')


def _save_env(key: str, value: str):
    """更新 .env 中的某个 key（保留其它行）。"""
    lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith(key + '='):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}\n")
    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)


@app.get("/api/settings/apikey")
def get_apikey():
    return {"has_key": bool(API_KEY)}


@app.post("/api/settings/apikey")
def set_apikey(data: dict):
    global API_KEY
    key = (data.get("api_key") or "").strip()
    if not key:
        return {"ok": False, "error": "API Key 不能为空"}
    _save_env("DEEPSEEK_API_KEY", key)
    API_KEY = key
    return {"ok": True, "has_key": True}

# ── Static files ──
FRONTEND_PATH = os.path.join(APP_DIR, "dist")

@app.get("/{path:path}")
async def serve_frontend(path: str):
    if path in ("", "index.html"):
        return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))
    fp = os.path.join(FRONTEND_PATH, path)
    if os.path.exists(fp):
        return FileResponse(fp)
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

if __name__ == "__main__":
    import socket

    PORT = 8501

    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    print("学习档案助理启动中...")
    print(f"   API Key: {'已配置' if API_KEY else '未配置（AI功能不可用）'}")

    if is_port_in_use(PORT):
        print(f"   [WARNING] 端口 {PORT} 已被占用，可能是上次未正常关闭")
        print(f"   [INFO] 请关闭占用该端口的程序，或重启电脑后重试")
        sys.exit(1)

    print(f"   访问地址 -> http://127.0.0.1:{PORT}")
    print("   （已取消自动打开浏览器，请手动在浏览器地址栏输入上方网址）")
    print()

    uvicorn.run(app, host="127.0.0.1", port=PORT)
