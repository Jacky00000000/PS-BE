## File Structure
```text
PS-BE/
├── manage.py                         # Django 專案管理入口
├── config/
│   ├── settings.py                   # Django 專案設定
│   ├── env.py                        # 環境變數讀取與管理
│   ├── database.py                   # 資料庫相關設定
│   ├── urls.py                       # 專案 URL 路由
│   ├── asgi.py                       
│   └── wsgi.py                       
├── chatbot/
│   ├── admin.py                      # Django Admin 設定
│   ├── apps.py                       # Chatbot Django App 設定
│   ├── constants.py                  # 共用常數
│   ├── models.py                     # 資料模型
│   ├── tests.py                      
│   ├── api/
│   │   ├── serializers.py             # API 資料驗證與序列化
│   │   ├── urls.py                    # Chatbot API 路由
│   │   └── views.py                   # API 請求處理
│   ├── application/
│   │   └── chat_service.py            # 問答應用服務
│   ├── llm/
│   │   ├── agent.py                   # LLM Agent 與工具呼叫流程
│   │   ├── exceptions.py              # LLM 相關例外
│   │   ├── messages.py                # 對話訊息處理
│   │   ├── model.py                   # 聊天模型建立
│   │   ├── prompts.py                 # 系統提示詞
│   ├── retrieval/                     # 資料檢索功能
│   ├── tools/
│   │   ├── registry.py                # Agent 工具註冊
│   │   └── web_search.py              # 網路搜尋工具
│   └── migrations/
│       └── 0001_initial.py            # 初始資料庫 migration
├── Dockerfile                         
├── docker-compose.yml                 
├── requirements.txt                   
├── README.md                          
└── docs/
    └── project-documentation.md       
```

## 每個檔案中的詳細功能與 function



