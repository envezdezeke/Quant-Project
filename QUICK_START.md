# Quick Start Guide

Get up and running with your quantitative trading project in minutes.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (optional, for version control)

## Installation

### 1. Set up virtual environment (recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Note: If `ta-lib` fails to install, you may need to install it separately:
```bash
# macOS
brew install ta-lib
pip install ta-lib

# Ubuntu/Debian
sudo apt-get install ta-lib
pip install ta-lib

# Windows
# Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# Then: pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl
```

If you have issues with `ta-lib`, you can comment it out in `requirements.txt` and use `pandas-ta` instead.

## Your First Backtest

### Option 1: Run the default example

```bash
python main.py
```

This will:
- Download data for configured stocks
- Run 3 different strategy backtests
- Perform portfolio optimization
- Generate performance plots
- Display comprehensive metrics

### Option 2: Interactive Jupyter notebook

```bash
jupyter notebook notebooks/example_analysis.ipynb
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
strategy:
  universe: ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]  # Your stocks
  lookback_period: 20

trading:
  initial_capital: 100000
  commission: 0.001

backtesting:
  start_date: "2020-01-01"
  end_date: null  # null = today
```

## Project Structure Overview

```
├── config/              # Configuration files
├── data/               # Data handling & caching
├── strategies/         # Alpha strategy implementations
├── backtesting/        # Backtesting engine
├── portfolio/          # Optimization & risk management
├── utils/              # Utilities & metrics
├── notebooks/          # Jupyter notebooks
└── main.py            # Main entry point
```

## Basic Usage Examples

### Example 1: Run a Single Strategy

```python
from data.data_handler import DataHandler
from strategies.momentum_strategy import MomentumStrategy
from backtesting.backtest_engine import BacktestEngine

# Get data
data_handler = DataHandler()
data = data_handler.get_data(['AAPL', 'MSFT', 'GOOGL'], '2020-01-01')

# Create and run strategy
strategy = MomentumStrategy(lookback_period=20, top_n=3)
engine = BacktestEngine(initial_capital=100000)
results = engine.run(strategy, data)

# View results
engine.print_results(results)
```

### Example 2: Optimize Portfolio

```python
from portfolio.portfolio_optimizer import PortfolioOptimizer

# Calculate statistics
stats = data_handler.calculate_statistics(data)

# Optimize
optimizer = PortfolioOptimizer(stats['mean_returns'], stats['cov_matrix'])
max_sharpe = optimizer.max_sharpe_ratio()

print(f"Expected Return: {max_sharpe['return']*100:.2f}%")
print(f"Sharpe Ratio: {max_sharpe['sharpe_ratio']:.2f}")
print("Weights:", max_sharpe['weights'])
```

### Example 3: Create a Custom Strategy

```python
from strategies.base_strategy import BaseStrategy
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    def __init__(self, param1=10):
        super().__init__(name="My Strategy", lookback_period=20)
        self.param1 = param1

    def calculate_alpha(self, data: pd.DataFrame) -> pd.Series:
        # Your alpha calculation logic
        returns = data.pct_change(self.param1)
        return returns.iloc[-1]

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Your signal generation logic
        signals = pd.DataFrame(0, index=data.index, columns=data.columns)
        # ... implement your logic
        return signals

# Use it
strategy = MyCustomStrategy(param1=15)
results = engine.run(strategy, data)
```

## Common Tasks

### Download and cache data
```python
data_handler = DataHandler()
data = data_handler.get_data(['AAPL', 'MSFT'], '2020-01-01', '2024-01-01')
```

### Calculate technical indicators
```python
data_with_indicators = data_handler.add_technical_indicators(
    data,
    indicators=['SMA_20', 'SMA_50', 'RSI', 'MACD']
)
```

### Generate performance plots
```python
from utils.plotting import PerformancePlotter

plotter = PerformancePlotter()
plotter.plot_portfolio_value(results['portfolio_series'])
plotter.plot_drawdown(results['portfolio_series'])
plotter.plot_returns(results['returns_series'])
```

### Calculate risk metrics
```python
from portfolio.risk_manager import RiskManager

risk_mgr = RiskManager()
risk_metrics = risk_mgr.calculate_risk_metrics(
    returns,
    portfolio_series,
    benchmark_returns
)
print(risk_metrics)
```

## Troubleshooting

### Issue: "Module not found"
```bash
# Make sure you're in the project root and venv is activated
pip install -r requirements.txt
```

### Issue: Data download fails
```bash
# Try manual download with specific dates
python -c "import yfinance as yf; print(yf.download('AAPL', '2020-01-01', '2024-01-01'))"
```

### Issue: Plots not showing
```bash
# For Jupyter notebooks
%matplotlib inline

# For scripts, add:
import matplotlib.pyplot as plt
plt.show()
```

## Next Steps

1. **Explore**: Run the example notebook to understand the framework
2. **Customize**: Modify `config.yaml` with your preferred settings
3. **Develop**: Create your own strategy by extending `BaseStrategy`
4. **Plan**: Use the Gemini planning prompt to create your roadmap
   - See: `HOW_TO_USE_GEMINI_PROMPT.md`
5. **Test**: Add unit tests as you develop new features
6. **Iterate**: Backtest, analyze, refine, repeat

## Learning Resources

- **Documentation**: See `README.md` for detailed documentation
- **Planning**: Use `gemini_planning_prompt.txt` with Gemini AI to create a project plan
- **Template**: Review `PLANNING_TEMPLATE.md` for project planning structure
- **Examples**: Check `notebooks/example_analysis.ipynb` for interactive examples

## Performance Tips

- Enable data caching (default: on) to speed up repeated backtests
- Use vectorized operations in custom strategies
- Limit the date range during development for faster iteration
- Use fewer tickers initially to test strategy logic

## Getting Help

- Check the README.md for detailed documentation
- Review example_analysis.ipynb for usage patterns
- Ensure all dependencies are installed correctly
- Check that data is downloading successfully

---

**Ready to build your alpha strategies?** Start with `python main.py` and explore from there!
