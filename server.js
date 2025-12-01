const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const CONFIG_FILE = path.join(__dirname, 'tabs-config.json');

// 中间件
app.use(cors({
    origin: process.env.CORS_ORIGIN || ['http://localhost:3000', 'http://localhost:5173'],
    credentials: true
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.static('public'));

// 健康检查
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 获取所有吉他谱配置
app.get('/api/tabs', async (req, res) => {
    try {
        const data = await fs.readFile(CONFIG_FILE, 'utf-8');
        const config = JSON.parse(data);
        res.json(config);
    } catch (error) {
        console.error('读取配置错误:', error);
        res.status(500).json({ error: '读取配置失败', message: error.message });
    }
});

// 获取单个谱子配置
app.get('/api/tabs/:tabKey', async (req, res) => {
    try {
        const { tabKey } = req.params;
        const data = await fs.readFile(CONFIG_FILE, 'utf-8');
        const config = JSON.parse(data);
        
        if (!config[tabKey]) {
            return res.status(404).json({ error: '谱子不存在', tabKey });
        }
        
        res.json(config[tabKey]);
    } catch (error) {
        console.error('读取谱子错误:', error);
        res.status(500).json({ error: '读取失败', message: error.message });
    }
});

// 保存时间戳配置
app.post('/api/save-config', async (req, res) => {
    try {
        const { tabKey, scroll } = req.body;

        if (!tabKey || !Array.isArray(scroll)) {
            return res.status(400).json({ 
                error: '缺少必要参数', 
                message: 'tabKey 和 scroll 数组必须存在' 
            });
        }

        // 读取当前配置
        const data = await fs.readFile(CONFIG_FILE, 'utf-8');
        const config = JSON.parse(data);

        // 验证 tabKey 存在
        if (!config[tabKey]) {
            return res.status(400).json({ 
                error: '谱子不存在', 
                tabKey 
            });
        }

        // 更新 scroll 字段
        config[tabKey].scroll = scroll.map(s => ({
            time: parseFloat(s.time) || 0,
            position: parseInt(s.position) || 0
        }));

        // 备份原配置
        await fs.writeFile(
            CONFIG_FILE.replace('.json', '-backup.json'),
            data,
            'utf-8'
        );

        // 写回文件
        await fs.writeFile(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');

        res.json({ 
            message: '配置已保存',
            tabKey,
            scroll: config[tabKey].scroll 
        });
    } catch (error) {
        console.error('保存配置出错:', error);
        res.status(500).json({ 
            error: '保存失败', 
            message: error.message 
        });
    }
});

// 批量更新配置
app.post('/api/save-all-configs', async (req, res) => {
    try {
        const updatedConfig = req.body;

        if (typeof updatedConfig !== 'object' || Array.isArray(updatedConfig)) {
            return res.status(400).json({ 
                error: '无效的配置格式',
                message: '必须是对象' 
            });
        }

        // 读取验证
        const data = await fs.readFile(CONFIG_FILE, 'utf-8');
        const config = JSON.parse(data);

        // 备份
        await fs.writeFile(
            CONFIG_FILE.replace('.json', '-backup.json'),
            data,
            'utf-8'
        );

        // 合并并保存
        const merged = { ...config, ...updatedConfig };
        await fs.writeFile(CONFIG_FILE, JSON.stringify(merged, null, 2), 'utf-8');

        res.json({ 
            message: '所有配置已保存',
            updatedKeys: Object.keys(updatedConfig)
        });
    } catch (error) {
        console.error('批量更新错误:', error);
        res.status(500).json({ 
            error: '更新失败', 
            message: error.message 
        });
    }
});

// 错误处理
app.use((err, req, res, next) => {
    console.error('错误:', err);
    res.status(err.status || 500).json({
        error: err.message || '服务器错误',
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ 吉他谱服务器启动在 ${PORT} 端口`);
    console.log(`🌐 API 基础地址: http://0.0.0.0:${PORT}`);
    console.log(`📝 配置文件: ${CONFIG_FILE}`);
    console.log(`💾 环境: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = app;
