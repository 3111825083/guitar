# data_manager.py
import json
import os
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = 'tabs-config.json'):
        self.config_path = config_path
        self.data = {}
        self.load_config()

    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                return True
            return False
        except Exception as e:
            print(f"加载配置文件出错: {e}")
            return False

    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件出错: {e}")
            return False

    def get_tabs(self) -> Dict[str, Any]:
        """获取所有吉他谱"""
        return self.data

    def get_tab(self, name: str) -> Dict[str, Any]:
        """获取指定吉他谱"""
        return self.data.get(name, {})

    def add_tab(self, name: str, info: Dict[str, Any]) -> bool:
        """添加吉他谱"""
        self.data[name] = info
        return self.save_config()

    def update_tab_stats(self, name: str, field: str, value: str) -> bool:
        """更新吉他谱统计信息"""
        if name in self.data:
            self.data[name][field] = value
            return self.save_config()
        return False


class FavoriteManager:
    """收藏管理器"""

    def __init__(self, favorite_file: str = 'favorites.json'):
        self.favorite_file = favorite_file
        self.favorites = set()
        self.load_favorites()

    def load_favorites(self) -> bool:
        """加载收藏列表"""
        try:
            if os.path.exists(self.favorite_file):
                with open(self.favorite_file, 'r', encoding='utf-8') as f:
                    self.favorites = set(json.load(f))
                return True
            return True
        except Exception as e:
            print(f"加载收藏列表出错: {e}")
            return False

    def save_favorites(self) -> bool:
        """保存收藏列表"""
        try:
            with open(self.favorite_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.favorites), f, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存收藏列表出错: {e}")
            return False

    def add_favorite(self, tab_name: str) -> bool:
        """添加收藏"""
        self.favorites.add(tab_name)
        return self.save_favorites()

    def remove_favorite(self, tab_name: str) -> bool:
        """移除收藏"""
        self.favorites.discard(tab_name)
        return self.save_favorites()

    def is_favorite(self, tab_name: str) -> bool:
        """检查是否已收藏"""
        return tab_name in self.favorites

    def get_favorites(self) -> set:
        """获取所有收藏"""
        return self.favorites.copy()
