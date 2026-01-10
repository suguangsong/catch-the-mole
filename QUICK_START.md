# 快速开始指南

## 🚀 Zeabur 一键部署（5 分钟）

### 步骤 1：准备 GitHub 仓库

```bash
# 1. 初始化 Git（如果还没有）
git init
git add .
git commit -m "Initial commit"

# 2. 在 GitHub 创建新仓库，然后推送
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

### 步骤 2：部署到 Zeabur

1. 访问 [zeabur.com](https://zeabur.com) 并登录（使用 GitHub）
2. 点击 "New Project" → 输入项目名称
3. 点击 "Deploy New Service" → 选择 "GitHub"
4. 选择你的仓库 `catch-the-mole`
5. 添加环境变量：
   - `SECRET_KEY`: 生成一个随机字符串
   - `DEBUG`: `False`
6. 点击 "Deploy"
7. 等待 3-5 分钟，获得自动分配的域名

**生成 SECRET_KEY**：
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 步骤 3：访问应用

部署完成后，Zeabur 会提供一个类似 `your-app.zeabur.app` 的域名，点击即可访问！

---

## 💻 本地 Docker 运行

```bash
# 1. 克隆项目
git clone <repository-url>
cd catch-the-mole

# 2. 启动服务
docker-compose up --build

# 3. 访问 http://localhost:8000
```

---

## 📚 更多信息

- **详细部署文档**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Zeabur 部署指南**: [ZEABUR_DEPLOYMENT.md](ZEABUR_DEPLOYMENT.md)
- **部署检查清单**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
