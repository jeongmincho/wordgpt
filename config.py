"""
WordGPT - AI-Powered Vocabulary Card Generator for Anki
Copyright (c) 2024 jeongminc_
MIT License - See LICENSE file for details
"""

from aqt import mw
from aqt.utils import showInfo
from typing import Any, Dict

PACKAGE_NAME = "wordgpt" 

class ConfigManager:
    def __init__(self):
        self.default_config = {
            'include_synonyms': True,
            'include_examples': True
        }

    def get_config(self) -> Dict[str, Any]:
        """Load config from disk, creating default if it doesn't exist"""
        try:
            config = mw.addonManager.getConfig(PACKAGE_NAME)
            if config is None:
                mw.addonManager.writeConfig(PACKAGE_NAME, self.default_config)
                return self.default_config
            return config
        except Exception as e:
            return self.default_config

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save config to disk"""
        try:
            mw.addonManager.writeConfig(PACKAGE_NAME, config)
            return True
        except Exception:
            return False

    def update_config(self, key: str, value: Any) -> bool:
        """Update a single config value"""
        config = self.get_config()
        config[key] = value
        return self.save_config(config)

# Create a global instance
config = ConfigManager()
