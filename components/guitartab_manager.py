import json
class GuitarTabManager:
    """吉他谱管理器"""

    def __init__(self, config_file='./source/tabs-config.json'):
        self.config_file = config_file
        self.tabs_data = {}
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.tabs_data = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")

    def get_all_tabs(self):
        """获取所有吉他谱列表"""
        return self.tabs_data

    def get_tab_detail(self, tab_name):
        """获取指定吉他谱详情"""
        return self.tabs_data.get(tab_name, {})

    def search_tabs(self, keyword):
        """搜索吉他谱"""
        result = {}
        keyword = keyword.lower()
        for name, info in self.tabs_data.items():
            if (keyword in name.lower() or
                    keyword in info.get('singer', '').lower() or
                    keyword in info.get('type', '').lower()):
                result[name] = info
        return result
    def add_tab(self, tab_name, tab_info):
        """添加新歌曲"""
        try:
            self.tabs_data[tab_name] = tab_info
            self.save_config()
            return True
        except Exception as e:
            print(f"添加歌曲失败: {e}")
            return False

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.tabs_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
