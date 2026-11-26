# 轻量任务管理系统（Task Manager）

一个面向初级后端 / 全栈岗位的作品集 Demo：用户注册登录后管理自己的任务，支持任务的增删改查与按状态筛选，基于 JWT 鉴权并做了用户级数据隔离。项目刻意保持低复杂度，便于在面试中完整讲清每一层设计。

## 一、项目简介 & 适用场景

- **做什么**：多用户待办任务管理。每个用户只能看到和操作自己的任务，任务包含标题、描述、状态（待办 / 进行中 / 已完成）。
- **适用场景**：简历项目、面试演示、前后端分离 + RESTful 接口 + JWT 鉴权的基础实践样例。
- **不包含**（有意裁剪，控制复杂度）：分页、标签、评论、文件上传、消息通知、角色权限、图表、支付、拖拽排序等。

## 二、技术栈

### 后端

| 技术 | 用途 |
|---|---|
| FastAPI | Web 框架，提供 RESTful 接口与自动接口文档 |
| SQLAlchemy | ORM，映射数据库表 |
| SQLite | 轻量文件数据库，零外部服务依赖 |
| PyJWT | 签发与校验 JWT |
| passlib[bcrypt] | 密码 bcrypt 哈希 |
| python-multipart | 表单 / 请求体解析支持 |
| uvicorn | ASGI 运行服务器 |

### 前端

| 技术 | 用途 |
|---|---|
| React 18 | UI 框架 |
| Ant Design 5 | 组件库（表单、表格、弹窗、标签等） |
| Axios | HTTP 请求封装与拦截器 |
| React Router 6 | 路由与登录守卫 |
| Vite | 前端构建与开发服务器 |

> 状态管理仅使用 React 原生 `useState` / `useEffect`，未引入 Redux / Zustand 等额外状态库。

## 三、本地启动步骤

### 1. 后端（端口 8000）

```bash
cd backend

# 建议创建虚拟环境
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

- 启动后自动创建 `backend/task.db`（SQLite 文件库）。
- 自动接口文档：http://localhost:8000/docs

### 2. 前端（端口 5173）

```bash
cd frontend
npm install
npm run dev
```

- 访问 http://localhost:5173
- 前端请求默认指向 `http://localhost:8000`，如需修改可在 `src/api/request.js` 中调整 `baseURL`。

### 3. 快速体验

1. 打开前端地址，在注册页创建账号；
2. 登录后进入任务列表，新增 / 编辑 / 删除任务，按状态筛选；
3. 另注册一个账号登录，验证看不到前一个账号的任务。

## 四、功能截图

> 启动前后端后截图替换下列占位文件即可。

- 登录 / 注册页：`docs/screenshot-login.png`
- 任务列表页：`docs/screenshot-task-list.png`

## 五、数据库设计

仅两张表：`users`、`tasks`。

### users（用户表）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | 主键，自增 | 用户 ID |
| username | VARCHAR(50) | 唯一，非空 | 登录名 |
| password_hash | VARCHAR(255) | 非空 | bcrypt 哈希，不存明文 |
| created_at | DATETIME | 默认当前时间 | 注册时间 |

### tasks（任务表）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | 主键，自增 | 任务 ID |
| title | VARCHAR(100) | 非空 | 任务标题 |
| description | TEXT | 可空 | 任务描述 |
| status | VARCHAR(20) | 非空，默认 `todo` | `todo` / `doing` / `done` |
| user_id | INTEGER | 外键 → users.id，索引 | 所属用户 |
| created_at | DATETIME | 默认当前时间 | 创建时间 |
| updated_at | DATETIME | 更新时自动刷新 | 最后修改时间 |

## 六、项目难点 & 思考（面试口述核心）

### 1. 如何保证用户数据隔离

