"""
🏦 プロ仕様 株式ポートフォリオ管理アプリ
Professional Stock Portfolio Manager
Built with Streamlit + yfinance + Plotly
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import json
import base64
import urllib.parse
import io
import time

# ============================================================
# 1. ページ設定 & 定数
# ============================================================
st.set_page_config(
    page_title="Stock Portfolio Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

RISK_FREE_RATE = 0.005  # 無リスク金利 (年率)
TRADING_DAYS = 252
BENCHMARK_JP = "^N225"  # 日経225
BENCHMARK_US = "^GSPC"  # S&P500


# ============================================================
# 1.5 主要銘柄リスト（ティッカーサジェスト用）
# ============================================================
TICKER_CATALOG = {
    # ── 米国株 ──
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet (Google)",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "NVDA": "NVIDIA",
    "META": "Meta Platforms",
    "NFLX": "Netflix",
    "AMD": "Advanced Micro Devices",
    "INTC": "Intel",
    "CRM": "Salesforce",
    "ORCL": "Oracle",
    "ADBE": "Adobe",
    "PYPL": "PayPal",
    "DIS": "Walt Disney",
    "V": "Visa",
    "MA": "Mastercard",
    "JPM": "JPMorgan Chase",
    "BAC": "Bank of America",
    "GS": "Goldman Sachs",
    "WMT": "Walmart",
    "KO": "Coca-Cola",
    "PEP": "PepsiCo",
    "JNJ": "Johnson & Johnson",
    "PFE": "Pfizer",
    "UNH": "UnitedHealth",
    "XOM": "Exxon Mobil",
    "CVX": "Chevron",
    "BA": "Boeing",
    "CAT": "Caterpillar",
    "SPY": "SPDR S&P 500 ETF",
    "VOO": "Vanguard S&P 500 ETF",
    "QQQ": "Invesco QQQ (NASDAQ)",
    "VTI": "Vanguard Total Stock",
    "ARKK": "ARK Innovation ETF",
    # ── 日本株 ──
    "7203.T": "トヨタ自動車",
    "9984.T": "ソフトバンクグループ",
    "6758.T": "ソニーグループ",
    "8306.T": "三菱UFJフィナンシャル",
    "9432.T": "日本電信電話 (NTT)",
    "6861.T": "キーエンス",
    "7974.T": "任天堂",
    "9433.T": "KDDI",
    "6501.T": "日立製作所",
    "8035.T": "東京エレクトロン",
    "4063.T": "信越化学工業",
    "6902.T": "デンソー",
    "7267.T": "本田技研工業",
    "8058.T": "三菱商事",
    "4502.T": "武田薬品工業",
    "6098.T": "リクルートHD",
    "9983.T": "ファーストリテイリング",
    "2914.T": "日本たばこ産業 (JT)",
    "3382.T": "セブン&アイHD",
    "4661.T": "オリエンタルランド",
}


# ============================================================
# 2. カスタムCSS
# ============================================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0E1117;
    --bg-secondary: #1A1F2E;
    --bg-card: #151B28;
    --accent-green: #00D4AA;
    --accent-red: #FF4B6E;
    --accent-blue: #3B82F6;
    --accent-purple: #8B5CF6;
    --accent-yellow: #F59E0B;
    --text-primary: #F0F2F6;
    --text-secondary: #8B95A5;
    --border-color: #2A3040;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', 'JetBrains Mono', sans-serif;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #1A1F2E 0%, #151B28 100%);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));
    border-radius: 16px 16px 0 0;
}
.kpi-card.loss::before {
    background: linear-gradient(90deg, var(--accent-red), var(--accent-purple));
}
.kpi-label {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
}
.kpi-delta {
    font-size: 14px;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}
.positive { color: var(--accent-green); }
.negative { color: var(--accent-red); }

/* Section Headers */
.section-header {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 24px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border-color);
}

/* Data table styling */
.holdings-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 14px;
}
.holdings-table th {
    background: var(--bg-secondary);
    color: var(--text-secondary);
    padding: 10px 14px;
    text-align: left;
    font-weight: 500;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border-color);
}
.holdings-table td {
    padding: 12px 14px;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
}
.holdings-table tr:hover td {
    background: rgba(59, 130, 246, 0.05);
}

/* Share Button */
.share-btn {
    background: linear-gradient(135deg, var(--accent-green), var(--accent-blue));
    color: white;
    padding: 10px 24px;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    display: inline-block;
    margin: 8px 0;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    color: var(--text-secondary);
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--accent-green) !important;
}

/* Sidebar refinements */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117 0%, #151B28 100%);
    border-right: 1px solid var(--border-color);
}

/* Metric overrides */
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }

/* ── News Card ── */
.news-card {
    background: linear-gradient(135deg, #1A1F2E 0%, #151B28 100%);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.news-card:hover {
    border-color: var(--accent-blue);
}
.news-card a {
    color: var(--accent-blue);
    text-decoration: none;
    font-weight: 600;
    font-size: 15px;
    line-height: 1.5;
}
.news-card a:hover {
    text-decoration: underline;
}
.news-meta {
    color: var(--text-secondary);
    font-size: 12px;
    margin-top: 6px;
}
.news-publisher {
    color: var(--accent-green);
    font-weight: 500;
}
</style>
"""

def inject_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# 3. データ取得関数群
# ============================================================

@st.cache_data(ttl=300)
def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """株価データを取得"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, auto_adjust=True)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_stock_info(ticker: str) -> dict:
    """銘柄情報を取得"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("shortName", info.get("longName", ticker)),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "currency": info.get("currency", "JPY" if ".T" in ticker else "USD"),
            "dividend_yield": info.get("dividendYield", 0) or 0,
            "market_cap": info.get("marketCap", 0),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
            "previous_close": info.get("previousClose", 0),
        }
    except Exception:
        return {
            "name": ticker, "sector": "N/A", "industry": "N/A",
            "currency": "JPY" if ".T" in ticker else "USD",
            "dividend_yield": 0, "market_cap": 0,
            "current_price": 0, "previous_close": 0,
        }


