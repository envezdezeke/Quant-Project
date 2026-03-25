import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    def __init__(self, lookback_period: int = 20, holding_period: int = 5,
                 top_n: int = 5):
        super().__init__(name="Momentum Strategy", lookback_period=lookback_period)
        self.holding_period = holding_period
        self.top_n = top_n

    def calculate_alpha(self, data: pd.DataFrame) -> pd.Series:
        returns = data.pct_change(self.lookback_period)
        return returns.iloc[-1]

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        self.validate_data(data)
        data = self.preprocess_data(data)

        signals = pd.DataFrame(0, index=data.index, columns=data.columns)

        for i in range(self.lookback_period, len(data)):
            current_data = data.iloc[:i+1]

            momentum = current_data.pct_change(self.lookback_period).iloc[-1]

            momentum = momentum.dropna()

            if len(momentum) == 0:
                continue

            top_stocks = momentum.nlargest(self.top_n).index
            bottom_stocks = momentum.nsmallest(self.top_n).index

            signals.loc[data.index[i], top_stocks] = 1
            signals.loc[data.index[i], bottom_stocks] = -1

        self.signals = signals
        return signals

    def get_metrics(self) -> dict:
        metrics = super().get_metrics()
        metrics.update({
            'holding_period': self.holding_period,
            'top_n': self.top_n,
        })
        return metrics
