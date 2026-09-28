# Paper 阅读平台 API 接口规范

## 1. 概述

本文档定义现有 Vue 前端需要的后端接口，覆盖 paper 列表/分类/详情、用户账户、收藏和浏览历史。该项目的主内容是论文，不提供新闻 API。

## 2. 基础约定

### 2.1 基础 URL

前端当前配置：

```text
http://127.0.0.1:8000
```

生产环境应使用可从浏览器访问的 API 域名，并通过环境配置替换基础 URL。

### 2.2 JSON 响应结构

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

业务错误响应示例：

```json
{
  "code": 404,
  "message": "Paper not found",
  "data": null
}
```

建议 HTTP 状态码与结果一致：未认证/无权限 `401`/`403`，资源不存在 `404`，参数错误 `422`，冲突 `409`，未预期服务错误 `500`。前端以 HTTP 成功且 `code === 200` 作为业务成功。

时间采用 ISO 8601 格式；分页页码从 1 开始。除特别说明外，列表都返回 `{ "list": [], "total": 0, "hasMore": false }`。

### 2.3 论文标识

- `paperId`、详情查询参数 `id` 和论文对象的 `id` 均表示稳定的论文标识，建议取数据库 `papers.paper_id`（arXiv 字符串 ID）。
- `paper_id` 保留数据库/CSV 的原始字段形式。
- 收藏记录的 `id`/`favoriteId`、浏览记录的 `historyId` 是关系记录标识，不得替代论文 `id`。
- 收藏/历史列表推荐返回 `{ ..., "paper": {论文对象} }`，并在关系对象上单独返回时间和关系记录 ID。

### 2.4 认证

登录后，受保护请求使用前端现行格式：

```http
Authorization: <token>
```

当前客户端不发送 `Bearer ` 前缀。所有受保护操作必须从 token 解析用户身份，禁止使用请求 body/query 中的 user ID 作为授权依据。

## 3. 论文模块

论文数据来自现有 `papers` 和 `paper_primary_category` 表。导入字段依据 `import_to_db.py`：`paper_id`、`title`、`abstract`、`first_author`、`primary_category`、`submitted_date`、`arxiv_url`、`pdf_url`。具体 SQL 列/外键类型应以项目 migration 和实际数据库为准。

### 3.1 获取分类

```http
GET /api/papers/categories
```

无需认证。接口返回数据库中实际存在的分类，不硬编码新闻分类。当前前端空数据/接口不可用时默认显示 7 个 paper 分类；后端接通后前端以 API 数据为准。

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "Computer Vision",
      "code": "cs.CV"
    },
    {
      "id": 2,
      "name": "Machine Learning",
      "code": "cs.LG"
    }
  ]
}
```

`code` 是可选字段：importer 目前将友好名称写入分类表，若 code 没有保存或不能可靠映射，应省略而不是猜测。`id` 应为分类表 ID；`name` 应与数据库分类名称一致。

### 3.2 获取论文列表

```http
GET /api/papers/list
```

无需认证。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---:|---|
| `categoryId` | integer 或 string | 否 | 无 | 数据库分类 ID；前端默认 fallback 分类时会使用 arXiv code 字符串 |
| `categoryCode` | string | 否 | 无 | arXiv 分类 code，可能由前端同时发送 |
| `page` | integer | 否 | 1 | 页码，最小 1 |
| `pageSize` | integer | 否 | 10 | 每页条数，建议限制最大 100 |

分类筛选规则：

1. 若 `categoryId` 是数据库中存在的分类 ID，按该分类查询。
2. 若 `categoryId` 是已知 arXiv code 字符串，可按数据库可验证的分类映射查询。
3. `categoryCode` 可用于补充明确的分类 code；不得让无效分类参数静默变成全量查询。
4. 没有分类参数时返回所有论文。

请求示例：

```http
GET /api/papers/list?page=1&pageSize=10
GET /api/papers/list?categoryId=1&categoryCode=cs.CV&page=2&pageSize=10
GET /api/papers/list?categoryId=cs.CV&page=1&pageSize=10
```

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "2301.01234",
        "paper_id": "2301.01234",
        "title": "Example Paper Title",
        "abstract": "Paper abstract...",
        "first_author": "Example Author",
        "submitted_at": "2023-01-03",
        "category_id": 1,
        "category_name": "Computer Vision",
        "pdf_url": "https://arxiv.org/pdf/2301.01234",
        "arxiv_url": "https://arxiv.org/abs/2301.01234"
      }
    ],
    "total": 1,
    "hasMore": false
  }
}
```

