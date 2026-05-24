"""
設定ファイル読み込みユーティリティ
config.yaml.age (暗号化) を優先して読み、なければ config.yaml (平文) を読む
"""

import os
import subprocess
import yaml

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_ENCRYPTED = os.path.join(CONFIG_DIR, "config.yaml.age")
CONFIG_PLAIN = os.path.join(CONFIG_DIR, "config.yaml")
AGE_KEY = os.path.expanduser("~/.config/age/key.txt")
AGE_BIN = os.path.expanduser("~/bin/age")


def load_config() -> dict:
    """設定を読み込む。暗号化ファイルがあればそちらを優先"""
    if os.path.exists(CONFIG_ENCRYPTED) and os.path.exists(AGE_KEY):
        try:
            result = subprocess.run(
                [AGE_BIN, "-d", "-i", AGE_KEY, CONFIG_ENCRYPTED],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return yaml.safe_load(result.stdout)
        except Exception:
            pass

    # フォールバック: 平文ファイル
    if os.path.exists(CONFIG_PLAIN):
        with open(CONFIG_PLAIN, "r") as f:
            return yaml.safe_load(f)

    raise FileNotFoundError("config.yaml.age も config.yaml も見つかりません")
