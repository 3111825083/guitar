# 🚀 吉他谱网 - 快速部署清单

## 部署选项对比

| 方案 | 难度 | 成本 | 配置时间 | 自动化 | 推荐度 |
|------|------|------|---------|--------|--------|
| Railway | ⭐ 极易 | 免费 | 2分钟 | ✅ 自动 | ⭐⭐⭐⭐⭐ |
| Vercel | ⭐ 极易 | 免费 | 3分钟 | ✅ 自动 | ⭐⭐⭐⭐ |
| VPS自建 | ⭐⭐⭐ 中等 | $5-30/月 | 15分钟 | ⚠️ 手动 | ⭐⭐ |
| Docker | ⭐⭐ 简易 | 取决于托管 | 5分钟 | ✅ 自动 | ⭐⭐⭐ |

## 选择推荐

- **新手/快速上线** → Railway（最简单）
- **需要高级功能** → 自建 VPS + Docker
- **企业级应用** → Kubernetes 集群

---

## 方案 1️⃣ Railway（推荐 ⭐⭐⭐⭐⭐）

### 前置条件
- ✅ GitHub 账号
- ✅ Fork 本项目

### 部署步骤

1. **Fork 项目**
   ```bash
   # 访问 https://github.com/your-username/guitar
   # 点击右上角 Fork 按钮
   ```

2. **Railway 部署**
   - 访问 https://railway.app
   - 点击 "Create New Project"
   - 选择 "Deploy from GitHub Repo"
   - 选择你的 `guitar` 仓库
   - 选择分支 `main`
   - ✅ 自动部署！

3. **获取域名**
   - Railway 自动分配域名：`xxxx.railway.app`
   - 或者绑定自定义域名

### 部署完成后

- 访问你的 URL：`https://your-app.railway.app`
- 所有功能自动可用
- 后续代码更新自动部署

### 查看日志
```
在 Railway 控制面板 → Logs 标签
```

---

## 方案 2️⃣ Vercel

### 前置条件
- ✅ GitHub 账号
- ✅ Vercel 账号

### 部署步骤

1. **访问 Vercel**
   ```
   https://vercel.com/import
   ```

2. **导入 GitHub 仓库**
   - 点击 "Import Project"
   - 授权 GitHub
   - 选择 `guitar` 仓库

3. **配置项目**
   - 项目名称：`guitar`
   - Framework：Node.js
   - Root Directory：`.`

4. **部署**
   - 点击 "Deploy"
   - 等待部署完成

### 获得 URL
- Vercel 自动生成：`guitar.vercel.app`

---

## 方案 3️⃣ 自建服务器（VPS）

### 前置条件
- ✅ VPS 主机（推荐 Ubuntu 20.04+）
  - 推荐商家：Linode、DigitalOcean、腾讯云、阿里云
  - 配置：1GB RAM 以上
  - 价格：$5-30/月

### 快速部署脚本

```bash
# SSH 登录到你的服务器
ssh root@your-vps-ip

# 复制粘贴以下一键部署命令
curl -fsSL https://raw.githubusercontent.com/your-username/guitar/main/deploy.sh | bash
```

### 手动部署步骤

```bash
# 1. 更新系统
apt update && apt upgrade -y

# 2. 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt install nodejs -y

# 3. 克隆项目
git clone https://github.com/your-username/guitar.git
cd guitar

# 4. 安装依赖
npm install

# 5. 安装 PM2（进程管理）
npm install -g pm2

# 6. 启动应用
pm2 start server.js --name guitar

# 7. 配置开机自启
pm2 startup
pm2 save

# 8. 配置反向代理（Nginx）
apt install nginx -y
# 编辑 /etc/nginx/sites-available/default
# 配置指向 localhost:3000
```

### 配置 Nginx

编辑 `/etc/nginx/sites-available/default`：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 启用 HTTPS

```bash
# 安装 Certbot
apt install certbot python3-certbot-nginx -y

# 申请证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

### 检查状态

```bash
# 查看应用运行状态
pm2 status

# 查看日志
pm2 logs guitar

# 重启应用
pm2 restart guitar
```

---

## 方案 4️⃣ Docker 部署

### Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

ENV PORT=3000
ENV NODE_ENV=production

EXPOSE 3000

CMD ["npm", "start"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t guitar-tabs .

# 运行容器
docker run -d -p 3000:3000 \
  -v $(pwd)/tabs-config.json:/app/tabs-config.json \
  --name guitar guitar-tabs

# 查看日志
docker logs guitar
```

---

## 后续维护

### 更新代码

```bash
# 本地修改后推送到 GitHub
git add .
git commit -m "update features"
git push origin main

# Railway/Vercel 自动部署
# VPS 需要手动拉取
ssh root@your-vps
cd guitar
git pull
pm2 restart guitar
```

### 备份配置

```bash
# 下载配置文件备份
scp root@your-vps:/path/to/guitar/tabs-config.json ./backup/
```

### 监控应用

```bash
# 查看 CPU/内存使用
pm2 monit

# 日志监控
pm2 logs guitar --follow
```

---

## 常见问题

**Q: 怎样绑定自定义域名？**

A: 
- Railway：在项目设置中添加 Custom Domain
- Vercel：在项目设置中添加 Domain
- VPS：修改 DNS 记录指向你的服务器 IP

**Q: 内存不足或应用崩溃？**

A:
```bash
# 查看进程
top

# 增加 VPS 内存配置
# 或使用 pm2 cluster 模式
pm2 start server.js -i max --name guitar
```

**Q: 如何回滚到上个版本？**

A:
```bash
# GitHub 查看提交历史
git log

# 回滚
git revert <commit-id>
git push

# 自动重新部署
```

**Q: 部署后无法访问？**

A:
1. 检查应用日志：`pm2 logs`
2. 检查防火墙：`ufw allow 3000/tcp`
3. 检查 DNS 解析：`nslookup your-domain.com`
4. 检查反向代理：`curl localhost:3000`

---

## 📊 部署状态检查

```bash
# 健康检查
curl https://your-app.com/api/health

# 期望响应
{ "status": "ok", "timestamp": "2025-12-01T..." }
```

---

## 💡 最佳实践

1. ✅ 始终在 `main` 分支提交代码
2. ✅ 定期备份 `tabs-config.json`
3. ✅ 监控服务器资源使用
4. ✅ 启用 HTTPS（安全）
5. ✅ 配置自动日志轮换

---

**祝部署顺利！🚀**