- 所有任务查询都强制带上 `user_id = 当前登录用户 id` 条件，而不是只按任务 ID 查。
- 单条任务的查 / 改 / 删使用 **ID + user_id 双条件** 查询；查不到统一返回 404，不区分「任务不存在」还是「属于他人」，避免泄露他人任务是否存在。
- 新建任务时 `user_id` 取自后端登录态，前端请求体里即使伪造 `user_id` 也会被忽略。

### 2. JWT 鉴权流程 & 优缺点

**流程**：登录校验密码通过后，后端签发 JWT（payload 只放用户 id 和过期时间，用密钥 HS256 签名）；前端把 token 存到 localStorage，之后请求由 axios 拦截器自动放到 `Authorization: Bearer <token>`；后端依赖层解析并校验签名与有效期，通过后取出当前用户。

**优点**：
- 无状态，服务端不存会话，便于水平扩展；
- 接口鉴权统一由一个依赖完成，路由直接复用。

**缺点 / 注意点**：
- 签发后在过期前难以主动失效（本项目未做刷新 token 与黑名单）；
- payload 不要放敏感信息（仅编码，非加密）；
- 密钥需要妥善保管，不能硬编码进公开仓库。

### 3. 密码为什么用 bcrypt，不能明文

- 明文存储一旦数据库泄露，所有账号密码直接暴露；
- 普通哈希（如 MD5/SHA）可被彩虹表、暴力破解快速还原；
- bcrypt 自带加盐、计算代价可调（work factor），哈希速度慢，能显著提高暴力破解成本；
- 校验时用 `verify` 比对明文与哈希，全程不存储、不回传明文。

### 4. 接口异常统一处理方案

- 后端定义统一响应结构 `{ "code": 200, "msg": "success", "data": ... }`；
- 用全局异常处理器把 `HTTPException`、入参校验错误（`RequestValidationError`）、未捕获兜底异常分别转成统一格式，对应 400 / 401 / 404 / 500；
- 兜底异常不把内部堆栈信息暴露给前端。

### 5. 前端 axios 拦截器的作用

- **请求拦截器**：自动从 localStorage 读取 token 并放到请求头，业务代码无需每次手动携带；
- **响应拦截器**：统一拆解后端 `{code, msg, data}` 结构，业务层直接拿 `data`；业务错误统一弹提示；遇到 401 清除本地 token 并跳转登录页。

## 七、待优化点

- **认证**：增加刷新 token（refresh token）机制；token 失效黑名单 / 主动登出失效；密钥与配置改用环境变量。
- **后端**：接入单元测试（pytest）；参数校验提示中文化；补充接口日志；数据库迁移改用 Alembic；开启 SQLite 外键约束 `PRAGMA foreign_keys=ON`。
- **数据**：任务列表分页、按创建时间 / 状态排序；热门数据可加缓存。
- **前端**：路由级代码分包、Ant Design 按需加载以减小打包体积；错误边界与加载状态细化。
- **扩展能力（按需再做）**：角色权限、任务标签、评论、文件上传、消息通知等。

## 八、目录结构

```
task-manager/
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # 入口、CORS、全局异常处理、路由挂载
│       ├── database.py         # SQLite 引擎、会话工厂、get_db 依赖
│       ├── models.py           # User / Task ORM 模型
│       ├── schemas.py          # Pydantic 请求 / 响应模型
│       ├── security.py         # bcrypt 哈希、JWT 签发与解析
│       ├── deps.py             # 当前登录用户依赖
│       ├── response.py         # 统一响应结构
│       └── routers/
│           ├── auth.py         # 注册 / 登录
│           └── tasks.py        # 任务 CRUD / 筛选
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx            # 路由 + 登录守卫
│       ├── api/               # axios 实例与接口封装
│       ├── utils/auth.js      # token 本地存取
│       └── pages/
│           ├── Login.jsx      # 登录 / 注册 Tab 页
│           └── TaskList.jsx   # 任务列表 + 新增 / 编辑弹窗
├── api.md                     # 接口文档
└── README.md
```
