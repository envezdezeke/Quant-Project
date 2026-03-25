import yaml
import os
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigLoader:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        load_dotenv()

    def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_env(self, key: str, default: str = None) -> str:
        return os.getenv(key, default)

    @property
    def data_config(self) -> Dict:
        return self.config.get('data', {})

    @property
    def trading_config(self) -> Dict:
        return self.config.get('trading', {})

    @property
    def backtesting_config(self) -> Dict:
        return self.config.get('backtesting', {})

    @property
    def strategy_config(self) -> Dict:
        return self.config.get('strategy', {})

    @property
    def risk_config(self) -> Dict:
        return self.config.get('risk', {})
