import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional


class PerformanceMetrics:
    @staticmethod
    def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
        return prices.pct_change().dropna()

    @staticmethod
    def cumulative_returns(returns: pd.Series) -> pd.Series:
        return (1 + returns).cumprod() - 1

    @staticmethod
    def total_return(prices: pd.Series) -> float:
        return (prices.iloc[-1] / prices.iloc[0] - 1) * 100

    @staticmethod
    def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
        cumulative_return = (1 + returns).prod() - 1
        num_years = len(returns) / periods_per_year
        if num_years > 0:
            return (((1 + cumulative_return) ** (1 / num_years)) - 1) * 100
        return 0

    @staticmethod
    def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
        return returns.std() * np.sqrt(periods_per_year) * 100

    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                    periods_per_year: int = 252) -> float:
        excess_returns = returns - risk_free_rate / periods_per_year
        if excess_returns.std() > 0:
            return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()
        return 0

    @staticmethod
    def sortino_ratio(returns: pd.Series, target_return: float = 0,
                     risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = returns[returns < target_return]

        if len(downside_returns) > 0 and downside_returns.std() > 0:
            downside_std = downside_returns.std()
            return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std
        return 0

    @staticmethod
    def max_drawdown(prices: pd.Series) -> float:
        cumulative = prices
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min() * 100

    @staticmethod
    def calmar_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
        annual_return = PerformanceMetrics.annualized_return(returns, periods_per_year)
        prices = (1 + returns).cumprod()
        max_dd = abs(PerformanceMetrics.max_drawdown(prices))

        if max_dd > 0:
            return annual_return / max_dd
        return 0

    @staticmethod
    def win_rate(returns: pd.Series) -> float:
        if len(returns) > 0:
            return (returns > 0).sum() / len(returns) * 100
        return 0

    @staticmethod
    def profit_factor(returns: pd.Series) -> float:
        wins = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())

        if losses > 0:
            return wins / losses
        return 0

    @staticmethod
    def information_ratio(returns: pd.Series, benchmark_returns: pd.Series,
                         periods_per_year: int = 252) -> float:
        active_returns = returns - benchmark_returns
        tracking_error = active_returns.std() * np.sqrt(periods_per_year)

        if tracking_error > 0:
            return (active_returns.mean() * periods_per_year) / tracking_error
        return 0

    @staticmethod
    def beta(returns: pd.Series, benchmark_returns: pd.Series) -> float:
        aligned = pd.concat([returns, benchmark_returns], axis=1).dropna()
        if len(aligned) > 1:
            covariance = aligned.cov().iloc[0, 1]
            benchmark_variance = aligned.iloc[:, 1].var()
            return covariance / benchmark_variance if benchmark_variance > 0 else 0
        return 0

    @staticmethod
    def alpha(returns: pd.Series, benchmark_returns: pd.Series,
             risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
        beta_value = PerformanceMetrics.beta(returns, benchmark_returns)
        portfolio_return = returns.mean() * periods_per_year
        benchmark_return = benchmark_returns.mean() * periods_per_year

        alpha_value = portfolio_return - (risk_free_rate + beta_value * (benchmark_return - risk_free_rate))
        return alpha_value * 100

    @staticmethod
    def calculate_all_metrics(returns: pd.Series,
                            benchmark_returns: Optional[pd.Series] = None,
                            risk_free_rate: float = 0.02) -> Dict:
        prices = (1 + returns).cumprod()

        metrics = {
            'Total Return (%)': PerformanceMetrics.total_return(prices),
            'Annual Return (%)': PerformanceMetrics.annualized_return(returns),
            'Volatility (%)': PerformanceMetrics.annualized_volatility(returns),
            'Sharpe Ratio': PerformanceMetrics.sharpe_ratio(returns, risk_free_rate),
            'Sortino Ratio': PerformanceMetrics.sortino_ratio(returns, risk_free_rate=risk_free_rate),
            'Max Drawdown (%)': PerformanceMetrics.max_drawdown(prices),
            'Calmar Ratio': PerformanceMetrics.calmar_ratio(returns),
            'Win Rate (%)': PerformanceMetrics.win_rate(returns),
            'Profit Factor': PerformanceMetrics.profit_factor(returns)
        }

        if benchmark_returns is not None:
            metrics['Beta'] = PerformanceMetrics.beta(returns, benchmark_returns)
            metrics['Alpha (%)'] = PerformanceMetrics.alpha(returns, benchmark_returns, risk_free_rate)
            metrics['Information Ratio'] = PerformanceMetrics.information_ratio(returns, benchmark_returns)

        return metrics

    @staticmethod
    def print_metrics(metrics: Dict):
        print("\n" + "="*60)
        print("PERFORMANCE METRICS")
        print("="*60)
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"{key:<25} {value:>10.2f}")
            else:
                print(f"{key:<25} {value:>10}")
        print("="*60)
