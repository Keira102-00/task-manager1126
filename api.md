# 接口文档（API）

- Base URL：`http://localhost:8000`
- 鉴权方式：除注册 / 登录外，所有接口需在请求头携带 `Authorization: Bearer <access_token>`
- 数据格式：请求与响应均为 JSON

## 统一响应结构

```json
{ "code": 200, "msg": "success", "data": {} }
```

| 字段 | 说明 |
|---|---|
| code | 业务状态码，200 成功；400 参数错误；401 未登录 / 凭证无效；404 资源不存在或无权访问；500 服务器内部错误 |
| msg | 提示信息 |
| data | 业务数据，失败时为 `null` |

### 错误码一览

| code | HTTP 状态 | 触发场景 |
|---|---|---|
| 200 | 200 | 成功 |
| 400 | 400 | 入参校验失败、用户名已存在 |
| 401 | 401 | 未携带 token、token 无效 / 过期、用户名或密码错误 |
| 404 | 404 | 任务不存在或无权访问 |
| 500 | 500 | 未捕获的服务器内部错误 |

### 任务状态枚举

| 值 | 含义 |
|---|---|
| `todo` | 待办 |
| `doing` | 进行中 |
| `done` | 已完成 |

---

## 1. 鉴权

### 1.1 注册

`POST /auth/register`

**请求体**

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| username | string | 是 | 3–50 字符 |
| password | string | 是 | 6–64 字符，仅传输用，不落库明文 |

请求示例：

```json
{ "username": "alice", "password": "123456" }
```

成功响应 `200`：

```json
{ "code": 200, "msg": "success", "data": { "id": 1, "username": "alice" } }
```

失败响应：

- 用户名已存在 → `400` `{"code":400,"msg":"用户名已存在","data":null}`
- 入参不合法 → `400` `{"code":400,"msg":"参数错误：...","data":null}`

### 1.2 登录

`POST /auth/login`

**请求体**

| 字段 | 类型 | 必填 |
|---|---|---|
| username | string | 是 |
| password | string | 是 |

请求示例：

```json
{ "username": "alice", "password": "123456" }
```

成功响应 `200`：

```json
{
  "code": 200,
  "msg": "success",
  "data": { "access_token": "eyJhbGciOi...", "token_type": "bearer" }
}
```

失败响应：

- 密码错误 / 用户不存在 → `401` `{"code":401,"msg":"用户名或密码错误","data":null}`

---

## 2. 任务

> 以下接口均需登录，请求头携带 `Authorization: Bearer <access_token>`。

### 2.1 任务列表（可按状态筛选）

`GET /tasks`

**查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| status | string | 否 | `todo` / `doing` / `done`；不传返回全部 |

请求示例：

```
GET /tasks?status=done
```

成功响应 `200`（按创建时间倒序）：

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 3,
      "title": "复盘",
      "description": null,
      "status": "done",
      "created_at": "2026-11-26T07:27:02.518316",
      "updated_at": "2026-11-26T07:27:02.518316"
    }
  ]
}
```

### 2.2 任务详情

`GET /tasks/{task_id}`

成功响应 `200`：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "title": "写周报",
    "description": "本周工作总结",
    "status": "todo",
    "created_at": "2026-11-26T07:27:02.461527",
    "updated_at": "2026-11-26T07:27:02.461531"
  }
}
```

失败：任务不存在或属于他人 → `404` `{"code":404,"msg":"任务不存在或无权访问","data":null}`

### 2.3 新建任务

`POST /tasks`

**请求体**

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| title | string | 是 | 1–100 字符 |
| description | string | 否 | 最长 1000 字符 |
| status | string | 否 | `todo` / `doing` / `done`，默认 `todo` |

> `user_id` 由后端从登录态写入，前端传入会被忽略。

请求示例：

```json
{ "title": "写周报", "description": "本周工作总结", "status": "todo" }
```

成功响应 `200`：

```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "id": 1,
    "title": "写周报",
    "description": "本周工作总结",
    "status": "todo",
    "created_at": "2026-11-26T07:27:02.461527",
    "updated_at": "2026-11-26T07:27:02.461531"
  }
}
```

### 2.4 编辑任务

`PUT /tasks/{task_id}`

**请求体**（字段均可选，只更新传入的字段）

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| title | string | 否 | 1–100 字符 |
| description | string | 否 | 最长 1000 字符 |
| status | string | 否 | `todo` / `doing` / `done` |

请求示例：

```json
{ "title": "写周报(终稿)", "status": "doing" }
```

成功响应 `200`：

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "title": "写周报(终稿)",
    "description": "本周工作总结",
    "status": "doing",
    "created_at": "2026-11-26T07:27:02.461527",
    "updated_at": "2026-11-26T07:27:11.555040"
  }
}
```

失败：任务不存在或属于他人 → `404`

### 2.5 删除任务

`DELETE /tasks/{task_id}`

成功响应 `200`：

```json
{ "code": 200, "msg": "删除成功", "data": null }
```

失败：任务不存在或属于他人 → `404`

---

## 3. 鉴权失败响应示例

未携带 token 或 token 无效 / 过期：

```json
{ "code": 401, "msg": "未登录或登录已过期", "data": null }
```
