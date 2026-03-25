import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MovingAverageCrossover(BaseStrategy):
    def __init__(self, fast_period: int = 10, slow_period: int = 50):
        super().__init__(name="MA Crossover Strategy", lookback_period=slow_period)
        self.fast_period = fast_period
        self.slow_period = slow_period

    def calculate_alpha(self, data: pd.DataFrame) -> pd.Series:
        fast_ma = data.rolling(window=self.fast_period).mean()
        slow_ma = data.rolling(window=self.slow_period).mean()

        alpha = (fast_ma - slow_ma) / slow_ma
        return alpha.iloc[-1]

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        self.validate_data(data)
        data = self.preprocess_data(data)

        fast_ma = data.rolling(window=self.fast_period).mean()
        slow_ma = data.rolling(window=self.slow_period).mean()

        signals = pd.DataFrame(0, index=data.index, columns=data.columns)
        positions = pd.DataFrame(0, index=data.index, columns=data.columns)

        positions[fast_ma > slow_ma] = 1
        positions[fast_ma < slow_ma] = -1

        signals = positions.diff()
        signals.iloc[0] = 0

        self.signals = signals
        return signals

    def get_metrics(self) -> dict:
        metrics = super().get_metrics()
        metrics.update({
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
        })
        return metrics