@st.cache_data(ttl=3600)
def get_exchange_rate() -> float:
    """USD/JPY為替レートを取得"""
    try:
        fx = yf.Ticker("USDJPY=X")
        data = fx.history(period="1d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception:
        pass
    return 150.0  # フォールバック値


@st.cache_data(ttl=300)
def fetch_benchmark(ticker: str, period: str = "1y") -> pd.DataFrame:
    """ベンチマークデータを取得"""
    return fetch_stock_data(ticker, period)


@st.cache_data(ttl=600)
def fetch_stock_news(ticker: str) -> list:
    """銘柄のニュースを取得（最大10件）"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if news:
            return news[:10]
    except Exception:
        pass
    return []


# ============================================================
# 4. ポートフォリオ計算関数群
# ============================================================

def calculate_holdings(portfolio: list, exchange_rate: float) -> pd.DataFrame:
    """保有銘柄の評価額・損益を計算"""
    if not portfolio:
        return pd.DataFrame()

    rows = []
    for item in portfolio:
        ticker = item["ticker"]
        shares = item["shares"]
        cost_price = item["cost_price"]
        buy_date = item.get("buy_date", "")

        info = fetch_stock_info(ticker)
        hist = fetch_stock_data(ticker, period="5d")

        current_price = info["current_price"]
        if current_price == 0 and not hist.empty:
            current_price = float(hist["Close"].iloc[-1])

        prev_close = info["previous_close"]
        if prev_close == 0 and len(hist) >= 2:
            prev_close = float(hist["Close"].iloc[-2])

        is_jpy = ".T" in ticker or ".JP" in ticker
        currency = "JPY" if is_jpy else "USD"

        # 評価額計算
        market_value = current_price * shares
        cost_total = cost_price * shares
        pnl = market_value - cost_total
        pnl_pct = (pnl / cost_total * 100) if cost_total != 0 else 0

        # 前日比
        daily_change = current_price - prev_close if prev_close > 0 else 0
        daily_change_pct = (daily_change / prev_close * 100) if prev_close > 0 else 0

        # JPY換算
        market_value_jpy = market_value if is_jpy else market_value * exchange_rate
        cost_total_jpy = cost_total if is_jpy else cost_total * exchange_rate
        pnl_jpy = market_value_jpy - cost_total_jpy

        rows.append({
            "ticker": ticker,
            "name": info["name"],
            "sector": info["sector"],
            "currency": currency,
            "shares": shares,
            "cost_price": cost_price,
            "current_price": current_price,
            "prev_close": prev_close,
            "daily_change": daily_change,
            "daily_change_pct": daily_change_pct,
            "market_value": market_value,
            "cost_total": cost_total,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "market_value_jpy": market_value_jpy,
            "cost_total_jpy": cost_total_jpy,
            "pnl_jpy": pnl_jpy,
            "dividend_yield": info["dividend_yield"],
            "buy_date": buy_date,
        })

    return pd.DataFrame(rows)


def calculate_portfolio_summary(holdings_df: pd.DataFrame) -> dict:
    """ポートフォリオサマリーを計算"""
    if holdings_df.empty:
        return {
            "total_value_jpy": 0, "total_cost_jpy": 0,
            "total_pnl_jpy": 0, "total_pnl_pct": 0,
            "daily_change_jpy": 0, "daily_change_pct": 0,
            "weighted_dividend_yield": 0, "annual_dividend_jpy": 0,
        }

    total_value = holdings_df["market_value_jpy"].sum()
    total_cost = holdings_df["cost_total_jpy"].sum()
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost != 0 else 0

    # 日次変動（加重平均）
    if total_value > 0:
        weights = holdings_df["market_value_jpy"] / total_value
        daily_pct = (holdings_df["daily_change_pct"] * weights).sum()
    else:
        daily_pct = 0
    daily_change_jpy = total_value * daily_pct / 100

    # 加重平均配当利回り
    if total_value > 0:
        weights = holdings_df["market_value_jpy"] / total_value
        weighted_div = (holdings_df["dividend_yield"] * weights).sum()
    else:
        weighted_div = 0
    annual_dividend = total_value * weighted_div

    return {
        "total_value_jpy": total_value,
        "total_cost_jpy": total_cost,
        "total_pnl_jpy": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "daily_change_jpy": daily_change_jpy,
        "daily_change_pct": daily_pct,
        "weighted_dividend_yield": weighted_div,
        "annual_dividend_jpy": annual_dividend,
    }


# ============================================================
# 5. 分析指標計算関数群
# ============================================================

def calculate_portfolio_returns(portfolio: list, period: str = "1y") -> pd.Series:
    """ポートフォリオの日次リターンを計算（加重平均）"""
    if not portfolio:
        return pd.Series(dtype=float)

    exchange_rate = get_exchange_rate()
    all_returns = {}
    weights = {}

    for item in portfolio:
        ticker = item["ticker"]
        hist = fetch_stock_data(ticker, period=period)
        if hist.empty or len(hist) < 2:
            continue

        returns = hist["Close"].pct_change().dropna()
        is_jpy = ".T" in ticker or ".JP" in ticker
        info = fetch_stock_info(ticker)
        current_price = info["current_price"]
        if current_price == 0 and not hist.empty:
            current_price = float(hist["Close"].iloc[-1])

        value = current_price * item["shares"]
        if not is_jpy:
            value *= exchange_rate

        all_returns[ticker] = returns
        weights[ticker] = value

    if not all_returns:
        return pd.Series(dtype=float)

    returns_df = pd.DataFrame(all_returns)
    returns_df = returns_df.dropna()

    total_value = sum(weights.values())
    if total_value == 0:
        return pd.Series(dtype=float)

    w = pd.Series({t: v / total_value for t, v in weights.items()})
    portfolio_returns = returns_df.mul(w).sum(axis=1)
    return portfolio_returns


def calculate_risk_metrics(returns: pd.Series) -> dict:
    """リスク指標を計算"""
    if returns.empty or len(returns) < 10:
        return {
            "sharpe_ratio": 0, "sortino_ratio": 0,
            "max_drawdown": 0, "volatility": 0,
            "var_95": 0, "var_99": 0, "beta": 0,
            "total_return": 0, "cagr": 0,
        }

    # 年率ボラティリティ
    vol = returns.std() * np.sqrt(TRADING_DAYS)

    # シャープレシオ
    excess_return = returns.mean() * TRADING_DAYS - RISK_FREE_RATE
    sharpe = excess_return / vol if vol != 0 else 0

    # ソルティノレシオ
    downside = returns[returns < 0]
    downside_std = downside.std() * np.sqrt(TRADING_DAYS) if len(downside) > 0 else 0
    sortino = excess_return / downside_std if downside_std != 0 else 0

    # 最大ドローダウン
    cum = (1 + returns).cumprod()
    peak = cum.cummax()
    drawdown = (cum - peak) / peak
    max_dd = drawdown.min()

    # VaR
    var_95 = np.percentile(returns, 5)
    var_99 = np.percentile(returns, 1)

    # トータルリターン
    total_ret = (1 + returns).prod() - 1

    # CAGR
    n_days = len(returns)
    if n_days > 0 and (1 + total_ret) > 0:
        cagr = (1 + total_ret) ** (TRADING_DAYS / n_days) - 1
    else:
        cagr = 0

    return {
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_dd,
        "volatility": vol,
        "var_95": var_95,
        "var_99": var_99,
        "total_return": total_ret,
        "cagr": cagr,
    }


def calculate_beta(portfolio_returns: pd.Series, benchmark_ticker: str, period: str = "1y") -> float:
    """ベータ値を計算"""
    bench_hist = fetch_benchmark(benchmark_ticker, period=period)
    if bench_hist.empty or portfolio_returns.empty:
        return 0

    bench_returns = bench_hist["Close"].pct_change().dropna()

    # 共通日付で揃える
    common = portfolio_returns.index.intersection(bench_returns.index)
    if len(common) < 10:
        return 0

    p = portfolio_returns.loc[common]
    b = bench_returns.loc[common]

    cov = np.cov(p, b)
    if cov[1, 1] != 0:
        return cov[0, 1] / cov[1, 1]
    return 0


def calculate_correlation_matrix(portfolio: list, period: str = "1y") -> pd.DataFrame:
    """銘柄間の相関マトリクスを計算"""
    all_prices = {}
    for item in portfolio:
        ticker = item["ticker"]
        hist = fetch_stock_data(ticker, period=period)
        if not hist.empty:
            all_prices[ticker] = hist["Close"]

    if len(all_prices) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(all_prices).dropna()
    returns = df.pct_change().dropna()
    return returns.corr()


# ============================================================
# 5.5 モンテカルロ・シミュレーション
# ============================================================

def run_monte_carlo(returns: pd.Series, initial_value: float,
                    years: int = 10, n_simulations: int = 200) -> np.ndarray:
    """モンテカルロ・シミュレーションを実行

    幾何ブラウン運動ベースで将来の資産推移をシミュレーション。
    Returns: shape (n_simulations, trading_days * years + 1) の配列
    """
    if returns.empty or initial_value <= 0:
        return np.array([])

    mu = returns.mean()
    sigma = returns.std()
    total_days = TRADING_DAYS * years

    # 日次リターンを正規分布から生成
    daily_returns = np.random.normal(mu, sigma, size=(n_simulations, total_days))

    # 資産パスを構築
    price_paths = np.zeros((n_simulations, total_days + 1))
    price_paths[:, 0] = initial_value

    for t in range(1, total_days + 1):
        price_paths[:, t] = price_paths[:, t - 1] * (1 + daily_returns[:, t - 1])

    return price_paths


def create_monte_carlo_chart(price_paths: np.ndarray, initial_value: float,
                             years: int = 10) -> go.Figure:
    """モンテカルロ結果をPlotlyチャートに描画"""
    if price_paths.size == 0:
        return go.Figure()

    n_sims, n_steps = price_paths.shape
    x_years = np.linspace(0, years, n_steps)

    fig = go.Figure()

    # 個別パス（薄く描画、最大100本）
    display_sims = min(n_sims, 100)
    for i in range(display_sims):
        fig.add_trace(go.Scatter(
            x=x_years, y=price_paths[i],
            mode="lines",
            line=dict(color="rgba(59,130,246,0.06)", width=1),
            hoverinfo="skip",
            showlegend=False,
        ))

    # パーセンタイルライン
    p10 = np.percentile(price_paths, 10, axis=0)
    p50 = np.percentile(price_paths, 50, axis=0)
    p90 = np.percentile(price_paths, 90, axis=0)

    fig.add_trace(go.Scatter(
        x=x_years, y=p90,
        mode="lines", name="上位10% (楽観)",
        line=dict(color="#00D4AA", width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=x_years, y=p50,
        mode="lines", name="中央値 (標準)",
        line=dict(color="#F59E0B", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=x_years, y=p10,
        mode="lines", name="下位10% (悲観)",
        line=dict(color="#FF4B6E", width=2.5),
    ))

    # 初期値ライン
    fig.add_hline(
        y=initial_value, line_dash="dot", line_color="#8B95A5",
        annotation_text=f"現在: {initial_value:,.0f}",
        annotation_font_color="#8B95A5",
    )

    fig.update_layout(**base_layout(
        xaxis_title="経過年数",
        yaxis_title="ポートフォリオ評価額 (¥)",
        hovermode="x unified",
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
    ))
    return fig


# ============================================================
# 6. チャート生成関数群
# ============================================================

def base_layout(**overrides):
    """ベースレイアウトにオーバーライドをマージして返すヘルパー"""
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F0F2F6", family="Noto Sans JP, sans-serif"),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#2A3040", zerolinecolor="#2A3040"),
        yaxis=dict(gridcolor="#2A3040", zerolinecolor="#2A3040"),
    )
    base.update(overrides)
    return base


def create_donut_chart(holdings_df: pd.DataFrame, by: str = "sector") -> go.Figure:
    """ドーナツチャート（セクター別/銘柄別）"""
    if holdings_df.empty:
        return go.Figure()

    if by == "sector":
        grouped = holdings_df.groupby("sector")["market_value_jpy"].sum().reset_index()
        labels = grouped["sector"]
        values = grouped["market_value_jpy"]
    else:
        labels = holdings_df["name"]
        values = holdings_df["market_value_jpy"]

    colors = ["#00D4AA", "#3B82F6", "#8B5CF6", "#F59E0B", "#FF4B6E",
              "#06B6D4", "#EC4899", "#84CC16", "#F97316", "#6366F1"]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker=dict(colors=colors[:len(labels)]),
        textinfo="label+percent",
        textfont=dict(size=12, color="#F0F2F6"),
        hovertemplate="<b>%{label}</b><br>¥%{value:,.0f}<br>%{percent}<extra></extra>",
    )])
    fig.update_layout(**base_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5,
                    font=dict(size=11, color="#8B95A5")),
        height=400,
    ))
    return fig


def create_performance_chart(portfolio: list, period: str = "1y",
                             benchmark_ticker: str = "^GSPC") -> go.Figure:
    """パフォーマンス推移チャート"""
    port_returns = calculate_portfolio_returns(portfolio, period=period)
    if port_returns.empty:
        return go.Figure()

    port_cum = (1 + port_returns).cumprod() - 1

    bench_hist = fetch_benchmark(benchmark_ticker, period=period)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=port_cum.index, y=port_cum.values * 100,
        mode="lines", name="ポートフォリオ",
        line=dict(color="#00D4AA", width=2.5),
        fill="tozeroy", fillcolor="rgba(0,212,170,0.08)",
    ))

    if not bench_hist.empty:
        bench_returns = bench_hist["Close"].pct_change().dropna()
        common = port_cum.index.intersection(bench_returns.index)
        if len(common) > 0:
            bench_cum = (1 + bench_returns.loc[common]).cumprod() - 1
            fig.add_trace(go.Scatter(
                x=bench_cum.index, y=bench_cum.values * 100,
                mode="lines", name="ベンチマーク",
                line=dict(color="#3B82F6", width=2, dash="dot"),
            ))

    fig.update_layout(**base_layout(
        yaxis_title="リターン (%)",
        hovermode="x unified",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    ))
    return fig


def create_candlestick_chart(ticker: str, period: str = "6mo") -> go.Figure:
    """ローソク足チャート"""
    hist = fetch_stock_data(ticker, period=period)
    if hist.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"],
        increasing_line_color="#00D4AA",
        decreasing_line_color="#FF4B6E",
        name="OHLC",
    ))

    # 出来高バー（サブプロット代わりにoverlay）
    colors = ["#00D4AA" if c >= o else "#FF4B6E"
              for c, o in zip(hist["Close"], hist["Open"])]

    fig.add_trace(go.Bar(
        x=hist.index, y=hist["Volume"],
        marker_color=colors, opacity=0.3,
        name="出来高", yaxis="y2",
    ))

    fig.update_layout(**base_layout(
        yaxis=dict(title="価格", gridcolor="#2A3040", side="left"),
        yaxis2=dict(title="出来高", overlaying="y", side="right",
                    showgrid=False, range=[0, hist["Volume"].max() * 4]),
        xaxis=dict(gridcolor="#2A3040", zerolinecolor="#2A3040"),
        xaxis_rangeslider_visible=False,
        height=450,
        showlegend=False,
    ))
    return fig


def create_treemap(holdings_df: pd.DataFrame) -> go.Figure:
    """損益ツリーマップ"""
    if holdings_df.empty:
        return go.Figure()

    df = holdings_df.copy()
    df["abs_value"] = df["market_value_jpy"].abs()
    df["color_val"] = df["pnl_pct"]
    df["label"] = df.apply(
        lambda r: f"{r['name']}<br>{r['pnl_pct']:+.1f}%", axis=1
    )

    fig = go.Figure(go.Treemap(
        labels=df["label"],
        parents=[""] * len(df),
        values=df["abs_value"],
        marker=dict(
            colors=df["color_val"],
            colorscale=[[0, "#FF4B6E"], [0.5, "#2A3040"], [1, "#00D4AA"]],
            cmid=0,
            line=dict(width=2, color="#0E1117"),
        ),
        textfont=dict(size=14, color="#F0F2F6"),
        hovertemplate="<b>%{label}</b><br>評価額: ¥%{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        height=400,
    ))
    return fig


def create_correlation_heatmap(portfolio: list, period: str = "1y") -> go.Figure:
    """相関マトリクスヒートマップ"""
    corr = calculate_correlation_matrix(portfolio, period)
    if corr.empty:
        return go.Figure()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale=[[0, "#FF4B6E"], [0.5, "#1A1F2E"], [1, "#00D4AA"]],
        zmid=0, zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=12, color="#F0F2F6"),
        hovertemplate="<b>%{x} × %{y}</b><br>相関: %{z:.3f}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        yaxis=dict(gridcolor="#2A3040", zerolinecolor="#2A3040"),
        height=400,
        xaxis=dict(side="bottom", gridcolor="#2A3040", zerolinecolor="#2A3040"),
    ))
    return fig


def create_return_histogram(returns: pd.Series) -> go.Figure:
    """リターン分布ヒストグラム"""
    if returns.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=returns.values * 100,
        nbinsx=50,
        marker_color="#3B82F6",
        opacity=0.7,
        name="日次リターン",
    ))

    mean_ret = returns.mean() * 100
    fig.add_vline(x=mean_ret, line_dash="dash", line_color="#00D4AA",
                  annotation_text=f"平均: {mean_ret:.3f}%")
    fig.add_vline(x=0, line_dash="solid", line_color="#8B95A5", line_width=1)

    fig.update_layout(**base_layout(
        xaxis_title="日次リターン (%)",
        yaxis_title="頻度",
        height=350,
        showlegend=False,
    ))
    return fig


# ============================================================
# 7. URL共有機能（エンコード/デコード）
# ============================================================

def encode_portfolio(portfolio: list) -> str:
    """ポートフォリオをBase64エンコード"""
    data = json.dumps(portfolio, ensure_ascii=False)
    encoded = base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8")
    return encoded


def decode_portfolio(encoded: str) -> list:
    """Base64からポートフォリオを復元"""
    try:
        data = base64.urlsafe_b64decode(encoded.encode("utf-8")).decode("utf-8")
        portfolio = json.loads(data)
        return portfolio
    except Exception:
        return []


def restore_from_url():
    """URLパラメータからポートフォリオを復元"""
    params = st.query_params
    if "p" in params:
        encoded = params["p"]
        portfolio = decode_portfolio(encoded)
        if portfolio:
            st.session_state["portfolio"] = portfolio
            st.session_state["restored"] = True


def generate_share_url(portfolio: list) -> str:
    """共有URLを生成"""
    encoded = encode_portfolio(portfolio)
    base_url = "https://stock-portfolio-pro-3rv7hhykj6dcwxzqpopvl8.streamlit.app/"
    return f"{base_url}?p={encoded}"


# ============================================================
# 8. CSV インポート/エクスポート
# ============================================================

def export_csv(portfolio: list) -> str:
    """ポートフォリオをCSV文字列に変換"""
    if not portfolio:
        return ""
    df = pd.DataFrame(portfolio)
    return df.to_csv(index=False)


def import_csv(csv_text: str) -> list:
    """CSVからポートフォリオを読み込み"""
    try:
        df = pd.read_csv(io.StringIO(csv_text))
        required = {"ticker", "shares", "cost_price"}
        if not required.issubset(set(df.columns)):
            return []
        portfolio = []
        for _, row in df.iterrows():
            portfolio.append({
                "ticker": str(row["ticker"]).strip().upper(),
                "shares": float(row["shares"]),
                "cost_price": float(row["cost_price"]),
                "buy_date": str(row.get("buy_date", "")),
            })
        return portfolio
    except Exception:
        return []


# ============================================================
# 9. KPIカード HTML & ニュースカード HTML
# ============================================================

def kpi_card(label: str, value: str, delta: str = "", is_loss: bool = False) -> str:
    """KPIカードのHTML生成"""
    loss_class = "loss" if is_loss else ""
    delta_class = "negative" if is_loss else "positive"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card {loss_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def news_card_html(title: str, link: str, publisher: str,
                   published: str, thumbnail: str = "") -> str:
    """ニュースカードのHTML生成"""
    thumb_html = ""
    if thumbnail:
        thumb_html = (
            f'<img src="{thumbnail}" '
            f'style="width:80px;height:56px;object-fit:cover;border-radius:8px;'
            f'margin-right:14px;flex-shrink:0;" />'
        )
    return f"""
    <div class="news-card" style="display:flex;align-items:flex-start;">
        {thumb_html}
        <div style="flex:1;min-width:0;">
            <a href="{link}" target="_blank" rel="noopener">{title}</a>
            <div class="news-meta">
                <span class="news-publisher">{publisher}</span>
                &nbsp;·&nbsp; {published}
            </div>
        </div>
    </div>
    """


def format_jpy(val: float) -> str:
    """日本円フォーマット"""
    if abs(val) >= 1e8:
        return f"¥{val/1e8:.2f}億"
    elif abs(val) >= 1e4:
        return f"¥{val/1e4:.1f}万"
    else:
        return f"¥{val:,.0f}"


# ============================================================
# 10. サイドバーUI（ティッカーサジェスト機能付き）
# ============================================================

def render_sidebar():
    """サイドバーの入力フォームを表示"""
    with st.sidebar:
        st.markdown("## 📈 ポートフォリオ管理")

        # 初期化
        if "portfolio" not in st.session_state:
            st.session_state["portfolio"] = []

        # URL復元
        if "restored" not in st.session_state:
            restore_from_url()

        st.markdown("---")
        st.markdown("### ➕ 銘柄を追加")

        # ── サジェストリスト（フォーム外で選択 → session_state に保持） ──
        catalog_options = ["（リストから選択）"] + [
            f"{t}  —  {n}" for t, n in TICKER_CATALOG.items()
        ]
        selected_from_list = st.selectbox(
            "📋 主要銘柄から選択",
            options=catalog_options,
            index=0,
            help="検索窓に銘柄名やティッカーを入力して絞り込めます",
            key="ticker_suggest",
        )

        with st.form("add_stock", clear_on_submit=True):
            # 自由入力欄（リストにない銘柄用 / 直接入力したい場合）
            manual_ticker = st.text_input(
                "ティッカー（手動入力）",
                placeholder="例: AAPL, 7203.T（上のリストにない場合）",
                help="上のリストで選択済みならここは空欄でOKです。日本株は .T を付けてください。",
            )

            col1, col2 = st.columns(2)
            with col1:
                shares = st.number_input("株数", min_value=0.0, value=0.0, step=1.0)
            with col2:
                cost_price = st.number_input("取得単価", min_value=0.0, value=0.0, step=0.01)
            buy_date = st.date_input("取得日", value=datetime.now())
            submitted = st.form_submit_button("✅ 追加", use_container_width=True)

            if submitted:
                # 手動入力を優先、なければリスト選択を使用
                if manual_ticker.strip():
                    ticker = manual_ticker.strip().upper()
                elif selected_from_list and selected_from_list != "（リストから選択）":
                    ticker = selected_from_list.split("  —  ")[0].strip()
                else:
                    ticker = ""

                if ticker and shares > 0 and cost_price > 0:
                    st.session_state["portfolio"].append({
                        "ticker": ticker,
                        "shares": shares,
                        "cost_price": cost_price,
                        "buy_date": str(buy_date),
                    })
                    st.rerun()

        # 保有銘柄一覧
        if st.session_state["portfolio"]:
            st.markdown("---")
            st.markdown("### 📋 保有銘柄")
            for i, item in enumerate(st.session_state["portfolio"]):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{item['ticker']}** × {item['shares']:.0f}株")
                    st.caption(f"取得単価: {item['cost_price']:,.2f}")
                with col2:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state["portfolio"].pop(i)
                        st.rerun()

            # 共有リンク生成
            st.markdown("---")
            st.markdown("### 🔗 共有")
            if st.button("📋 共有リンクを生成", use_container_width=True):
                share_url = generate_share_url(st.session_state["portfolio"])
                st.code(share_url, language=None)
                st.info("👆 このURLを友人に送ると同じポートフォリオが復元されます")

            # CSVエクスポート
            csv_data = export_csv(st.session_state["portfolio"])
            st.download_button(
                "📥 CSVエクスポート",
                data=csv_data,
                file_name="portfolio.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # CSVインポート
        st.markdown("---")
        st.markdown("### 📤 CSVインポート")
        uploaded = st.file_uploader("CSVファイルを選択", type=["csv"])
        if uploaded:
            csv_text = uploaded.read().decode("utf-8")
            imported = import_csv(csv_text)
            if imported:
                if st.button("インポートを確定"):
                    st.session_state["portfolio"] = imported
                    st.rerun()
                st.success(f"{len(imported)}銘柄を読み込みました")
            else:
                st.error("CSV形式が不正です（ticker, shares, cost_price が必要です）")

        # リセット
        st.markdown("---")
        if st.button("🔄 ポートフォリオをリセット", use_container_width=True):
            st.session_state["portfolio"] = []
            st.rerun()


# ============================================================
# 11. メインページUI
# ============================================================

def render_main():
    """メインダッシュボードを表示"""
    st.markdown("# 📊 Stock Portfolio Pro")
    st.markdown(
        '<p style="color:#8B95A5; margin-top:-12px;">リアルタイム株式ポートフォリオ管理</p>',
        unsafe_allow_html=True,
    )

    portfolio = st.session_state.get("portfolio", [])

    if not portfolio:
        st.markdown("---")
        st.info("👈 サイドバーから銘柄を追加してください。"
                "または共有URLから復元するか、CSVをインポートしてください。")

        # デモデータ
        if st.button("🎮 デモデータで体験する"):
            st.session_state["portfolio"] = [
                {"ticker": "AAPL", "shares": 10, "cost_price": 150.0, "buy_date": "2024-01-15"},
                {"ticker": "GOOGL", "shares": 5, "cost_price": 140.0, "buy_date": "2024-02-01"},
                {"ticker": "MSFT", "shares": 8, "cost_price": 380.0, "buy_date": "2024-03-10"},
                {"ticker": "7203.T", "shares": 100, "cost_price": 2500.0, "buy_date": "2024-01-20"},
                {"ticker": "6758.T", "shares": 50, "cost_price": 12000.0, "buy_date": "2024-04-05"},
            ]
            st.rerun()
        return

    # データ取得
    with st.spinner("📡 最新データを取得中..."):
        exchange_rate = get_exchange_rate()
        holdings_df = calculate_holdings(portfolio, exchange_rate)
        summary = calculate_portfolio_summary(holdings_df)

    # ─── KPIカード ───
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(kpi_card(
            "総資産評価額",
            format_jpy(summary["total_value_jpy"]),
        ), unsafe_allow_html=True)

    with c2:
        pnl = summary["total_pnl_jpy"]
        pnl_pct = summary["total_pnl_pct"]
        is_loss = pnl < 0
        st.markdown(kpi_card(
            "総損益",
            format_jpy(pnl),
            f"{'▲' if pnl >= 0 else '▼'} {pnl_pct:+.2f}%",
            is_loss=is_loss,
        ), unsafe_allow_html=True)

    with c3:
        dc = summary["daily_change_jpy"]
        dp = summary["daily_change_pct"]
        st.markdown(kpi_card(
            "日次変動",
            format_jpy(dc),
            f"{'▲' if dc >= 0 else '▼'} {dp:+.2f}%",
            is_loss=dc < 0,
        ), unsafe_allow_html=True)

    with c4:
        port_returns = calculate_portfolio_returns(portfolio, "1y")
        metrics = calculate_risk_metrics(port_returns)
        sharpe = metrics["sharpe_ratio"]
        st.markdown(kpi_card(
            "シャープレシオ",
            f"{sharpe:.2f}",
        ), unsafe_allow_html=True)

    # ─── タブ（5つに拡張） ───
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 概要", "📈 チャート", "🔬 分析", "🏢 個別銘柄", "🔮 シミュレーション"]
    )

    # ── タブ1: 概要 ──
    with tab1:
        st.markdown('<div class="section-header">保有銘柄一覧</div>', unsafe_allow_html=True)

        if not holdings_df.empty:
            display_df = holdings_df[[
                "ticker", "name", "sector", "shares", "current_price",
                "daily_change_pct", "market_value_jpy", "pnl_jpy", "pnl_pct",
                "dividend_yield"
            ]].copy()

            display_df.columns = [
                "ティッカー", "銘柄名", "セクター", "株数", "現在値",
                "前日比(%)", "評価額(¥)", "損益(¥)", "損益(%)", "配当利回り"
            ]

            # フォーマット
            display_df["現在値"] = display_df["現在値"].apply(lambda x: f"{x:,.2f}")
            display_df["前日比(%)"] = display_df["前日比(%)"].apply(
                lambda x: f"{'🟢' if x >= 0 else '🔴'} {x:+.2f}%"
            )
            display_df["評価額(¥)"] = display_df["評価額(¥)"].apply(lambda x: f"¥{x:,.0f}")
            display_df["損益(¥)"] = display_df["損益(¥)"].apply(
                lambda x: f"{'🟢' if x >= 0 else '🔴'} ¥{x:,.0f}"
            )
            display_df["損益(%)"] = display_df["損益(%)"].apply(
                lambda x: f"{x:+.2f}%"
            )
            display_df["配当利回り"] = display_df["配当利回り"].apply(
                lambda x: f"{x*100:.2f}%"
            )

            st.dataframe(display_df, use_container_width=True, hide_index=True)

        # 配当情報サマリー
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("加重平均配当利回り",
                       f"{summary['weighted_dividend_yield']*100:.2f}%")
        with col2:
            st.metric("年間予想配当収入",
                       format_jpy(summary["annual_dividend_jpy"]))
        with col3:
            st.metric("為替レート (USD/JPY)", f"¥{exchange_rate:,.2f}")

    # ── タブ2: チャート ──
    with tab2:
        # 資産配分
        st.markdown('<div class="section-header">資産配分</div>', unsafe_allow_html=True)
        alloc_by = st.radio("表示切替", ["セクター別", "銘柄別"],
                            horizontal=True, label_visibility="collapsed")
        by = "sector" if alloc_by == "セクター別" else "ticker"
        st.plotly_chart(create_donut_chart(holdings_df, by=by),
                        use_container_width=True)

        # パフォーマンス推移
        st.markdown('<div class="section-header">パフォーマンス推移</div>',
                    unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            period_map = {"1W": "5d", "1M": "1mo", "3M": "3mo",
                          "6M": "6mo", "1Y": "1y", "ALL": "max"}
            selected_period = st.selectbox("期間", list(period_map.keys()), index=4)
        with col2:
            # ベンチマーク自動判定
            has_jp = any(".T" in item["ticker"] or ".JP" in item["ticker"]
                         for item in portfolio)
            bench_options = {"S&P 500": "^GSPC", "日経225": "^N225", "TOPIX": "^TPX"}
            default_bench = "日経225" if has_jp else "S&P 500"
            bench_name = st.selectbox("ベンチマーク", list(bench_options.keys()),
                                       index=list(bench_options.keys()).index(default_bench))

        st.plotly_chart(
            create_performance_chart(
                portfolio,
                period=period_map[selected_period],
                benchmark_ticker=bench_options[bench_name],
            ),
            use_container_width=True,
        )

        # 損益ヒートマップ
        st.markdown('<div class="section-header">損益ヒートマップ</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(create_treemap(holdings_df), use_container_width=True)

        # 相関マトリクス
        if len(portfolio) >= 2:
            st.markdown('<div class="section-header">相関マトリクス</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(create_correlation_heatmap(portfolio),
                            use_container_width=True)

    # ── タブ3: 分析 ──
    with tab3:
        st.markdown('<div class="section-header">リスク・リターン分析</div>',
                    unsafe_allow_html=True)

        if not port_returns.empty:
            # ベータ計算
            has_jp = any(".T" in item["ticker"] for item in portfolio)
            beta_bench = "^N225" if has_jp else "^GSPC"
            beta = calculate_beta(port_returns, beta_bench)

            # リスク指標
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### 📊 リスク指標")
                st.metric("シャープレシオ", f"{metrics['sharpe_ratio']:.3f}")
                st.metric("ソルティノレシオ", f"{metrics['sortino_ratio']:.3f}")
                st.metric("年率ボラティリティ", f"{metrics['volatility']*100:.2f}%")

            with col2:
                st.markdown("#### 📉 ドローダウン・VaR")
                st.metric("最大ドローダウン", f"{metrics['max_drawdown']*100:.2f}%")
                st.metric("VaR (95%)", f"{metrics['var_95']*100:.3f}%")
                st.metric("VaR (99%)", f"{metrics['var_99']*100:.3f}%")

            with col3:
                st.markdown("#### 📈 リターン指標")
                st.metric("トータルリターン", f"{metrics['total_return']*100:.2f}%")
                st.metric("CAGR (年率)", f"{metrics['cagr']*100:.2f}%")
                st.metric(f"β値 ({'日経225' if has_jp else 'S&P500'})", f"{beta:.3f}")

            # リターン分布
            st.markdown('<div class="section-header">日次リターン分布</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(create_return_histogram(port_returns),
                            use_container_width=True)

            # 統計サマリー
            st.markdown('<div class="section-header">統計サマリー</div>',
                        unsafe_allow_html=True)
            desc = port_returns.describe()
            stat_df = pd.DataFrame({
                "指標": ["データ数", "平均 (日次)", "標準偏差 (日次)", "最小値", "25%",
                         "中央値", "75%", "最大値", "歪度", "尖度"],
                "値": [
                    f"{int(desc['count'])}日",
                    f"{desc['mean']*100:.4f}%",
                    f"{desc['std']*100:.4f}%",
                    f"{desc['min']*100:.4f}%",
                    f"{desc['25%']*100:.4f}%",
                    f"{desc['50%']*100:.4f}%",
                    f"{desc['75%']*100:.4f}%",
                    f"{desc['max']*100:.4f}%",
                    f"{port_returns.skew():.4f}",
                    f"{port_returns.kurtosis():.4f}",
                ]
            })
            st.dataframe(stat_df, use_container_width=True, hide_index=True)
        else:
            st.info("分析に十分なデータがありません。")

    # ── タブ4: 個別銘柄（ニュースフィード付き） ──
    with tab4:
        st.markdown('<div class="section-header">個別銘柄チャート</div>',
                    unsafe_allow_html=True)

        tickers = [item["ticker"] for item in portfolio]
        selected_ticker = st.selectbox("銘柄を選択", tickers)

        if selected_ticker:
            info = fetch_stock_info(selected_ticker)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("銘柄名", info["name"])
            with col2:
                st.metric("セクター", info["sector"])
            with col3:
                st.metric("現在値", f"{info['current_price']:,.2f}")
            with col4:
                if info["previous_close"] > 0:
                    chg = (info["current_price"] - info["previous_close"]) / info["previous_close"] * 100
                    st.metric("前日比", f"{chg:+.2f}%")

            chart_period = st.selectbox(
                "チャート期間",
                ["1mo", "3mo", "6mo", "1y", "2y", "max"],
                index=2,
                key="candle_period",
            )
            st.plotly_chart(
                create_candlestick_chart(selected_ticker, period=chart_period),
                use_container_width=True,
            )

            # ── ニュースフィード ──
            st.markdown('<div class="section-header">📰 関連ニュース</div>',
                        unsafe_allow_html=True)

            with st.spinner("ニュースを取得中..."):
                news_items = fetch_stock_news(selected_ticker)

            if news_items:
                for article in news_items:
                    # yfinance news の構造に対応
                    title = article.get("title", "")
                    link = article.get("link", "")
                    publisher = article.get("publisher", "")
                    thumbnail = ""

                    # サムネイル取得（yfinance の構造はバージョンで変わりうる）
                    thumb_data = article.get("thumbnail", {})
                    if isinstance(thumb_data, dict):
                        resolutions = thumb_data.get("resolutions", [])
                        if resolutions:
                            thumbnail = resolutions[0].get("url", "")

                    # 発行日時のフォーマット
                    pub_ts = article.get("providerPublishTime", 0)
                    if pub_ts:
                        try:
                            pub_dt = datetime.fromtimestamp(pub_ts)
                            published = pub_dt.strftime("%Y/%m/%d %H:%M")
                        except Exception:
                            published = ""
                    else:
                        published = ""

                    if title and link:
                        st.markdown(
                            news_card_html(title, link, publisher, published, thumbnail),
                            unsafe_allow_html=True,
                        )
            else:
                st.caption("ニュースが見つかりませんでした。")

    # ── タブ5: モンテカルロ・シミュレーション ──
    with tab5:
        st.markdown(
            '<div class="section-header">🔮 モンテカルロ・シミュレーション</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "過去のリターン分布に基づいて、今後の資産推移を確率的にシミュレーションします。"
            "将来の正確な予測ではなく、リスクの可視化を目的としたツールです。"
        )

        if port_returns.empty or len(port_returns) < 20:
            st.info("シミュレーションにはより多くの過去データが必要です。")
        else:
            # パラメータ設定
            col1, col2 = st.columns(2)
            with col1:
                sim_years = st.slider(
                    "予測期間（年）", min_value=1, max_value=20,
                    value=10, step=1,
                )
            with col2:
                n_sims = st.select_slider(
                    "シナリオ数",
                    options=[100, 200, 500, 1000],
                    value=200,
                )

            initial_value = summary["total_value_jpy"]

            if st.button("▶ シミュレーション実行", use_container_width=True,
                         type="primary"):
                with st.spinner("シミュレーション実行中..."):
                    paths = run_monte_carlo(
                        port_returns, initial_value,
                        years=sim_years, n_simulations=n_sims,
                    )

                if paths.size > 0:
                    # チャート描画
                    st.plotly_chart(
                        create_monte_carlo_chart(paths, initial_value, years=sim_years),
                        use_container_width=True,
                    )

                    # 最終日の分布から指標を算出
                    final_values = paths[:, -1]
                    p10 = np.percentile(final_values, 10)
                    p50 = np.percentile(final_values, 50)
                    p90 = np.percentile(final_values, 90)

                    # KPIカードで結果表示
                    st.markdown(
                        '<div class="section-header">シミュレーション結果サマリー</div>',
                        unsafe_allow_html=True,
                    )

                    rc1, rc2, rc3 = st.columns(3)

                    with rc1:
                        growth = (p10 / initial_value - 1) * 100
                        st.markdown(kpi_card(
                            "悲観シナリオ (下位10%)",
                            format_jpy(p10),
                            f"{'▲' if growth >= 0 else '▼'} {growth:+.1f}%",
                            is_loss=growth < 0,
                        ), unsafe_allow_html=True)

                    with rc2:
                        growth = (p50 / initial_value - 1) * 100
                        st.markdown(kpi_card(
                            "標準シナリオ (中央値)",
                            format_jpy(p50),
                            f"{'▲' if growth >= 0 else '▼'} {growth:+.1f}%",
                            is_loss=growth < 0,
                        ), unsafe_allow_html=True)

                    with rc3:
                        growth = (p90 / initial_value - 1) * 100
                        st.markdown(kpi_card(
                            "楽観シナリオ (上位10%)",
                            format_jpy(p90),
                            f"▲ {growth:+.1f}%",
                            is_loss=False,
                        ), unsafe_allow_html=True)

                    # 確率分析
                    prob_profit = (final_values > initial_value).mean() * 100
                    prob_double = (final_values > initial_value * 2).mean() * 100
                    prob_halve = (final_values < initial_value * 0.5).mean() * 100

                    st.markdown(
                        '<div class="section-header">確率分析</div>',
                        unsafe_allow_html=True,
                    )
                    pc1, pc2, pc3 = st.columns(3)
                    with pc1:
                        st.metric("元本プラスの確率", f"{prob_profit:.1f}%")
                    with pc2:
                        st.metric("資産2倍の確率", f"{prob_double:.1f}%")
                    with pc3:
                        st.metric("資産半減の確率", f"{prob_halve:.1f}%")

                else:
                    st.error("シミュレーションの実行に失敗しました。")


# ============================================================
# 12. main
# ============================================================

def main():
    inject_css()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
