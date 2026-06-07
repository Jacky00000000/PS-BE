# PS-BE

个人网站后端 API，提供 AI 分身聊天机器人（DeepSeek）。

## 功能

- 公共聊天机器人：所有访客与同一个 AI 分身对话
- 记录所有问答到 `ChatbotRecord` 模型
- REST API：提问、查询全部、查询单条、删除

## 快速开始

### 1. 环境准备

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`，填入 `DEEPSEEK_API_KEY`。

编辑 `chatbot/prompts.py`，填入你的个人信息与回答风格。

### 2. 选择数据库

**本地 Docker PostgreSQL（默认）：**

```bash
docker compose up -d db
```

在 `.env` 中设置：

```env
USE_PROD_DATABASE=False
```

**连接 Render 生产数据库（从本机）：**

在 `.env` 中设置：

```env
USE_PROD_DATABASE=True
```

并确保已填写 `DATABASE_*_PROD` 或 `DATABASE_URL_EXTERNAL_PROD`。

### 3. 数据库迁移 & 启动服务

```bash
python manage.py migrate
python manage.py runserver
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chatbot/ask/` | 提问并获得 AI 回答 |
| GET | `/api/chatbot/records/` | 获取全部问答记录 |
| GET | `/api/chatbot/records/<uuid>/` | 获取单条记录 |
| DELETE | `/api/chatbot/records/<uuid>/` | 删除单条记录 |

### 提问示例

```bash
curl -X POST http://127.0.0.1:8000/api/chatbot/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "你是谁？"}'
```

## 部署到 Render

1. 创建 **PostgreSQL** 数据库
2. 创建 **Web Service**，连接本仓库
3. 在 Render 环境变量中设置（参考 `.env.example`）：
   - `DJANGO_SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app.onrender.com`
   - `DEEPSEEK_API_KEY`
   - `CORS_ALLOWED_ORIGINS=https://your-frontend.com`
4. Render 会自动注入 `DATABASE_URL`（链接 Postgres 后）
5. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
6. Start Command: `python manage.py migrate && gunicorn config.wsgi:application`

参考：[Render 文档](https://render.com/docs)

## 项目结构

```
PS-BE/
├── chatbot/              # 聊天机器人 app
│   ├── models.py         # ChatbotRecord 模型
│   ├── prompts.py        # AI 人设 prompt 配置
│   ├── services/         # DeepSeek 与业务逻辑
│   ├── views.py          # API 视图
│   └── urls.py
├── config/
│   ├── env.py            # 环境变量读取
│   ├── database.py       # 数据库连接切换逻辑
│   └── settings.py       # Django 配置
├── docker-compose.yml    # 本地 PostgreSQL
├── .env.example          # 环境变量模板
└── requirements.txt
```
