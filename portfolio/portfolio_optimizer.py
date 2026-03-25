import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Tuple


class PortfolioOptimizer:
    def __init__(self, mean_returns: pd.Series, cov_matrix: pd.DataFrame):
        self.mean_returns = mean_returns
        self.cov_matrix = cov_matrix
        self.num_assets = len(mean_returns)

    def portfolio_stats(self, weights: np.ndarray) -> Tuple[float, float, float]:
        portfolio_return = np.dot(weights, self.mean_returns)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
        return portfolio_return, portfolio_std, sharpe_ratio

    def negative_sharpe(self, weights: np.ndarray, risk_free_rate: float = 0.02) -> float:
        p_return, p_std, _ = self.portfolio_stats(weights)
        return -(p_return - risk_free_rate) / p_std if p_std > 0 else 0

    def max_sharpe_ratio(self, risk_free_rate: float = 0.02) -> Dict:
        num_assets = self.num_assets
        args = (risk_free_rate,)
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(num_assets))
        initial_guess = num_assets * [1. / num_assets]

        result = minimize(
            self.negative_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            args=args
        )

        weights = result.x
        p_return, p_std, p_sharpe = self.portfolio_stats(weights)

        return {
            'weights': pd.Series(weights, index=self.mean_returns.index),
            'return': p_return,
            'volatility': p_std,
            'sharpe_ratio': p_sharpe
        }

    def min_volatility(self) -> Dict:
        num_assets = self.num_assets

        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))

        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(num_assets))
        initial_guess = num_assets * [1. / num_assets]

        result = minimize(
            portfolio_volatility,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights = result.x
        p_return, p_std, p_sharpe = self.portfolio_stats(weights)

        return {
            'weights': pd.Series(weights, index=self.mean_returns.index),
            'return': p_return,
            'volatility': p_std,
            'sharpe_ratio': p_sharpe
        }

    def efficient_frontier(self, num_portfolios: int = 100) -> pd.DataFrame:
        results = {
            'returns': [],
            'volatility': [],
            'sharpe_ratio': []
        }

        target_returns = np.linspace(
            self.mean_returns.min(),
            self.mean_returns.max(),
            num_portfolios
        )

        for target_return in target_returns:
            weights = self._efficient_portfolio(target_return)
            if weights is not None:
                p_return, p_std, p_sharpe = self.portfolio_stats(weights)
                results['returns'].append(p_return)
                results['volatility'].append(p_std)
                results['sharpe_ratio'].append(p_sharpe)

        return pd.DataFrame(results)

    def _efficient_portfolio(self, target_return: float) -> np.ndarray:
        num_assets = self.num_assets

        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))

        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.dot(x, self.mean_returns) - target_return}
        ]
        bounds = tuple((0, 1) for _ in range(num_assets))
        initial_guess = num_assets * [1. / num_assets]

        result = minimize(
            portfolio_volatility,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x if result.success else None

    def equal_weight(self) -> Dict:
        weights = np.array([1.0 / self.num_assets] * self.num_assets)
        p_return, p_std, p_sharpe = self.portfolio_stats(weights)

        return {
            'weights': pd.Series(weights, index=self.mean_returns.index),
            'return': p_return,
            'volatility': p_std,
            'sharpe_ratio': p_sharpe
        }

    def risk_parity(self) -> Dict:
        def risk_budget_objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            marginal_contrib = np.dot(self.cov_matrix, weights)
            contrib = weights * marginal_contrib / portfolio_vol
            target = portfolio_vol / self.num_assets
            return sum((contrib - target) ** 2)

        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(self.num_assets))
        initial_guess = self.num_assets * [1. / self.num_assets]

        result = minimize(
            risk_budget_objective,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights = result.x
        p_return, p_std, p_sharpe = self.portfolio_stats(weights)

        return {
            'weights': pd.Series(weights, index=self.mean_returns.index),
            'return': p_return,
            'volatility': p_std,
            'sharpe_ratio': p_sharpe
        }
