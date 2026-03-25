from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class BaseStrategy(ABC):
    def __init__(self, name: str, lookback_period: int = 20):
        self.name = name
        self.lookback_period = lookback_period
        self.positions = {}
        self.signals = None

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_alpha(self, data: pd.DataFrame) -> pd.Series:
        pass

    def get_position_sizes(self, signals: pd.DataFrame,
                          risk_budget: float = 1.0) -> pd.DataFrame:
        position_sizes = signals.copy()
        num_positions = (signals != 0).sum(axis=1)
        num_positions = num_positions.replace(0, 1)

        for col in position_sizes.columns:
            position_sizes[col] = (position_sizes[col] / num_positions) * risk_budget

        return position_sizes

    def validate_data(self, data: pd.DataFrame) -> bool:
        if data is None or data.empty:
            raise ValueError("Data cannot be None or empty")

        if len(data) < self.lookback_period:
            raise ValueError(f"Insufficient data: need at least {self.lookback_period} periods")

        return True

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data = data.fillna(method='ffill').fillna(method='bfill')
        return data

    def get_metrics(self) -> Dict:
        return {
            'strategy_name': self.name,
            'lookback_period': self.lookback_period,
        }
