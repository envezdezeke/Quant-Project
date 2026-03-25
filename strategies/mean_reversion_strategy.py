import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    def __init__(self, lookback_period: int = 20, entry_threshold: float = 2.0,
                 exit_threshold: float = 0.5):
        super().__init__(name="Mean Reversion Strategy", lookback_period=lookback_period)
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold

    def calculate_alpha(self, data: pd.DataFrame) -> pd.Series:
        returns = data.pct_change()
        rolling_mean = returns.rolling(window=self.lookback_period).mean()
        rolling_std = returns.rolling(window=self.lookback_period).std()

        z_score = (returns - rolling_mean) / rolling_std
        return -z_score.iloc[-1]

    def calculate_z_score(self, data: pd.DataFrame) -> pd.DataFrame:
        returns = data.pct_change()
        rolling_mean = returns.rolling(window=self.lookback_period).mean()
        rolling_std = returns.rolling(window=self.lookback_period).std()

        z_score = (returns - rolling_mean) / rolling_std
        return z_score

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        self.validate_data(data)
        data = self.preprocess_data(data)

        z_scores = self.calculate_z_score(data)

        signals = pd.DataFrame(0, index=data.index, columns=data.columns)
        positions = pd.DataFrame(0, index=data.index, columns=data.columns)

        for i in range(self.lookback_period, len(data)):
            if i > 0:
                positions.iloc[i] = positions.iloc[i-1]

            current_z = z_scores.iloc[i]

            oversold = current_z < -self.entry_threshold
            overbought = current_z > self.entry_threshold

            exit_long = current_z > -self.exit_threshold
            exit_short = current_z < self.exit_threshold

            positions.iloc[i][oversold] = 1
            positions.iloc[i][overbought] = -1

            positions.iloc[i][(positions.iloc[i] == 1) & exit_long] = 0
            positions.iloc[i][(positions.iloc[i] == -1) & exit_short] = 0

            if i > 0:
                signals.iloc[i] = positions.iloc[i] - positions.iloc[i-1]

        self.signals = signals
        return signals

    def get_metrics(self) -> dict:
        metrics = super().get_metrics()
        metrics.update({
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold,
        })
        return metrics