列表项应包含前端用到的字段。若数据库保存 `submitted_date`，响应可使用该字段，也可映射为 `submitted_at`；作者映射 `first_author`，分类名称映射 `category_name`。按稳定排序（例如提交日期倒序，再按 paper ID）分页，避免翻页重复或漏项。

### 3.3 获取论文详情

```http
GET /api/papers/detail?id=<paper_id>
```

无需认证。`id` 是论文标识（建议 paper_id 字符串），不是分类 ID、favorite ID 或 history ID。

请求示例：

```http
GET /api/papers/detail?id=2301.01234
```

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "2301.01234",
    "paper_id": "2301.01234",
    "title": "Example Paper Title",
    "abstract": "Paper abstract...",
    "first_author": "Example Author",
    "submitted_at": "2023-01-03",
    "category_id": 1,
    "category_name": "Computer Vision",
    "pdf_url": "https://arxiv.org/pdf/2301.01234",
    "arxiv_url": "https://arxiv.org/abs/2301.01234"
  }
}
```

不存在的 paper 返回 HTTP `404` 和非成功 `code`。

### 3.4 PDF 交付

详情 JSON 提供数据库中的 `pdf_url`。前端将 URL 设置为 iframe `src`，由用户浏览器直接请求 PDF；后端无需将 PDF 转为 JSON/base64。

- URL 必须从客户端所在设备可访问；生产环境不要返回仅容器内部可解析的 host。
- 直链应指向 PDF，源站允许浏览器访问并返回 `Content-Type: application/pdf`。
- 源站可通过 `X-Frame-Options` / CSP 禁止 iframe 展示；这是源站策略导致，详情页会提供新窗口打开链接。
- 详情页可在 `pdf_url` 为空时从可信的 arXiv `/abs/<id>` URL 构造 `/pdf/<id>`。后端仍应优先返回数据库 `pdf_url`。
- 若未来增加代理下载，使用独立流式端点，只允许服务端白名单域名，禁止代理客户端任意 URL，以避免 SSRF。

## 4. 用户管理模块（保留现有账户功能）

### 4.1 注册

```http
POST /api/user/register
Content-Type: application/json
```

请求：

```json
{
  "username": "example_user",
  "password": "example_password"
}
```

成功响应（注册后前端自动登录）：

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "opaque-access-token",
    "userInfo": {
      "id": 1,
      "username": "example_user",
      "nickname": null,
      "avatar": null,
      "bio": ""
    }
  }
}
```

用户名已存在返回 `409`；密码只存哈希。

### 4.2 登录

```http
POST /api/user/login
Content-Type: application/json
```

请求字段与注册相同。成功响应结构与注册相同。凭据错误返回 `401`，不要区分用户名不存在和密码错误。

### 4.3 获取用户信息

```http
GET /api/user/info
Authorization: <token>
```

成功 `data` 为用户对象：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "example_user",
    "nickname": null,
    "avatar": null,
    "gender": "unknown",
    "bio": ""
  }
}
```

### 4.4 更新用户资料

```http
PUT /api/user/update
Authorization: <token>
Content-Type: application/json
```

支持部分更新：`nickname`、`avatar`、`gender`、`bio`、`phone`。当前前端至少发送：

```json
{
  "bio": "My profile"
}
```

成功返回更新后的用户对象，字段结构同 `/api/user/info`。

### 4.5 修改密码

```http
PUT /api/user/password
Authorization: <token>
Content-Type: application/json
```

请求：

```json
{
  "oldPassword": "current_password",
  "newPassword": "new_password"
}
```

成功响应：`{ "code": 200, "message": "密码修改成功", "data": null }`。旧密码错误返回 `400` 或 `401`。

## 5. 收藏模块（收藏 paper）

以下接口均需认证。`paperId` 是稳定的论文 ID，前端发送 JSON number/string 均可能出现；后端应按数据库 ID 类型规范化并校验。

### 5.1 检查收藏状态

```http
GET /api/favorite/check?paperId=2301.01234
Authorization: <token>
```

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "isFavorite": true
  }
}
```

### 5.2 添加收藏

```http
POST /api/favorite/add
Authorization: <token>
Content-Type: application/json
```

请求：

```json
{
  "paperId": "2301.01234"
}
```

成功响应：

```json
{
  "code": 200,
  "message": "收藏成功",
  "data": {
    "id": 10,
    "userId": 1,
    "paperId": "2301.01234",
    "createTime": "2026-09-27T10:00:00"
  }
}
```

重复添加应幂等：返回成功并保留现有唯一收藏，或返回 `409` 并提供稳定业务错误。优先采用幂等成功。

### 5.3 取消收藏

```http
DELETE /api/favorite/remove?paperId=2301.01234
Authorization: <token>
```

删除当前用户对此 paper 的收藏；成功返回 `{ "code": 200, "message": "取消收藏成功", "data": null }`。不要删除其他用户记录。

