# VolatilityEdge

A self-contained options analytics and strategy-testing app inspired by the supplied blueprint and the core warnings in Colin Bennett's *Trading Volatility*: delta is not probability, implied volatility must be judged against realized volatility, short-vol trades carry equity risk, VIX products have roll drag, and skew trades depend on regime.

Open `index.html` in a browser to run the app. No server or package install is required.

## What is included

- Stock selection for SPY, AAPL, MSFT, NVDA, TSLA, AMZN, GOOGL, and META
- Black-Scholes-Merton option pricing with delta, probability ITM, first-order Greeks, and shadow Greeks
- Strategy builder with common structures: calls, puts, straddles, spreads, overwriting, underwriting, condors, and risk reversals
- Rolling options backtester across a selected stock basket
- Monte Carlo discrete-hedging P&L simulator
- P&L-at-expiry payoff map
- Volatility surface heatmap, IV/RV spread chart, VRP warnings, variance-vs-vol swap convexity display, and VIX roll simulator
- Education cards for the book-derived pitfalls

This first version uses deterministic synthetic market data so the tooling is testable offline. Live market data, FastAPI endpoints, and exchange-grade option chains can be added behind the same UI later.
