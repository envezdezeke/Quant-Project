import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime


class BacktestEngine:
    def __init__(self, initial_capital: float = 100000,
                 commission: float = 0.001,
                 slippage: float = 0.0005):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.portfolio_value = []
        self.positions = {}
        self.trades = []
        self.cash = initial_capital

    def run(self, strategy, data: pd.DataFrame,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None) -> Dict:
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]

        print(f"Running backtest for {strategy.name}")
        print(f"Period: {data.index[0]} to {data.index[-1]}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")

        signals = strategy.generate_signals(data)

        portfolio_values = []
        cash_history = []
        positions_history = []

        self.cash = self.initial_capital
        positions = pd.Series(0, index=data.columns)

        for date in data.index:
            current_prices = data.loc[date]
            current_signals = signals.loc[date]

            position_value = (positions * current_prices).sum()
            total_value = self.cash + position_value

            for ticker in data.columns:
                signal = current_signals[ticker]
                if signal != 0:
                    price = current_prices[ticker]
                    if pd.isna(price) or price <= 0:
                        continue

                    if signal > 0:
                        shares_to_buy = int((total_value * abs(signal)) / price)
                        if shares_to_buy > 0:
                            cost = shares_to_buy * price * (1 + self.commission + self.slippage)
                            if cost <= self.cash:
                                self.cash -= cost
                                positions[ticker] += shares_to_buy
                                self.trades.append({
                                    'date': date,
                                    'ticker': ticker,
                                    'action': 'BUY',
                                    'shares': shares_to_buy,
                                    'price': price,
                                    'cost': cost
                                })

                    elif signal < 0:
                        shares_to_sell = int((total_value * abs(signal)) / price)
                        shares_to_sell = min(shares_to_sell, positions[ticker])
                        if shares_to_sell > 0:
                            proceeds = shares_to_sell * price * (1 - self.commission - self.slippage)
                            self.cash += proceeds
                            positions[ticker] -= shares_to_sell
                            self.trades.append({
                                'date': date,
                                'ticker': ticker,
                                'action': 'SELL',
                                'shares': shares_to_sell,
                                'price': price,
                                'proceeds': proceeds
                            })

            position_value = (positions * current_prices).sum()
            total_value = self.cash + position_value

            portfolio_values.append(total_value)
            cash_history.append(self.cash)
            positions_history.append(positions.copy())

        self.portfolio_value = pd.Series(portfolio_values, index=data.index)
        self.cash_history = pd.Series(cash_history, index=data.index)

        results = self.calculate_performance_metrics(data)

        return results

    def calculate_performance_metrics(self, data: pd.DataFrame) -> Dict:
        returns = self.portfolio_value.pct_change().dropna()

        total_return = (self.portfolio_value.iloc[-1] / self.initial_capital - 1) * 100
        annual_return = self._annualized_return(returns)
        volatility = returns.std() * np.sqrt(252) * 100
        sharpe_ratio = self._sharpe_ratio(returns)
        max_drawdown = self._max_drawdown(self.portfolio_value) * 100
        win_rate = self._win_rate(returns)

        metrics = {
            'initial_capital': self.initial_capital,
            'final_value': self.portfolio_value.iloc[-1],
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'num_trades': len(self.trades),
            'portfolio_series': self.portfolio_value,
            'returns_series': returns
        }

        return metrics

    def _annualized_return(self, returns: pd.Series) -> float:
        cumulative_return = (1 + returns).prod() - 1
        num_years = len(returns) / 252
        if num_years > 0:
            return (((1 + cumulative_return) ** (1 / num_years)) - 1) * 100
        return 0

    def _sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() > 0:
            return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return 0

    def _max_drawdown(self, portfolio_series: pd.Series) -> float:
        cumulative = portfolio_series
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()

    def _win_rate(self, returns: pd.Series) -> float:
        if len(returns) > 0:
            return (returns > 0).sum() / len(returns) * 100
        return 0

    def print_results(self, results: Dict):
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Capital:    ${results['initial_capital']:,.2f}")
        print(f"Final Value:        ${results['final_value']:,.2f}")
        print(f"Total Return:       {results['total_return']:.2f}%")
        print(f"Annual Return:      {results['annual_return']:.2f}%")
        print(f"Volatility:         {results['volatility']:.2f}%")
        print(f"Sharpe Ratio:       {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:       {results['max_drawdown']:.2f}%")
        print(f"Win Rate:           {results['win_rate']:.2f}%")
        print(f"Number of Trades:   {results['num_trades']}")
        print("="*60)