### 5.4 获取收藏列表

```http
GET /api/favorite/list?page=1&pageSize=10
Authorization: <token>
```

默认 `page=1`、`pageSize=10`，最大值建议为 100。按收藏时间倒序。`list` 每项返回关系记录 ID、`favoriteTime`，以及完整 paper 对象（优先嵌套在 `paper` 属性中）：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "favoriteId": 10,
        "favoriteTime": "2026-09-27T10:00:00",
        "paper": {
          "id": "2301.01234",
          "paper_id": "2301.01234",
          "title": "Example Paper Title",
          "abstract": "Paper abstract...",
          "first_author": "Example Author",
          "submitted_at": "2023-01-03",
          "category_name": "Computer Vision",
          "pdf_url": "https://arxiv.org/pdf/2301.01234",
          "arxiv_url": "https://arxiv.org/abs/2301.01234"
        }
      }
    ],
    "total": 1,
    "hasMore": false
  }
}
```

嵌套对象可避免收藏记录 ID 和 paper ID 混淆。若提供扁平兼容字段，仍必须保留 `paperId` 或 `paper_id` 作为论文标识。

### 5.5 清空收藏

```http
DELETE /api/favorite/clear
Authorization: <token>
```

仅清除当前用户所有收藏。成功响应：`{ "code": 200, "message": "清空成功", "data": null }`。

## 6. 浏览历史模块（paper 浏览记录）

所有历史数据均按 token 中的当前用户隔离。

### 6.1 添加/更新浏览记录

```http
POST /api/history/add
Authorization: <token>
Content-Type: application/json
```

请求：

```json
{
  "paperId": "2301.01234"
}
```

成功响应：

```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "historyId": 20,
    "userId": 1,
    "paperId": "2301.01234",
    "viewTime": "2026-09-27T10:00:00"
  }
}
```

同一用户重复浏览同一论文时更新 `viewTime`，不要无限创建重复行。

### 6.2 获取浏览历史

```http
GET /api/history/list?page=1&pageSize=10
Authorization: <token>
```

当前前端不传分页参数，但后端可支持可选分页；如省略则返回最近 50 条以内，或采用明确配置的默认 page size。按 `viewTime` 倒序。

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "historyId": 20,
        "viewTime": "2026-09-27T10:00:00",
        "paper": {
          "id": "2301.01234",
          "paper_id": "2301.01234",
          "title": "Example Paper Title",
          "abstract": "Paper abstract...",
          "first_author": "Example Author",
          "submitted_at": "2023-01-03",
          "category_name": "Computer Vision",
          "pdf_url": "https://arxiv.org/pdf/2301.01234",
          "arxiv_url": "https://arxiv.org/abs/2301.01234"
        }
      }
    ],
    "total": 1,
    "hasMore": false
  }
}
```

### 6.3 删除单条历史记录

```http
DELETE /api/history/delete/{history_id}
Authorization: <token>
```

`history_id` 是历史关系记录自身 ID（列表中的 `historyId`），不是 paper ID。只能删除当前用户拥有的记录。

示例：

```http
DELETE /api/history/delete/20
```

成功响应：`{ "code": 200, "message": "删除成功", "data": null }`。

### 6.4 清空历史记录

```http
DELETE /api/history/clear
Authorization: <token>
```

仅清除当前用户历史。成功响应：`{ "code": 200, "message": "清空成功", "data": null }`。

## 7. 错误响应

所有错误应有明确 HTTP 状态码和非成功 `code`，示例：

```json
{
  "code": 401,
  "message": "Authentication required",
  "data": null
}
```

常见情况：

| HTTP | code | 场景 |
|---:|---:|---|
| 400 | 400 | 参数组合不合法、旧密码错误 |
| 401 | 401 | token 缺失/无效/过期，或登录凭据错误 |
| 403 | 403 | 已认证但无权访问该用户数据 |
| 404 | 404 | paper 或指定关系记录不存在 |
| 409 | 409 | 用户名已存在等唯一约束冲突 |
| 422 | 422 | 请求体/查询参数类型或范围校验失败 |
| 500 | 500 | 未预期服务异常，不泄露 SQL、密钥或堆栈 |

## 8. CORS 和开发联调

- 本地 Vite 页面常见来源为 `http://localhost:5173` 或 `http://127.0.0.1:5173`，需按实际浏览器地址显式配置。
- 允许 `Authorization`、`Content-Type` 和本规范使用的 GET/POST/PUT/DELETE 方法。
- 不要在生产环境使用任意来源的通配 CORS。
- 联调顺序建议：paper categories → paper list → paper detail/PDF → register/login → favorite → history。
