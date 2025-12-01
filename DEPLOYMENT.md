# 吉他谱网 - 部署指南

这是一个全栈动态网页应用，支持云部署。

## 项目结构

```
.
├── server.js              # Express 后端服务器
├── public/                # 前端文件（静态资源）
│   ├── index.html
│   ├── tab-detail.html
│   └── source/            # 吉他谱图片
├── tabs-config.json       # 配置文件（动态修改）
├── package.json           # 依赖配置
├── .env.example           # 环境变量示例
├── railway.toml           # Railway 部署配置
└── vercel.json            # Vercel 部署配置
```

## 本地开发

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm start
# 或使用 nodemon 监听文件变化
npm run dev
```

服务器运行在 `http://localhost:3000`

### 环境配置
复制 `.env.example` 到 `.env` 并修改：
```bash
cp .env.example .env
```

## 云部署方案

### 方案 1：Railway（推荐）

1. **注册账户**
   - 访问 https://railway.app
   - 使用 GitHub 账号登录

2. **连接 Git 仓库**
   ```bash
   git add .
   git commit -m "Deploy to Railway"
   git push origin main
   ```

3. **在 Railway 中创建项目**
   - 点击 "Create New Project"
   - 选择 "Deploy from GitHub"
   - 选择你的 guitar 仓库
   - 自动部署完成！

4. **获取公网 URL**
   - 在 Railway 项目中查看部署信息
   - 你的应用 URL 类似：`https://xxxx.railway.app`

### 方案 2：Vercel

1. **安装 Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **登录并部署**
   ```bash
   vercel
   ```

3. **按照提示完成部署**
   - 选择关联的 GitHub 账号
   - 选择项目目录

### 方案 3：Heroku（已弃用，不推荐）

### 方案 4：自建服务器（VPS）

1. **准备服务器**
   - 任何支持 Node.js 的 Linux VPS
   - 推荐 Ubuntu 20.04 LTS

2. **部署步骤**
   ```bash
   # SSH 登录到服务器
   ssh root@your-server-ip
   
   # 克隆仓库
   git clone https://github.com/your-username/guitar.git
   cd guitar
   
   # 安装依赖
   npm install
   
   # 安装 PM2（进程管理工具）
   npm install -g pm2
   
   # 启动应用
   pm2 start server.js --name guitar
   
   # 配置 PM2 开机自启
   pm2 startup
   pm2 save
   ```

3. **配置反向代理（Nginx）**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
   
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

4. **启用 HTTPS（Let's Encrypt）**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

## API 文档

### 获取所有配置
```
GET /api/tabs
返回: { "歌曲名": { id, singer, type, view, download, cover, scroll }, ... }
```

### 获取单个谱子配置
```
GET /api/tabs/:tabKey
返回: { id, singer, type, view, download, cover, scroll }
```

### 保存时间戳配置
```
POST /api/save-config
请求体: { tabKey: "string", scroll: [{ time: number, position: number }, ...] }
返回: { message: "配置已保存", tabKey, scroll }
```

### 批量保存配置
```
POST /api/save-all-configs
请求体: { "歌曲名": { id, singer, ..., scroll }, ... }
返回: { message: "所有配置已保存", updatedKeys }
```

### 健康检查
```
GET /api/health
返回: { status: "ok", timestamp }
```

## 常见问题

### Q: 配置文件丢失怎么办？
A: 自动备份在 `tabs-config-backup.json`。恢复方法：
```bash
cp tabs-config-backup.json tabs-config.json
npm start
```

### Q: 如何更新吉他谱图片？
A: 将新的 PNG 图片放入 `public/source/歌曲名/` 目录，重启服务器即可加载。

### Q: 前端怎么连接线上后端？
A: 前端会自动检测环境：
- 本地开发：自动连接 `http://localhost:3000/api`
- 线上部署：自动连接当前域名的 `/api` 路由

### Q: 如何修改时间戳配置？
A: 两种方法：
1. 在全屏模式中使用"录制时间戳"功能（GUI）
2. 直接编辑 `tabs-config.json`（手动）

## 维护建议

1. **定期备份** `tabs-config.json`
2. **监控日志** 查看服务状态
3. **更新依赖** 定期运行 `npm update`
4. **性能优化** 使用 CDN 加速图片访问

## 许可证

ISC

## 支持

有问题？提交 Issue 或联系开发者。
