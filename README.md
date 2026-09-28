# PaperPilot - 学术论文浏览平台

## 项目概述

PaperPilot 是一个基于 **FastAPI + Vue3** 的全栈学术论文浏览平台，数据来源于 arXiv / Semantic Scholar，提供论文分类浏览、收藏管理、阅读历史和 AI 智能问答等功能。项目采用前后端分离架构，后端使用 Python FastAPI 框架，前端使用 Vue3 + Vite 构建，面向移动端适配。

### 核心功能

- ✅ **用户系统**: 注册、登录、个人信息管理、头像上传（Base64）
- ✅ **论文浏览**: 按 arXiv 分类（cs.CV / cs.LG / cs.CL 等）浏览、分页加载、详情查看
- ✅ **收藏管理**: 添加收藏、取消收藏、收藏列表、一键清空
- ✅ **历史记录**: 浏览记录、单条删除、一键清空
- ✅ **AI 问答**: 基于 DeepSeek 大模型，支持流式 / 非流式响应
- ✅ **国际化**: 支持中文 / 英文切换
- ✅ **暗色模式**: 主题切换支持

---

## 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | >=3.11 | 编程语言 |
| **FastAPI** | >=0.136.1 | Web 框架，高性能异步 API |
| **SQLAlchemy** | >=2.0.49 | ORM 数据库操作框架 |
| **aiomysql** | >=0.3.2 | MySQL 异步驱动 |
| **Redis** | >=7.4.0 | 缓存系统，提升数据读取性能 |
| **Uvicorn** | >=0.46.0 | ASGI 服务器，运行 FastAPI 应用 |
| **Passlib[bcrypt]** | 1.7.4 | 密码加密与验证 |
| **Cryptography** | >=47.0.0 | 加密算法支持 |
| **HTTPX** | >=0.28.1 | 异步 HTTP 客户端，用于 AI 接口调用 |
| **python-dotenv** | - | 环境变量管理（AI API Key 等） |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue** | ^3.x | 前端渐进式框架 |
| **Vite** | ^7.1.6 | 前端构建工具 |
| **Vue Router** | ^4.5.1 | 路由管理 |
| **Pinia** | ^3.0.3 | 状态管理 |
| **Pinia PersistedState** | ^4.5.0 | Pinia 持久化插件 |
| **Vant** | ^4.9.21 | 移动端 UI 组件库 |
| **Axios** | ^1.12.2 | HTTP 请求库 |
| **Vue I18n** | ^9.8.0 | 国际化支持 |
| **Marked** | ^16.3.0 | Markdown 解析器（AI 回答渲染） |
| **DOMPurify** | ^3.2.7 | HTML 内容安全过滤 |

---

## 项目结构

