# Paper 项目 API 接口文档

## 概述

后端使用 FastAPI，前端 API 地址当前为 `http://127.0.0.1:8000`。接口返回 JSON，成功示例：

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

需要登录的接口在请求头中传入：

```http
Authorization: token值
```

`papers.id` 是 paper 数据库主键。详情、收藏和历史使用此 ID；CSV 中的 arXiv `paper_id` 是外部 ID，不要与数据库主键混淆。

## Paper 模块

### 1. 获取分类列表

- **接口地址**：`GET /api/papers/categories`
- **请求参数**：无
- **说明**：返回分类数组。当前前端无分类数据时会显示默认 7 个 paper 分类。

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    { "id": 1, "name": "Computer Vision" },
    { "id": 2, "name": "Machine Learning" }
  ]
}
```

> `data` 应为分类数组，不能返回单个 paper detail 对象。分类项至少要有 `id`、`name`。

### 2. 获取 Paper 列表

- **接口地址**：`GET /api/papers/list`
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `categoryId` | integer/string | 否 | 分类 ID；若传 arXiv 分类 code，后端需能识别 |
| `page` | integer | 否 | 页码，默认 1 |
| `pageSize` | integer | 否 | 每页数量，默认 10 |

- **请求示例**：

```text
GET /api/papers/list?categoryId=1&page=1&pageSize=10
```

- **响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "Paper title",
        "abstract": "Paper abstract",
        "author": "Author name",
        "publishTime": "2023-01-01",
        "categoryId": 1,
        "categoryName": "Computer Vision",
        "pdfUrl": "https://arxiv.org/pdf/2301.01234",
        "paperId": "2301.01234"
      }
    ],
    "total": 1,
    "hasMore": false
  }
}
```

列表项使用与 detail 相同的字段名称，保证前端列表和详情数据一致。

### 3. 获取 Paper 详情

- **接口地址**：`GET /api/papers/detail`
- **请求参数**：`id`，paper 数据库主键
- **请求示例**：

```text
GET /api/papers/detail?id=1
```

- **响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "title": "Paper title",
    "abstract": "Paper abstract",
    "author": "Author name",
    "publishTime": "2023-01-01",
    "categoryId": 1,
    "categoryName": "Computer Vision",
    "paperId": "2301.01234",
    "pdfUrl": "https://arxiv.org/pdf/2301.01234",
    "relatedNews": []
  }
}
```

`author` 可以为 `null`。前端使用 `pdfUrl` 在详情页 iframe 中显示 PDF；它应映射数据库的 `pdf_url`。没有 PDF 时可返回 `null`。`relatedNews` 可为空数组；若后端字段名沿用该名称，数组项应提供 `id`、`title`。

## 用户模块

### 1. 注册

- **接口地址**：`POST /api/user/register`
- **请求 Body**：

```json
{
  "username": "example_user",
  "password": "example_password"
}
```

- **响应示例**：

```json
{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "token": "user-token",
    "userInfo": {
      "id": 1,
      "username": "example_user",
      "bio": ""
    }
  }
}
```

### 2. 登录

- **接口地址**：`POST /api/user/login`
- **请求 Body**：与注册相同
- **响应**：与注册相同，返回 `token` 和 `userInfo`

### 3. 获取用户信息

- **接口地址**：`GET /api/user/info`
- **请求头**：需要认证
- **响应 `data`**：用户对象，至少包含 `id`、`username`、`bio`

### 4. 更新用户信息

- **接口地址**：`PUT /api/user/update`
- **请求头**：需要认证
- **请求 Body**：支持更新 `nickname`、`avatar`、`gender`、`bio`、`phone`

```json
{
  "bio": "个人简介"
}
```

### 5. 修改密码

- **接口地址**：`PUT /api/user/password`
- **请求头**：需要认证
- **请求 Body**：

```json
{
  "oldPassword": "old-password",
  "newPassword": "new-password"
}
```

## 收藏模块

以下接口均需要登录，`paperId` 填 Paper 数据库主键。

### 1. 检查收藏状态

- **接口地址**：`GET /api/favorite/check?paperId=1`
- **响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": { "isFavorite": true }
}
```

### 2. 添加收藏

- **接口地址**：`POST /api/favorite/add`
- **请求 Body**：

```json
{
  "paperId": 1
}
```

### 3. 取消收藏

- **接口地址**：`DELETE /api/favorite/remove?paperId=1`

### 4. 获取收藏列表

- **接口地址**：`GET /api/favorite/list?page=1&pageSize=10`
- **响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "Paper title",
        "abstract": "Paper abstract",
        "author": "Author name",
        "publishTime": "2023-01-01",
        "paperId": 1,
        "favoriteTime": "2026-09-27T10:00:00"
      }
    ],
    "total": 1,
    "hasMore": false
  }
}
```

返回项中的 `id` 是 Paper 数据库主键，供前端打开详情；不要把 favorite 记录 ID 放在 `id` 字段。

### 5. 清空收藏

- **接口地址**：`DELETE /api/favorite/clear`
- **说明**：只清空当前登录用户的收藏

## 浏览历史模块

以下接口均需要登录。

### 1. 添加浏览记录

- **接口地址**：`POST /api/history/add`
- **请求 Body**：

```json
{
  "paperId": 1
}
```

### 2. 获取浏览历史

- **接口地址**：`GET /api/history/list`
- **响应 `data.list`**：返回 Paper 字段以及 `historyId`、`viewTime`

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [
      {
        "historyId": 10,
        "id": 1,
        "title": "Paper title",
        "abstract": "Paper abstract",
        "author": "Author name",
        "publishTime": "2023-01-01",
        "viewTime": "2026-09-27T10:00:00"
      }
    ],
    "total": 1,
    "hasMore": false
  }
}
```

### 3. 删除一条浏览记录

- **接口地址**：`DELETE /api/history/delete/{history_id}`
- **说明**：`history_id` 是历史记录主键，不是 Paper ID

### 4. 清空浏览历史

- **接口地址**：`DELETE /api/history/clear`
- **说明**：只清空当前登录用户的浏览历史

## PDF 显示说明

详情接口返回 `pdfUrl`（对应数据库 `pdf_url`），浏览器会直接通过 iframe 加载该 URL，不需要后端把 PDF 转成 JSON。URL 必须能从用户的浏览器访问；若来源站点禁止 iframe，可通过新窗口打开 PDF。
