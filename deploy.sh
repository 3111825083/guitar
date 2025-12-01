#!/bin/bash

# 🎸 吉他谱网 - 一键部署脚本

set -e

echo "======================================"
echo "  🎸 吉他谱网 - 部署工具"
echo "======================================"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装！"
    echo "请从 https://nodejs.org 下载安装"
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Node.js 版本: $NODE_VERSION"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装！"
    exit 1
fi

NPM_VERSION=$(npm -v)
echo "✅ npm 版本: $NPM_VERSION"
echo ""

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
else
    echo "✅ 依赖已安装"
fi
echo ""

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "⚙️  创建环境配置文件..."
    cp .env.example .env
    echo "✅ .env 已创建（可根据需要编辑）"
else
    echo "✅ .env 文件已存在"
fi
echo ""

# 启动开发服务器或生产服务器
if [ "$1" = "prod" ] || [ "$1" = "production" ]; then
    echo "🚀 启动生产服务器..."
    NODE_ENV=production npm start
elif [ "$1" = "test" ]; then
    echo "🧪 运行测试..."
    echo "✅ 健康检查："
    npm start > /tmp/server.log 2>&1 &
    sleep 3
    curl -s http://localhost:3000/api/health | jq .
    pkill -f "node server.js"
else
    echo "🚀 启动开发服务器..."
    echo ""
    echo "📝 可用命令："
    echo "  npm start      - 启动生产服务器"
    echo "  npm run dev    - 启动开发服务器（热重载）"
    echo "  node manage-config.js - 管理配置"
    echo ""
    echo "🌐 访问地址：http://localhost:3000"
    echo ""
    npm start
fi