```
myfastapi/
├── PaperPilot/                 # 后端项目根目录
│   ├── main.py                 # FastAPI 应用入口（CORS、路由挂载、异常处理）
│   ├── config/                 # 配置模块
│   │   ├── db_conf.py          # MySQL 异步数据库配置
│   │   ├── cache_conf.py       # Redis 缓存配置
│   │   └── ai_conf.py          # DeepSeek AI 服务配置（读取 .env）
│   ├── models/                 # SQLAlchemy 数据模型
│   │   ├── users.py            # 用户与令牌模型
│   │   ├── papers.py           # 论文与分类模型
│   │   ├── favourite.py        # 收藏记录模型
│   │   └── history.py          # 浏览历史模型
│   ├── schemas/                # Pydantic 数据验证模式
│   │   ├── users.py            # 用户请求/响应模式
│   │   ├── favorite.py         # 收藏相关模式
│   │   ├── history.py          # 历史记录模式
│   │   └── ai_chat.py          # AI 问答请求模式
│   ├── crud/                   # 数据库 CRUD 操作层
│   │   ├── users.py            # 用户增删改查
│   │   ├── papers.py           # 论文增删改查
│   │   ├── favorite.py         # 收藏操作
│   │   └── history.py          # 历史记录操作
│   ├── routers/                # API 路由层
│   │   ├── users.py            # 用户相关接口
│   │   ├── papers.py           # 论文相关接口
│   │   ├── favourite.py        # 收藏相关接口
│   │   ├── history.py          # 历史记录接口
│   │   └── ai_chat.py          # AI 问答接口（SSE 流式）
│   ├── cache/                  # 缓存操作层
│   │   └── papers_caches.py    # 论文分类与列表缓存逻辑
│   ├── utils/                  # 工具函数
│   │   ├── auth.py             # Token 认证（依赖注入）
│   │   ├── security.py         # 密码加密/验证
│   │   ├── response.py         # 统一响应格式封装
│   │   ├── Exception.py        # 自定义异常
│   │   └── Exception_handlers.py # 全局异常处理器
│   ├── docs/                   # 文档与数据迁移脚本
│   │   ├── semanticscholar_migration.sql # 数据库建表 SQL（含初始化数据）
│   │   ├── arxiv_ai_ml_papers.csv       # arXiv AI/ML 论文原始数据
│   │   └── import_to_db.py     # 论文数据导入脚本
│   └── .env                    # 环境变量（DeepSeek API Key 等）
│
├── xwzx-paper/                 # 前端项目根目录
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue        # 首页（分类 Tab 切换、论文列表）
│   │   │   ├── PaperDetail.vue # 论文详情（摘要、PDF 链接、相关推荐）
│   │   │   ├── Category.vue    # 分类页
│   │   │   ├── Login.vue       # 登录页
│   │   │   ├── Register.vue    # 注册页
│   │   │   ├── Favorite.vue    # 收藏页
│   │   │   ├── History.vue     # 历史页
│   │   │   ├── AIChat.vue      # AI 问答页（流式响应）
│   │   │   ├── My.vue          # 个人中心
│   │   │   ├── Profile.vue     # 个人资料（头像上传 Base64）
│   │   │   └── Settings.vue    # 设置页（语言、主题）
│   │   ├── components/         # 公共组件
│   │   │   ├── TabBar.vue      # 底部导航栏
│   │   │   ├── PaperItem.vue   # 论文列表项
│   │   │   └── HelloWorld.vue  # 示例组件
│   │   ├── store/              # Pinia 状态管理
│   │   │   ├── modules/
│   │   │   │   ├── papers.js   # 论文状态
│   │   │   │   ├── favorite.js # 收藏状态
│   │   │   │   └── history.js  # 历史状态
│   │   │   ├── user.js         # 用户状态
│   │   │   ├── theme.js        # 主题状态
│   │   │   ├── language.js     # 语言状态
│   │   │   └── index.js        # Store 入口
│   │   ├── router/             # 路由配置
│   │   ├── i18n/               # 国际化配置（zh-CN / en-US）
│   │   ├── config/
│   │   │   └── api.js          # API 地址与 AI 配置
│   │   ├── utils/
│   │   │   ├── paperCategories.js # 论文分类映射工具
│   │   │   └── papers.js       # 论文数据处理工具
│   │   ├── App.vue             # 根组件
│   │   ├── main.js             # 入口文件
│   │   └── style.css           # 全局样式
│   ├── package.json            # 依赖配置
│   └── vite.config.js          # Vite 配置
│
└── README.md
```

---

## 数据库设计

数据库名称：`papers_app`，MySQL 字符集 `utf8mb4`。

### 表结构概览

| 表名 | 说明 |
|------|------|
| `user` | 用户信息表 |
| `user_token` | 用户令牌表 |
| `paper_primary_category` | 论文分类表（对应 arXiv primary_category） |
| `papers` | 论文表（含 arXiv 论文 ID、标题、摘要、PDF URL 等） |
| `related_papers` | 相关论文关联表（推荐系统预留） |
| `favorite` | 收藏表 |
| `history` | 浏览历史表 |
| `ai_chat` | AI 聊天记录表（RAG 升级预留） |

### 核心表说明

#### 论文表 (papers)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 内部主键（自增） |
| paper_id | VARCHAR(64) | arXiv 原始论文 ID（唯一，用于去重，如 `2604.26951v1`） |
| title | VARCHAR(500) | 论文标题 |
| abstract | TEXT | 论文摘要 |
| pdf_url | VARCHAR(500) | PDF 下载链接 |
| arxiv_url | VARCHAR(500) | arXiv 页面链接 |
| first_author | VARCHAR(100) | 第一作者 |
| category_id | INT | 分类 ID（外键 → paper_primary_category） |
| submitted_at | TIMESTAMP | 论文提交时间 |

#### 论文分类表 (paper_primary_category)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 分类 ID（自增主键） |
| name | VARCHAR(50) | 分类代码（如 `cs.CV`、`cs.LG`、`cs.CL`） |
| sort_order | INT | 排序序号 |

支持的前端分类映射：

| 代码 | 名称 |
|------|------|
| cs.CV | Computer Vision |
| cs.LG | Machine Learning |
| cs.CL | Computation and Language (NLP) |
| cs.AI | Artificial Intelligence |
| cs.RO | Robotics |
| cs.IR | Information Retrieval |
| cs.NE | Neural and Evolutionary Computing |

---

## 系统架构

### 后端架构分层

