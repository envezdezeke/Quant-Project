# Quantitative Trading Strategy Project

A comprehensive Python-based quantitative trading framework for developing, backtesting, and analyzing alpha strategies.

## Features

- **Multiple Alpha Strategies**: Momentum, Mean Reversion, Moving Average Crossover
- **Backtesting Engine**: Full-featured backtesting with transaction costs and slippage
- **Portfolio Optimization**: Max Sharpe Ratio, Minimum Volatility, Risk Parity, Equal Weight
- **Risk Management**: VaR, CVaR, drawdown monitoring, position sizing, stop-loss/take-profit
- **Performance Analytics**: Comprehensive metrics including Sharpe, Sortino, Calmar ratios
- **Visualization**: Performance plots, drawdowns, rolling metrics, correlation matrices

## Project Structure

```
Quant-Project/
├── config/
│   └── config.yaml          # Configuration settings
├── data/
│   ├── raw/                 # Raw market data cache
│   ├── processed/           # Processed datasets
│   └── data_handler.py      # Data fetching and processing
├── strategies/
│   ├── base_strategy.py     # Abstract base strategy class
│   ├── momentum_strategy.py
│   ├── mean_reversion_strategy.py
│   └── moving_average_crossover.py
├── backtesting/
│   └── backtest_engine.py   # Backtesting framework
├── portfolio/
│   ├── portfolio_optimizer.py  # Portfolio optimization
│   └── risk_manager.py         # Risk management tools
├── utils/
│   ├── performance_metrics.py  # Performance calculations
│   ├── plotting.py            # Visualization utilities
│   └── config_loader.py       # Configuration management
├── notebooks/               # Jupyter notebooks for analysis
├── tests/                  # Unit tests
├── main.py                 # Main entry point
└── requirements.txt        # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Quant-Project.git
cd Quant-Project
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env with your API keys if needed
```

## Quick Start

See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.

**TL;DR:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run default backtest
python main.py
```

This will:
- Download historical data for configured tickers
- Run multiple strategy backtests
- Perform portfolio optimization
- Generate performance plots
- Display comprehensive metrics

## Project Planning

Want to take this project further? Use our Gemini AI planning prompt:

1. Read [HOW_TO_USE_GEMINI_PROMPT.md](HOW_TO_USE_GEMINI_PROMPT.md)
2. Copy the prompt from [gemini_planning_prompt.txt](gemini_planning_prompt.txt)
3. Submit to [Google Gemini](https://gemini.google.com/)
4. Get a comprehensive project roadmap and development plan

See [PLANNING_TEMPLATE.md](PLANNING_TEMPLATE.md) for the planning document structure.

## Configuration

Edit `config/config.yaml` to customize:

- **Trading universe**: List of tickers to trade
- **Backtest period**: Start and end dates
- **Capital settings**: Initial capital, position sizing
- **Risk parameters**: Stop-loss, take-profit, max drawdown
- **Strategy parameters**: Lookback periods, thresholds

## Creating Custom Strategies

Extend the `BaseStrategy` class:

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, param1=10):
        super().__init__(name="My Strategy", lookback_period=20)
        self.param1 = param1

    def calculate_alpha(self, data):
        # Calculate alpha scores for each asset
        pass

    def generate_signals(self, data):
        # Generate trading signals (1=buy, -1=sell, 0=hold)
        pass
```

## Running Backtests

```python
from backtesting.backtest_engine import BacktestEngine
from strategies.momentum_strategy import MomentumStrategy
from data.data_handler import DataHandler

# Load data
data_handler = DataHandler()
data = data_handler.get_data(['AAPL', 'MSFT'], '2020-01-01', '2023-12-31')

# Create strategy and backtest
strategy = MomentumStrategy(lookback_period=20, top_n=3)
engine = BacktestEngine(initial_capital=100000)
results = engine.run(strategy, data)

# View results
engine.print_results(results)
```

## Portfolio Optimization

```python
from portfolio.portfolio_optimizer import PortfolioOptimizer

# Calculate statistics
stats = data_handler.calculate_statistics(data)

# Optimize portfolio
optimizer = PortfolioOptimizer(stats['mean_returns'], stats['cov_matrix'])
max_sharpe_portfolio = optimizer.max_sharpe_ratio()
min_vol_portfolio = optimizer.min_volatility()
risk_parity_portfolio = optimizer.risk_parity()
```

## Performance Metrics

The framework calculates:

- **Return Metrics**: Total return, annual return, CAGR
- **Risk Metrics**: Volatility, VaR, CVaR, max drawdown
- **Risk-Adjusted**: Sharpe ratio, Sortino ratio, Calmar ratio
- **Relative Performance**: Alpha, Beta, Information ratio
- **Trade Statistics**: Win rate, profit factor, number of trades

## Visualization

```python
from utils.plotting import PerformancePlotter

plotter = PerformancePlotter()

# Create visualizations
plotter.plot_portfolio_value(results['portfolio_series'])
plotter.plot_returns(results['returns_series'])
plotter.plot_drawdown(results['portfolio_series'])
plotter.plot_rolling_metrics(results['returns_series'])
```

## Risk Management

```python
from portfolio.risk_manager import RiskManager

risk_manager = RiskManager(
    max_position_size=0.25,
    max_drawdown=0.20,
    stop_loss=0.05,
    take_profit=0.15
)

# Calculate risk metrics
risk_metrics = risk_manager.calculate_risk_metrics(
    returns, portfolio_series, benchmark_returns
)

# Check position limits
adjusted_positions = risk_manager.check_position_limits(positions, portfolio_value)
```

## Example Strategies

### Momentum Strategy
Buys top N performers based on price momentum over lookback period.

### Mean Reversion Strategy
Trades based on z-scores, buying oversold and selling overbought assets.

### Moving Average Crossover
Generates signals when fast MA crosses above/below slow MA.

## Development

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black .
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Disclaimer

This software is for educational and research purposes only. It is not financial advice. Always do your own research and consult with financial professionals before making investment decisions. Past performance does not guarantee future results.

## License

MIT License - see LICENSE file for details

## Resources

- [Quantitative Finance Tutorial](https://www.quantstart.com/)
- [Python for Finance](https://www.oreilly.com/library/view/python-for-finance/9781492024323/)
- [Algorithmic Trading](https://www.investopedia.com/articles/active-trading/101014/basics-algorithmic-trading-concepts-and-examples.asp)
