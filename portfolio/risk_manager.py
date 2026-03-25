import numpy as np
import pandas as pd
from typing import Dict, Optional
from scipy import stats


class RiskManager:
    def __init__(self, max_position_size: float = 0.25,
                 max_drawdown: float = 0.20,
                 stop_loss: float = 0.05,
                 take_profit: float = 0.15):
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def calculate_var(self, returns: pd.Series,
                     confidence_level: float = 0.95) -> float:
        if len(returns) == 0:
            return 0
        return np.percentile(returns, (1 - confidence_level) * 100)

    def calculate_cvar(self, returns: pd.Series,
                      confidence_level: float = 0.95) -> float:
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()

    def calculate_drawdown(self, portfolio_series: pd.Series) -> pd.Series:
        cumulative = portfolio_series
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown

    def check_position_limits(self, positions: pd.Series,
                            portfolio_value: float) -> pd.Series:
        adjusted_positions = positions.copy()

        for ticker in positions.index:
            position_value = abs(positions[ticker])
            if position_value / portfolio_value > self.max_position_size:
                adjusted_positions[ticker] = (
                    np.sign(positions[ticker]) *
                    self.max_position_size *
                    portfolio_value
                )

        return adjusted_positions

    def should_stop_trading(self, portfolio_series: pd.Series) -> bool:
        drawdown = self.calculate_drawdown(portfolio_series)
        current_drawdown = abs(drawdown.iloc[-1])
        return current_drawdown >= self.max_drawdown

    def calculate_position_size(self, capital: float,
                               risk_per_trade: float,
                               entry_price: float,
                               stop_loss_price: float) -> int:
        risk_amount = capital * risk_per_trade
        price_risk = abs(entry_price - stop_loss_price)

        if price_risk > 0:
            position_size = int(risk_amount / price_risk)
            return position_size
        return 0

    def calculate_kelly_criterion(self, win_rate: float,
                                  avg_win: float,
                                  avg_loss: float) -> float:
        if avg_loss == 0:
            return 0

        win_loss_ratio = abs(avg_win / avg_loss)
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        return max(0, min(kelly, 0.25))

    def calculate_risk_metrics(self, returns: pd.Series,
                              portfolio_series: pd.Series,
                              benchmark_returns: Optional[pd.Series] = None) -> Dict:
        metrics = {
            'var_95': self.calculate_var(returns, 0.95),
            'cvar_95': self.calculate_cvar(returns, 0.95),
            'max_drawdown': self.calculate_drawdown(portfolio_series).min(),
            'volatility': returns.std() * np.sqrt(252),
            'downside_deviation': self._downside_deviation(returns),
            'sortino_ratio': self._sortino_ratio(returns)
        }

        if benchmark_returns is not None:
            metrics['beta'] = self._calculate_beta(returns, benchmark_returns)
            metrics['alpha'] = self._calculate_alpha(returns, benchmark_returns)

        return metrics

    def _downside_deviation(self, returns: pd.Series,
                           target_return: float = 0) -> float:
        downside_returns = returns[returns < target_return]
        return downside_returns.std() * np.sqrt(252)

    def _sortino_ratio(self, returns: pd.Series,
                      target_return: float = 0,
                      risk_free_rate: float = 0.02) -> float:
        excess_returns = returns.mean() * 252 - risk_free_rate
        downside_dev = self._downside_deviation(returns, target_return)

        if downside_dev > 0:
            return excess_returns / downside_dev
        return 0

    def _calculate_beta(self, returns: pd.Series,
                       benchmark_returns: pd.Series) -> float:
        aligned_returns = pd.concat([returns, benchmark_returns], axis=1).dropna()
        if len(aligned_returns) > 1:
            covariance = aligned_returns.cov().iloc[0, 1]
            benchmark_variance = aligned_returns.iloc[:, 1].var()
            return covariance / benchmark_variance if benchmark_variance > 0 else 0
        return 0

    def _calculate_alpha(self, returns: pd.Series,
                        benchmark_returns: pd.Series,
                        risk_free_rate: float = 0.02) -> float:
        beta = self._calculate_beta(returns, benchmark_returns)
        portfolio_return = returns.mean() * 252
        benchmark_return = benchmark_returns.mean() * 252

        alpha = portfolio_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))
        return alpha

    def apply_stop_loss_take_profit(self, entry_prices: pd.Series,
                                   current_prices: pd.Series,
                                   positions: pd.Series) -> pd.Series:
        adjusted_positions = positions.copy()

        for ticker in positions.index:
            if positions[ticker] == 0:
                continue

            entry_price = entry_prices[ticker]
            current_price = current_prices[ticker]

            if entry_price > 0:
                price_change = (current_price - entry_price) / entry_price

                if positions[ticker] > 0:
                    if price_change <= -self.stop_loss or price_change >= self.take_profit:
                        adjusted_positions[ticker] = 0

                elif positions[ticker] < 0:
                    if price_change >= self.stop_loss or price_change <= -self.take_profit:
                        adjusted_positions[ticker] = 0

        return adjusted_positions