```
┌─────────────────────────────────────┐
│         API Routes (routers/)       │  ← 路由层：定义 API 端点
├─────────────────────────────────────┤
│         CRUD (crud/)                │  ← 业务逻辑层：数据库操作
├─────────────────────────────────────┤
│         Models (models/)            │  ← 数据模型层：ORM 映射
├─────────────────────────────────────┤
│         Schemas (schemas/)          │  ← 数据验证层：Pydantic 校验
├─────────────────────────────────────┤
│         Cache (cache/)              │  ← 缓存层：Redis 操作
├─────────────────────────────────────┤
│         Utils (utils/)              │  ← 工具层：认证、加密、响应
├─────────────────────────────────────┤
│         Config (config/)            │  ← 配置层：数据库、缓存、AI
└─────────────────────────────────────┘
```

### 缓存策略

| 缓存类型 | 缓存键格式 | TTL | 说明 |
|----------|-----------|-----|------|
| 分类缓存 | `news:categories` | 7200s | 论文分类列表 |
| 列表缓存 | `news:papers_list{category_id}:{page}:{page_size}` | 1800s | 论文列表分页数据 |

### 认证流程

- 认证类型：Bearer Token（UUID）
- 请求头：`Authorization: Bearer <token>`
- Token 有效期：7 天
- 获取方式：登录或注册接口
- 密码加密：bcrypt

---

## 部署与运行

### 环境要求

| 项目 | 版本要求 |
|------|----------|
| Python | >=3.11 |
| MySQL | >=5.7 |
| Redis | >=6.0 |
| Node.js | >=16（前端） |

### 后端部署

#### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

#### 2. 配置数据库

编辑 `PaperPilot/config/db_conf.py`：

```python
DATABASE_URL = "mysql+aiomysql://用户名:密码@主机:端口/papers_app?charset=utf8mb4"
```

#### 3. 配置 Redis

编辑 `PaperPilot/config/cache_conf.py`：

```python
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
```

#### 4. 配置 AI 服务

编辑 `PaperPilot/.env`：

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_ENDPOINT=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_STREAM=True
DEEPSEEK_TIMEOUT=120
```

#### 5. 初始化数据库

```bash
# 创建数据库并执行迁移脚本
mysql -u root -p < PaperPilot/docs/semanticscholar_migration.sql
```

#### 6. 导入论文数据

```bash
# 使用导入脚本将 CSV 数据导入数据库
python PaperPilot/docs/import_to_db.py
```

#### 7. 启动服务

```bash
# 开发环境
uvicorn PaperPilot.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uvicorn PaperPilot.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署

#### 1. 安装依赖

```bash
cd xwzx-paper
npm install
```

#### 2. 配置 API 地址

编辑 `xwzx-paper/src/config/api.js`：

```javascript
export const apiConfig = {
  baseURL: 'http://127.0.0.1:8000',
}
```

#### 3. 启动开发服务器

```bash
npm run dev
```

#### 4. 生产构建

```bash
npm run build
```

构建产物在 `xwzx-paper/dist` 目录，可部署到 Nginx 等 Web 服务器。

---

## API 接口概览

### 基础规范

| 项目 | 说明 |
|------|------|
| 基础路径 | `/api` |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |

### 统一响应结构

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

### 接口列表

| 模块 | 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|------|
| 用户 | POST | `/api/user/register` | 用户注册 | ❌ |
| 用户 | POST | `/api/user/login` | 用户登录 | ❌ |
| 用户 | GET | `/api/user/info` | 获取用户信息 | ✅ |
| 用户 | PUT | `/api/user/update` | 更新用户信息 | ✅ |
| 用户 | PUT | `/api/user/password` | 修改密码 | ✅ |
| 论文 | GET | `/api/papers/categories` | 获取分类列表 | ❌ |
| 论文 | GET | `/api/papers/list` | 获取论文列表（分页） | ❌ |
| 论文 | GET | `/api/papers/detail` | 获取论文详情 | ❌ |
| 收藏 | GET | `/api/favorite/check` | 检查是否已收藏 | ✅ |
| 收藏 | POST | `/api/favorite/add` | 添加收藏 | ✅ |
| 收藏 | DELETE | `/api/favorite/remove` | 取消收藏 | ✅ |
| 收藏 | GET | `/api/favorite/list` | 收藏列表 | ✅ |
| 收藏 | DELETE | `/api/favorite/clear` | 清空收藏 | ✅ |
| 历史 | POST | `/api/history/add` | 添加浏览记录 | ✅ |
| 历史 | GET | `/api/history/list` | 历史列表 | ✅ |
| 历史 | DELETE | `/api/history/delete/{history_id}` | 删除单条记录 | ✅ |
| 历史 | DELETE | `/api/history/clear` | 清空历史 | ✅ |
| AI | POST | `/api/ai/chat` | AI 问答（支持流式） | ❌ |
