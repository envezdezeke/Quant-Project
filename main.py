import warnings
warnings.filterwarnings('ignore')

from data.data_handler import DataHandler
from strategies.momentum_strategy import MomentumStrategy
from strategies.mean_reversion_strategy import MeanReversionStrategy
from strategies.moving_average_crossover import MovingAverageCrossover
from backtesting.backtest_engine import BacktestEngine
from portfolio.portfolio_optimizer import PortfolioOptimizer
from utils.plotting import PerformancePlotter
from utils.config_loader import ConfigLoader


def main():
    print("="*60)
    print("QUANTITATIVE TRADING STRATEGY BACKTESTER")
    print("="*60)

    config = ConfigLoader()

    tickers = config.strategy_config.get('universe', ['AAPL', 'MSFT', 'GOOGL', 'AMZN'])
    start_date = config.backtesting_config.get('start_date', '2020-01-01')
    end_date = config.backtesting_config.get('end_date', None)
    initial_capital = config.trading_config.get('initial_capital', 100000)
    benchmark = config.backtesting_config.get('benchmark', 'SPY')

    print(f"\nLoading data for {len(tickers)} tickers...")
    data_handler = DataHandler()
    data = data_handler.get_data(tickers, start_date, end_date)

    if data.empty:
        print("Error: No data loaded. Exiting.")
        return

    print(f"Data loaded: {len(data)} rows from {data.index[0]} to {data.index[-1]}")

    print("\n" + "-"*60)
    print("Running Momentum Strategy Backtest")
    print("-"*60)
    momentum_strategy = MomentumStrategy(lookback_period=20, top_n=3)
    backtest_engine = BacktestEngine(initial_capital=initial_capital)
    momentum_results = backtest_engine.run(momentum_strategy, data, start_date, end_date)
    backtest_engine.print_results(momentum_results)

    print("\n" + "-"*60)
    print("Running Mean Reversion Strategy Backtest")
    print("-"*60)
    mean_reversion_strategy = MeanReversionStrategy(lookback_period=20)
    backtest_engine2 = BacktestEngine(initial_capital=initial_capital)
    mr_results = backtest_engine2.run(mean_reversion_strategy, data, start_date, end_date)
    backtest_engine2.print_results(mr_results)

    print("\n" + "-"*60)
    print("Running Moving Average Crossover Strategy Backtest")
    print("-"*60)
    ma_strategy = MovingAverageCrossover(fast_period=10, slow_period=50)
    backtest_engine3 = BacktestEngine(initial_capital=initial_capital)
    ma_results = backtest_engine3.run(ma_strategy, data, start_date, end_date)
    backtest_engine3.print_results(ma_results)

    print("\n" + "-"*60)
    print("Portfolio Optimization")
    print("-"*60)
    stats = data_handler.calculate_statistics(data)
    optimizer = PortfolioOptimizer(stats['mean_returns'], stats['cov_matrix'])

    print("\nMax Sharpe Ratio Portfolio:")
    max_sharpe = optimizer.max_sharpe_ratio()
    print(f"Expected Return: {max_sharpe['return']*100:.2f}%")
    print(f"Volatility: {max_sharpe['volatility']*100:.2f}%")
    print(f"Sharpe Ratio: {max_sharpe['sharpe_ratio']:.2f}")
    print("\nWeights:")
    for ticker, weight in max_sharpe['weights'].items():
        if weight > 0.01:
            print(f"  {ticker}: {weight*100:.2f}%")

    print("\n" + "-"*60)
    print("Generating Performance Plots")
    print("-"*60)

    plotter = PerformancePlotter()

    benchmark_data = data_handler.get_market_data(benchmark, start_date, end_date)
    if not benchmark_data.empty:
        benchmark_returns = data_handler.get_returns(benchmark_data[benchmark])
        momentum_fig = plotter.plot_returns(
            momentum_results['returns_series'],
            benchmark_returns,
            title="Momentum Strategy vs Benchmark"
        )
        plotter.save_figure(momentum_fig, "momentum_performance.png")

    drawdown_fig = plotter.plot_drawdown(momentum_results['portfolio_series'])
    plotter.save_figure(drawdown_fig, "momentum_drawdown.png")

    print("\nPlots saved successfully!")
    print("\n" + "="*60)
    print("Backtest Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
