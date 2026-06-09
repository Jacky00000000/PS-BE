# PS-BE

个人网站后端 API，提供 AI 分身聊天机器人（DeepSeek）。

## 功能

- 公共聊天机器人：所有访客与同一个 AI 分身对话
- 记录所有问答到 `ChatbotRecord` 模型
- REST API：提问、查询全部、查询单条、删除
- Django Admin：在 `/admin/` 浏览与搜索聊天记录

## 系统架构

```
Client (HTTP)
    ↓
Views (APIView)          ← chatbot/views.py
    ↓
Serializers              ← 请求验证 / 响应序列化
    ↓
ChatbotService           ← 业务逻辑
    ↓
DeepSeekClient (httpx)   ← 调用 DeepSeek Chat Completions API
    ↓
ChatbotRecord (PostgreSQL)
```

- **Views**：处理 HTTP 请求，返回 JSON
- **ChatbotService**：校验问题、调用 AI、写入数据库
- **DeepSeekClient**：携带 `chatbot/prompts.py` 中的 system prompt 发起 API 请求
- **config/database.py**：按环境自动切换数据库连接

## 快速开始

### 1. 环境准备

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`，至少填入 `DEEPSEEK_API_KEY`。

编辑 `chatbot/prompts.py`，填入你的个人信息与回答风格。

### 2. 选择数据库

数据库连接按以下优先级解析（`config/database.py`）：

1. `DATABASE_URL` — Render 链接 Postgres 后自动注入（最高优先级）
2. `USE_PROD_DATABASE=True` — 使用 `DATABASE_URL_EXTERNAL_PROD` 或 `DATABASE_*_PROD`
3. 本地 Docker PostgreSQL（默认）

**本地 Docker PostgreSQL（默认）：**

```bash
docker compose up -d db
```

在 `.env` 中设置（`cp .env.example .env` 已包含默认值）：

```env
USE_PROD_DATABASE=False
DATABASE_HOST=localhost
DATABASE_PORT=5433
```

> 本地 Docker 将 PostgreSQL 映射到宿主机的 **5433** 端口（`docker-compose.yml`），请勿使用默认的 5432。

**连接 Render 生产数据库（从本机）：**

```env
USE_PROD_DATABASE=True
```

并确保已填写 `DATABASE_*_PROD` 或 `DATABASE_URL_EXTERNAL_PROD`。

### 3. 数据库迁移 & 启动服务

```bash
python manage.py migrate
python manage.py runserver
```

服务默认运行在 `http://127.0.0.1:8000`。

## API 端点

| 方法 | 路径 | 说明 | 成功状态码 |
|------|------|------|-----------|
| POST | `/api/chatbot/ask/` | 提问并获得 AI 回答 | `201 Created` |
| GET | `/api/chatbot/records/` | 获取全部问答记录 | `200 OK` |
| GET | `/api/chatbot/records/<uuid>/` | 获取单条记录 | `200 OK` |
| DELETE | `/api/chatbot/records/<uuid>/` | 删除单条记录 | `204 No Content` |

### 请求与响应

**提问（POST `/api/chatbot/ask/`）**

```json
{ "question": "你是谁？" }
```

- `question`：必填，最长 4000 字符，首尾空白自动去除
- 空问题返回 `400 Bad Request`
- DeepSeek API 失败返回 `502 Bad Gateway`

**响应格式（单条记录）**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "你是谁？",
  "answer": "我是...",
  "created_at": "2026-06-08T12:00:00+08:00"
}
```

### 提问示例

```bash
curl -X POST http://127.0.0.1:8000/api/chatbot/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "你是谁？"}'
```

## 环境变量

参考 `.env.example`（本地开发）和 `.env.prod.example`（Render 生产环境）。

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DJANGO_SECRET_KEY` | Django 密钥 | — |
| `DEBUG` | 调试模式 | `True` |
| `ALLOWED_HOSTS` | 允许的主机名（逗号分隔） | `localhost,127.0.0.1` |
| `USE_PROD_DATABASE` | 是否连接 Render 生产数据库 | `False` |
| `DATABASE_NAME` | 本地数据库名 | `ps_be` |
| `DATABASE_USER` | 本地数据库用户 | `ps_be` |
| `DATABASE_PASSWORD` | 本地数据库密码 | `ps_be` |
| `DATABASE_HOST` | 本地数据库主机 | `localhost` |
| `DATABASE_PORT` | 本地数据库端口 | `5433` |
| `DATABASE_URL` | Render 自动注入（优先于其他配置） | — |
| `DATABASE_*_PROD` | Render 生产数据库连接信息 | — |
| `DATABASE_URL_EXTERNAL_PROD` | Render 外部连接 URL（本机连接用） | — |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | — |
| `DEEPSEEK_MODEL` | 模型名称 | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_TIMEOUT` | 请求超时（秒） | `60` |
| `CORS_ALLOWED_ORIGINS` | 允许的前端来源（逗号分隔） | `http://localhost:3000,http://localhost:5173` |
| `CORS_ALLOW_CREDENTIALS` | 是否允许携带凭证 | `True` |

## 部署

### 部署到 Render

1. 创建 **PostgreSQL** 数据库
2. 创建 **Web Service**，连接本仓库
3. 在 Render 环境变量中设置（参考 `.env.prod.example`）：
   - `DJANGO_SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app.onrender.com`
   - `DEEPSEEK_API_KEY`
   - `CORS_ALLOWED_ORIGINS=https://your-frontend.com`
4. Render 会自动注入 `DATABASE_URL`（链接 Postgres 后，优先级最高）
5. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
6. Start Command: `python manage.py migrate && gunicorn config.wsgi:application`

参考：[Render 文档](https://render.com/docs)

### Docker 完整部署

使用 `docker-compose.prod.yml` 一键启动 Web + PostgreSQL：

```bash
cp .env.example .env
# 编辑 .env，设置 DEEPSEEK_API_KEY 等
docker compose -f docker-compose.prod.yml up -d --build
```

- Web 服务：`http://localhost:8000`
- 容器内自动执行 `migrate` 并以 gunicorn 启动
- `Dockerfile` 基于 Python 3.12，已包含 `collectstatic` 与 WhiteNoise 静态文件服务

## 项目结构

```
PS-BE/
├── chatbot/                  # 聊天机器人 app
│   ├── models.py             # ChatbotRecord 模型
│   ├── serializers.py        # 请求验证与响应序列化
│   ├── prompts.py            # AI 人设 prompt 配置
│   ├── services/
│   │   ├── chatbot_service.py    # 业务逻辑
│   │   └── deepseek_client.py    # DeepSeek API 客户端
│   ├── views.py              # API 视图
│   ├── urls.py               # 路由
│   ├── admin.py              # Django Admin 配置
│   └── migrations/
├── config/
│   ├── env.py                # 环境变量读取
│   ├── database.py           # 数据库连接切换逻辑
│   ├── settings.py           # Django 配置
│   ├── urls.py               # 根路由
│   └── wsgi.py
├── docker-compose.yml        # 本地 PostgreSQL
├── docker-compose.prod.yml   # Docker 完整部署（Web + DB）
├── Dockerfile
├── .env.example              # 本地开发环境变量模板
├── .env.prod.example         # Render 生产环境变量模板
└── requirements.txt
```
