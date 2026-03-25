import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional


class PerformancePlotter:
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
        sns.set_palette("husl")

    def plot_portfolio_value(self, portfolio_series: pd.Series,
                            benchmark_series: Optional[pd.Series] = None,
                            title: str = "Portfolio Value Over Time"):
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(portfolio_series.index, portfolio_series.values,
               label='Portfolio', linewidth=2)

        if benchmark_series is not None:
            benchmark_normalized = benchmark_series / benchmark_series.iloc[0] * portfolio_series.iloc[0]
            ax.plot(benchmark_series.index, benchmark_normalized.values,
                   label='Benchmark', linewidth=2, alpha=0.7)

        ax.set_xlabel('Date')
        ax.set_ylabel('Portfolio Value ($)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    def plot_returns(self, returns: pd.Series,
                    benchmark_returns: Optional[pd.Series] = None,
                    title: str = "Cumulative Returns"):
        fig, ax = plt.subplots(figsize=(12, 6))

        cumulative_returns = (1 + returns).cumprod() - 1
        ax.plot(cumulative_returns.index, cumulative_returns.values * 100,
               label='Strategy', linewidth=2)

        if benchmark_returns is not None:
            benchmark_cumulative = (1 + benchmark_returns).cumprod() - 1
            ax.plot(benchmark_cumulative.index, benchmark_cumulative.values * 100,
                   label='Benchmark', linewidth=2, alpha=0.7)

        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Returns (%)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        plt.tight_layout()
        return fig

    def plot_drawdown(self, portfolio_series: pd.Series,
                     title: str = "Drawdown Over Time"):
        fig, ax = plt.subplots(figsize=(12, 6))

        running_max = portfolio_series.expanding().max()
        drawdown = (portfolio_series - running_max) / running_max * 100

        ax.fill_between(drawdown.index, drawdown.values, 0,
                       alpha=0.3, color='red', label='Drawdown')
        ax.plot(drawdown.index, drawdown.values, color='red', linewidth=1)

        ax.set_xlabel('Date')
        ax.set_ylabel('Drawdown (%)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    def plot_returns_distribution(self, returns: pd.Series,
                                  title: str = "Returns Distribution"):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        ax1.hist(returns * 100, bins=50, alpha=0.75, edgecolor='black')
        ax1.set_xlabel('Returns (%)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Returns Histogram')
        ax1.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax1.grid(True, alpha=0.3)

        from scipy import stats
        stats.probplot(returns, dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot')
        ax2.grid(True, alpha=0.3)

        fig.suptitle(title)
        plt.tight_layout()
        return fig

    def plot_monthly_returns_heatmap(self, returns: pd.Series,
                                    title: str = "Monthly Returns Heatmap"):
        monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)

        monthly_table = pd.DataFrame({
            'Year': monthly_returns.index.year,
            'Month': monthly_returns.index.month,
            'Return': monthly_returns.values * 100
        })

        pivot_table = monthly_table.pivot(index='Month', columns='Year', values='Return')

        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        pivot_table.index = [month_names[i-1] for i in pivot_table.index]

        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdYlGn',
                   center=0, ax=ax, cbar_kws={'label': 'Return (%)'})
        ax.set_title(title)
        plt.tight_layout()
        return fig

    def plot_rolling_metrics(self, returns: pd.Series, window: int = 252,
                            title: str = "Rolling Performance Metrics"):
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))

        rolling_return = returns.rolling(window).mean() * 252 * 100
        axes[0].plot(rolling_return.index, rolling_return.values)
        axes[0].set_ylabel('Annual Return (%)')
        axes[0].set_title('Rolling Annual Return')
        axes[0].grid(True, alpha=0.3)

        rolling_vol = returns.rolling(window).std() * np.sqrt(252) * 100
        axes[1].plot(rolling_vol.index, rolling_vol.values, color='orange')
        axes[1].set_ylabel('Volatility (%)')
        axes[1].set_title('Rolling Volatility')
        axes[1].grid(True, alpha=0.3)

        rolling_sharpe = (returns.rolling(window).mean() / returns.rolling(window).std()) * np.sqrt(252)
        axes[2].plot(rolling_sharpe.index, rolling_sharpe.values, color='green')
        axes[2].set_ylabel('Sharpe Ratio')
        axes[2].set_xlabel('Date')
        axes[2].set_title('Rolling Sharpe Ratio')
        axes[2].grid(True, alpha=0.3)
        axes[2].axhline(y=0, color='black', linestyle='--', alpha=0.3)

        fig.suptitle(title)
        plt.tight_layout()
        return fig

    def plot_correlation_matrix(self, returns: pd.DataFrame,
                               title: str = "Asset Correlation Matrix"):
        fig, ax = plt.subplots(figsize=(10, 8))
        correlation = returns.corr()

        sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, ax=ax, square=True,
                   cbar_kws={'label': 'Correlation'})
        ax.set_title(title)
        plt.tight_layout()
        return fig

    @staticmethod
    def save_figure(fig, filename: str, dpi: int = 300):
        fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Figure saved to {filename}")

    def create_performance_report(self, portfolio_series: pd.Series,
                                 returns: pd.Series,
                                 benchmark_series: Optional[pd.Series] = None,
                                 benchmark_returns: Optional[pd.Series] = None):
        figs = []

        figs.append(self.plot_portfolio_value(portfolio_series, benchmark_series))
        figs.append(self.plot_returns(returns, benchmark_returns))
        figs.append(self.plot_drawdown(portfolio_series))
        figs.append(self.plot_returns_distribution(returns))
        figs.append(self.plot_rolling_metrics(returns))

        return figs
