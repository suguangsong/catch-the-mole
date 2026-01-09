下面是基于你给出的**业务约束与技术选型**，为项目 **catch-the-mole（抓畜）** 设计的**页面交互与整体架构方案**。内容以 **Markdown** 形式组织，可直接作为项目设计文档或 README 初稿。

---

# catch-the-mole（抓畜）

> 一个面向 Dota2 玩家、用于匿名投票“谁是内鬼”的轻量级 Web 应用

---

## 1. 项目目标与核心原则

### 1.1 项目目标

* 为 **单场 Dota2 比赛失败方的 5 名玩家** 提供一个**匿名投票工具**
* 快速创建房间、快速投票、即时出结果
* **免登录、无数据库、单体应用、容器化部署**

### 1.2 核心设计原则

* **低复杂度**：无账号体系、无持久化数据库
* **匿名性优先**：不展示个人投票去向
* **强约束投票**：

  * 每人每房间仅 1 票
  * 刷新页面不能重复投票
* **可扩展性**：后续可平滑引入 Redis / DB / 登录体系

---

## 2. 技术架构设计

### 2.1 技术选型总览

| 层级   | 技术                        |
| ---- | ------------------------- |
| 后端   | Django（单体）                |
| 前端   | Vue 3（编译后静态资源由 Django 提供） |
| 通信   | Django REST API（JSON）     |
| 数据来源 | OpenDota API              |
| 数据存储 | 内存（Python dict）           |
| 容器化  | Docker                    |
| 身份标识 | Cookie / LocalStorage     |

> 这是**前后端不分离的单体架构**，但在代码层面保持“逻辑分层”。

---

### 2.2 总体架构图（逻辑）

```text
┌───────────────┐
│   Browser     │
│  (Vue UI)     │
└───────▲───────┘
        │ HTTP / JSON
┌───────┴───────┐
│   Django App  │
│               │
│  ┌─────────┐ │
│  │ Views   │ │
│  └─────────┘ │
│       │       │
│  ┌─────────┐ │
│  │ Service │ │  ← 投票、房间、校验逻辑
│  └─────────┘ │
│       │       │
│  ┌─────────┐ │
│  │ Memory  │ │  ← dict / cache
│  └─────────┘ │
└───────────────┘
        │
        ▼
┌──────────────────┐
│ OpenDota API     │
│ matches/{id}     │
└──────────────────┘
```

---

## 3. 数据模型（内存结构）

> 不使用数据库，全部数据存于 Django 进程内存

### 3.1 Room（房间）

```python
Room = {
  room_id: str,          # uuid 或用户自定义
  match_id: int,
  max_votes: int,        # 默认 5
  status: "init" | "voting" | "finished",
  created_at: datetime,
  heroes: [              # 从 OpenDota 获取
    {
      player_slot: int,
      hero_id: int,
      hero_name: str,
      nickname: str
    }
  ],
  votes: {
    player_index: int -> vote_count
  },
  voted_users: set,      # user_fingerprint
}
```

---

### 3.2 用户指纹（免登录）

```text
user_fingerprint = UUID
```

* 首次进入站点生成
* 存储于 `localStorage`
* 每次请求通过 header / cookie 上报
* 用于限制：**同一房间只能投一次**

---

## 4. 页面与交互设计

## 4.1 首页（/）

### 页面目标

* 明确分流两类用户
* 极低理解成本

### 页面结构

```text
┌──────────────────────────┐
│       抓畜（catch-the-mole） │
│  谁是这把的内鬼？            │
│                          │
│ [ 我是第一个创建房间的人 ]  │
│                          │
│ [ 我是来投票的 ]            │
└──────────────────────────┘
```

### 交互说明

* **按钮 1** → 创建房间页
* **按钮 2** → 加入房间页

---

## 4.2 创建房间页（/create）

### 页面元素

```text
Match ID 输入框
房间 ID（自动生成，可编辑）
最大投票人数（默认 5）

[ 开始投票 ]
```

### 交互流程

1. 用户输入 `match_id`
2. 系统自动生成 `uuid` 作为房间 ID（可修改）
3. 点击「开始投票」
4. 后端：

   * 校验 match_id
   * 拉取 OpenDota 比赛数据
   * 解析失败方 5 名玩家
   * 创建房间
5. 跳转到房间页

---

## 4.3 加入房间页（/join）

### 页面元素

```text
请输入房间 ID

[ 进入房间 ]
```

### 交互说明

* 校验房间是否存在
* 若不存在：提示错误
* 若已结束：提示已结束

---

## 4.4 房间页（/room/{room_id}）

### 初始状态（未开始投票）

```text
比赛 ID：xxxxxx

失败方玩家：
1. 玩家昵称 - 英雄
2. 玩家昵称 - 英雄
3. 玩家昵称 - 英雄
4. 玩家昵称 - 英雄
5. 玩家昵称 - 英雄

[ 开始投票 ]
```

> 只有**房间创建者**能看到“开始投票”

---

### 投票中状态

```text
请在键盘输入 1 - 5 进行投票

（页面监听 keydown 事件）

投票后提示：
✅ 投票成功
```

#### 投票规则

* 只能输入 `1~5`
* 对应失败方 5 名玩家
* **不展示你投给了谁**
* 若已投票：

  * 禁止再次输入
  * 显示“你已完成投票”

---

### 投票完成（达到 max_votes）

```text
投票结果公布：

玩家 1（英雄）：2 票
玩家 2（英雄）：1 票
玩家 3（英雄）：0 票
玩家 4（英雄）：1 票
玩家 5（英雄）：1 票

🐭 内鬼是：玩家 1
```

---

### 页面底部

```text
[ 返回首页 ]
```

---

## 5. 后端接口设计（示例）

### 创建房间

```
POST /api/rooms
```

### 获取房间信息

```
GET /api/rooms/{room_id}
```

### 开始投票

```
POST /api/rooms/{room_id}/start
```

### 提交投票

```
POST /api/rooms/{room_id}/vote
Body: { player_index: 1-5 }
```

---

## 6. Docker 化方案

### 基本思路

* 单容器
* Django 提供 API + Vue 编译后静态资源
* 内存数据随容器生命周期存在

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY backend /app/backend
COPY frontend/dist /app/backend/static

RUN pip install -r backend/requirements.txt

CMD ["gunicorn", "app.wsgi:application", "-b", "0.0.0.0:8000"]
```

---

## 7. 可扩展方向（未来）

* 引入 Redis → 支持多实例
* 引入比赛缓存 → 降低 OpenDota 调用
* 增加投票倒计时
* WebSocket 实时展示投票进度
* 历史房间回放（需要 DB）

---

如果你愿意，下一步我可以：

* 帮你设计 **Django 项目目录结构**
* 设计 **Vue 组件拆分**
* 给你一份 **最小可运行 Demo 骨架**
* 或直接从 **“创建房间接口”** 开始写代码
