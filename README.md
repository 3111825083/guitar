# 🎸 吉他谱网 - 免费吉他谱分享平台

一个功能完整的动态网页应用，支持在线查看吉他谱、自动滚动播放、时间戳录制等功能。**开源 + 可部署到云端**。

## ✨ 核心功能

- 📱 **响应式设计** - 支持桌面、平板、手机多设备
- 🎯 **全屏查看** - 全屏沉浸式浏览谱子
- ⏱️ **自动滚动** - 基于时间戳的平滑自动滚动
- 📍 **时间戳录制** - 图形化工具记录谱子位置和时间
- 💾 **配置管理** - 实时保存并同步到后端
- ⭐ **收藏功能** - 本地收藏管理
- 🔍 **搜索筛选** - 按歌名、歌手、类型快速查找

## 🚀 快速开始

### 本地开发

```bash
# 克隆项目
git clone https://github.com/your-username/guitar.git
cd guitar

# 安装依赖
npm install

# 启动服务器（localhost:3000）
npm start

# 或开发模式（支持热重载）
npm run dev
```

打开浏览器访问 `http://localhost:3000`

### 云部署（推荐）

#### Railway 部署（1 分钟快速部署）

1. Fork 此项目到你的 GitHub
2. 访问 https://railway.app，使用 GitHub 登录
3. 创建 New Project → Deploy from GitHub
4. 选择你的 `guitar` 仓库
5. 自动部署完成！获得公网 URL

**优势**：免费额度充足、自动重启、支持环境变量管理

#### Vercel 部署

```bash
npm install -g vercel
vercel
# 按提示选择项目目录和关联账号
```

#### 自建服务器（VPS）

详见 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 📖 使用指南

### 查看谱子

1. 首页列出所有可用谱子
2. 点击任意谱子进入详情页
3. 查看谱子信息和图片

### 全屏自动滚动

1. 点击"全屏查看"按钮
2. 选择滚动模式：
   - **自定义时间戳**：根据配置的时间戳按设定速度滚动
   - **匀速滚动**：恒定速度从头到尾滚动
3. 点击"自动滚动"开始播放
4. 按 ESC 或点击关闭按钮退出全屏

### 录制时间戳（为谱子配置自动滚动速度）

1. 全屏模式下，点击"录制时间戳"按钮（蓝色十字图标）
2. 进入录制模式后，点击谱子上的位置
3. 在弹出框输入该位置对应的**时间戳**（秒）
   - 例如：第一张图片顶部 → 0s
   - 第二张图片顶部 → 5s
   - 第三张图片底部 → 10s
4. 重复步骤 2-3 录制多个时间戳
5. 再次点击"录制时间戳"退出，确认保存

系统会在 `tabs-config.json` 中自动保存这些配置，下次打开时自动使用。

### 收藏谱子

- 点击谱子卡片右上角的星形按钮收藏
- 收藏信息保存在浏览器本地存储（localStorage）
- 点击"我的收藏"查看所有收藏谱子

## 🔧 API 文档

### 获取所有谱子配置

```bash
GET /api/tabs
```

### 获取单个谱子配置

```bash
GET /api/tabs/:tabKey
```

### 保存时间戳配置

```bash
POST /api/save-config

请求体：
{
  "tabKey": "成都",
  "scroll": [
    { "time": 0, "position": 0 },
    { "time": 5, "position": 400 },
    { "time": 10, "position": 800 }
  ]
}
```

## 📁 项目结构

```
.
├── server.js               # Express 后端服务
├── public/                 # 前端资源
│   ├── index.html          # 首页
│   ├── tab-detail.html     # 谱子详情页
│   └── source/             # 谱子 PNG 图片
│       ├── 晴天/
│       ├── 成都/
│       ├── 卡农/
│       └── 我们俩/
├── tabs-config.json        # 配置文件（核心数据）
├── manage-config.js        # 配置管理工具
├── package.json            # 依赖配置
├── .env.example            # 环境变量示例
├── railway.toml            # Railway 部署配置
├── vercel.json             # Vercel 部署配置
└── DEPLOYMENT.md           # 详细部署指南
```

## 🎨 技术栈

- **前端**：HTML5 + Tailwind CSS + Vanilla JavaScript
- **后端**：Express.js + Node.js
- **存储**：JSON 文件 + localStorage
- **部署**：Railway / Vercel / 自建 VPS

## 🔐 环保建议

### 本地维护

修改 `tabs-config.json` 手动添加谱子：

```json
{
  "新歌曲": {
    "id": "5",
    "singer": "歌手名",
    "type": "弹唱",
    "view": "1000",
    "download": "100",
    "cover": "https://...",
    "scroll": [
      { "time": 0, "position": 0 },
      { "time": 5, "position": 400 }
    ]
  }
}
```

### 添加谱子图片

在 `public/source/` 下创建歌曲文件夹，添加 `1.png`, `2.png` ... 等图片文件

```bash
mkdir -p public/source/新歌曲
cp 1.png 2.png ... public/source/新歌曲/
```

## 📝 配置管理工具

使用交互式工具管理配置：

```bash
node manage-config.js
```

菜单选项：
- 1: 查看谱子详情
- 2: 编辑谱子信息
- 3: 新增谱子
- 4: 删除谱子

## 🌍 环境变量

复制 `.env.example` 到 `.env`：

```bash
PORT=3000                           # 服务器端口
NODE_ENV=development                # 环境（development/production）
CORS_ORIGIN=http://localhost:3000   # 允许的跨域来源
```

## 🐛 常见问题

**Q: 谱子图片加载失败怎么办？**
A: 检查 `public/source/` 目录结构，确保图片命名为 `1.png`, `2.png` ...

**Q: 自动滚动不工作？**
A: 需要先在全屏模式下使用"录制时间戳"功能配置滚动参数

**Q: 怎么在线上修改配置？**
A: 使用"录制时间戳"功能，或通过 API 调用 `POST /api/save-config`

**Q: 支持多用户管理吗？**
A: 当前版本不支持，可基于此项目扩展添加数据库和用户认证

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

ISC

## 📞 联系方式

- GitHub: https://github.com/3111825083/guitar
- Email: 3111825083@qq.com

---

**祝你弹琴愉快！🎵**