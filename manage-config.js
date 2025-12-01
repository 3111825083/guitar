#!/usr/bin/env node

/**
 * 配置管理工具
 * 用于本地管理和维护 tabs-config.json
 */

const fs = require('fs').promises;
const path = require('path');
const readline = require('readline');

const CONFIG_FILE = path.join(__dirname, 'tabs-config.json');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function question(prompt) {
    return new Promise(resolve => rl.question(prompt, resolve));
}

async function main() {
    try {
        const config = JSON.parse(await fs.readFile(CONFIG_FILE, 'utf-8'));
        
        console.log('\n🎸 吉他谱配置管理工具\n');
        console.log('当前配置的谱子：');
        Object.keys(config).forEach((key, idx) => {
            console.log(`${idx + 1}. ${key} (ID: ${config[key].id})`);
        });
        
        const choice = await question('\n选择操作 (1=查看详情 2=编辑 3=新增 4=删除 0=退出): ');
        
        if (choice === '1') {
            const key = await question('输入谱子名称: ');
            if (config[key]) {
                console.log(JSON.stringify(config[key], null, 2));
            } else {
                console.log('❌ 谱子不存在');
            }
        } else if (choice === '2') {
            const key = await question('输入要编辑的谱子名称: ');
            if (config[key]) {
                const field = await question('输入字段名 (scroll/singer/type/view/download): ');
                const value = await question(`输入新值: `);
                config[key][field] = field === 'scroll' ? JSON.parse(value) : value;
                await fs.writeFile(CONFIG_FILE, JSON.stringify(config, null, 2));
                console.log('✅ 配置已更新');
            }
        } else if (choice === '3') {
            const name = await question('输入谱子名称: ');
            if (!config[name]) {
                config[name] = {
                    id: String(Math.max(...Object.values(config).map(c => parseInt(c.id))) + 1),
                    singer: await question('输入歌手: '),
                    type: await question('输入类型 (弹唱/指弹): '),
                    view: await question('输入浏览次数: '),
                    download: await question('输入下载次数: '),
                    cover: await question('输入封面URL: '),
                    scroll: [{ time: 0, position: 0 }]
                };
                await fs.writeFile(CONFIG_FILE, JSON.stringify(config, null, 2));
                console.log('✅ 新谱子已添加');
            } else {
                console.log('❌ 谱子已存在');
            }
        } else if (choice === '4') {
            const key = await question('输入要删除的谱子名称: ');
            if (config[key]) {
                delete config[key];
                await fs.writeFile(CONFIG_FILE, JSON.stringify(config, null, 2));
                console.log('✅ 谱子已删除');
            }
        }
    } catch (error) {
        console.error('❌ 错误:', error.message);
    } finally {
        rl.close();
    }
}

main();
