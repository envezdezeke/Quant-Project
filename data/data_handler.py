import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os


class DataHandler:
    def __init__(self, cache_dir: str = "data/raw"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_data(self, tickers: List[str],
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 use_cache: bool = True) -> pd.DataFrame:
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        cache_file = os.path.join(
            self.cache_dir,
            f"{'_'.join(tickers)}_{start_date}_{end_date}.pkl"
        )

        if use_cache and os.path.exists(cache_file):
            print(f"Loading data from cache: {cache_file}")
            return pd.read_pickle(cache_file)

        print(f"Downloading data for {len(tickers)} tickers from {start_date} to {end_date}")

        try:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)

            if isinstance(data.columns, pd.MultiIndex):
                data = data['Adj Close']
            else:
                data = data[['Adj Close']]
                data.columns = tickers

            data = data.dropna(how='all')

            if use_cache:
                data.to_pickle(cache_file)
                print(f"Data cached to: {cache_file}")

            return data

        except Exception as e:
            print(f"Error downloading data: {e}")
            return pd.DataFrame()

    def get_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.pct_change().dropna()

    def get_log_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        return np.log(data / data.shift(1)).dropna()

    def calculate_statistics(self, data: pd.DataFrame) -> Dict:
        returns = self.get_returns(data)
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        volatility = returns.std() * np.sqrt(252)

        stats = {
            'mean_returns': mean_returns,
            'cov_matrix': cov_matrix,
            'volatility': volatility,
            'correlation': returns.corr()
        }

        return stats

    def resample_data(self, data: pd.DataFrame, frequency: str = 'W') -> pd.DataFrame:
        return data.resample(frequency).last()

    def add_technical_indicators(self, data: pd.DataFrame,
                                 indicators: List[str] = None) -> pd.DataFrame:
        result = data.copy()

        if indicators is None:
            indicators = ['SMA_20', 'SMA_50', 'RSI', 'MACD']

        for column in data.columns:
            series = data[column]

            if 'SMA_20' in indicators:
                result[f'{column}_SMA_20'] = series.rolling(window=20).mean()

            if 'SMA_50' in indicators:
                result[f'{column}_SMA_50'] = series.rolling(window=50).mean()

            if 'RSI' in indicators:
                result[f'{column}_RSI'] = self._calculate_rsi(series)

            if 'MACD' in indicators:
                macd, signal = self._calculate_macd(series)
                result[f'{column}_MACD'] = macd
                result[f'{column}_MACD_Signal'] = signal

        return result

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, series: pd.Series,
                       fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = series.ewm(span=fast).mean()
        ema_slow = series.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd, signal_line

    def clean_data(self, data: pd.DataFrame,
                   fill_method: str = 'ffill') -> pd.DataFrame:
        cleaned = data.copy()

        if fill_method == 'ffill':
            cleaned = cleaned.fillna(method='ffill').fillna(method='bfill')
        elif fill_method == 'interpolate':
            cleaned = cleaned.interpolate(method='linear')
        elif fill_method == 'drop':
            cleaned = cleaned.dropna()

        return cleaned

    def get_market_data(self, benchmark: str = 'SPY',
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        return self.get_data([benchmark], start_date, end_date)
