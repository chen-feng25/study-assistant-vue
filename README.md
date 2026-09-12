# 学习档案助理（Study Assistant）

面向学生的个人学习档案管理工具，帮助你记录成绩、刷题、笔记与错题，并通过 AI 生成学习复盘、诊断薄弱点、制定学习计划。

## ✨ 功能

- **账户系统**：注册 / 登录，数据按用户隔离
- **成绩记录**：录入各科考试 / 测验成绩，自动计算百分比与趋势
- **刷题记录**：记录刷题量、正确率、耗时与专题，评估刷题效率
- **学习笔记**：按课程归档学习笔记
- **错题本**：记录错题、错误原因与正解，标记是否已掌握
- **数据统计**：总览 + 成绩趋势图表（Chart.js）
- **AI 能力**（需 DeepSeek API Key）：
  - 📊 周度学习复盘报告
  - ⚠️ 薄弱知识点诊断
  - 🎯 下一周学习计划
  - 💬 基于学习数据的 AI 问答

## 🛠 技术栈

- **前端**：Vue 3 + Vite + Vue Router + Chart.js（纯 CSS 动画，无 UI 框架）
- **后端**：FastAPI + SQLite
- **AI**：DeepSeek API（`deepseek-chat`）
- **端口**：`8501`

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+（仅前端开发 / 构建需要）

### 1. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python server.py
```

Windows 用户可直接双击 `启动.bat`。

启动后，手动在浏览器打开：

```
http://127.0.0.1:8501
```

> 服务**不会自动打开浏览器**，请手动输入上述地址访问。

### 3. 前端开发（可选）

```bash
npm install
npm run dev        # 开发模式
npm run build      # 生产构建，产物输出到 dist/（由 server.py 直接托管）
```

## 🔑 配置 AI 功能

1. 启动后访问首页，进入 **「设置」** 页面，粘贴你的 DeepSeek API Key 保存即可（**无需重启服务**）。
2. 或者手动在项目根目录创建 `.env` 文件，写入：

   ```
   DEEPSEEK_API_KEY=sk-你的key
   ```

   然后重启服务。

获取 API Key：<https://platform.deepseek.com/api_keys>

> 不配置 Key 也不影响基础功能（数据录入、查询、统计等）；仅 AI 功能不可用。

## 💾 数据存储

所有数据保存在项目根目录的 `learning_archive.db`（SQLite）。备份数据时复制该文件即可。

> 该文件已被 `.gitignore` 忽略，不会被提交到版本库。

## ⚠️ 安全说明

本项目设计为**本地 / 单用户**使用。当前认证仅校验用户名密码，登录后由前端保存 `user_id`，后端各接口直接信任客户端传入的 `user_id`，**没有服务端会话 / Token 校验**。

因此请勿直接将服务暴露到公网；如需多人或公网部署，请自行补充真正的鉴权（如 JWT / Session）。

## 📁 项目结构

```
study-assistant-vue/
├── server.py          # FastAPI 后端入口
├── ai_service.py      # DeepSeek AI 调用封装
├── database.py        # SQLite 数据访问层
├── requirements.txt   # Python 依赖
├── start.sh           # Linux / macOS 启动脚本
├── 启动.bat           # Windows 启动脚本
└── src/               # Vue 前端源码
    ├── api/           # 后端 API 封装
    ├── components/    # 组件（Sidebar、GradeTrendChart 等）
    ├── router/        # 路由
    ├── styles/        # 主题样式（CSS 变量驱动的日系风格）
    └── views/         # 页面（Login / Entry / Chat / Report / Settings）
```

## 📄 License

[MIT](./LICENSE)
