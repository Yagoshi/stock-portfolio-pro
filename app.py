"""
株式ポートフォリオ管理アプリケーション (Stock Portfolio Management Application)

プロの投資家向けの包括的なポートフォリオ分析ツール
- リアルタイム株価データ取得
- モンテカルロシミュレーション
- リバランス提案
- 配当追跡・カレンダー
- 効率的フロンティア分析
- ニュースフィード
- URL共有機能
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from urllib.parse import urlencode, parse_qs
import warnings
from scipy.optimize import minimize

warnings.filterwarnings('ignore')


# ================================================================================
# ページ設定
# ================================================================================

st.set_page_config(
    page_title="株式ポートフォリオ管理",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ================================================================================
# カスタムCSS
# ================================================================================

st.markdown("""
<style>
    /* メインコンテナ */
    .main > div {
        padding-top: 2rem;
    }
    
    /* サイドバースタイリング */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: #1f2937;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #374151;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    
    /* サイドバーのexpander */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        font-weight: 600;
        color: #1f2937;
        padding: 0.75rem 1rem;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: #f3f4f6;
        border-color: #667eea;
    }
    
    /* サイドバーの入力フィールド */
    [data-testid="stSidebar"] input {
        border-radius: 6px;
        border: 1px solid #d1d5db;
    }
    
    [data-testid="stSidebar"] input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* サイドバーのボタン */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* サイドバーのスライダー */
    [data-testid="stSidebar"] .stSlider {
        padding: 0.5rem 0;
    }
    
    /* サイドバーの情報ボックス */
    [data-testid="stSidebar"] .element-container div[data-testid="stMarkdownContainer"] p {
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* サイドバーの区切り線 */
    [data-testid="stSidebar"] hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 2px solid #e5e7eb;
    }
    
    /* KPIカード */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        font-weight: 500;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .kpi-change {
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    /* セクションヘッダー */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* テーブルスタイル */
    .dataframe {
        font-size: 0.9rem;
    }
    
    .dataframe th {
        background-color: #667eea !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* メトリクスカスタマイズ */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem;
    }
    
    /* ボタンスタイル（メインエリア） */
    .stButton > button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #5568d3;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* タブスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f3f4f6;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
    /* アラートボックス */
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-info {
        background-color: #eff6ff;
        border-color: #3b82f6;
        color: #1e40af;
    }
    
    .alert-success {
        background-color: #f0fdf4;
        border-color: #22c55e;
        color: #166534;
    }
    
    .alert-warning {
        background-color: #fffbeb;
        border-color: #f59e0b;
        color: #92400e;
    }
    
    /* サイドバーの保有銘柄カード */
    .holding-card {
        background: white;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .holding-card:hover {
        border-color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
    }
</style>
""", unsafe_allow_html=True)


# ================================================================================
# セッション状態の初期化
# ================================================================================

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

if 'target_allocation' not in st.session_state:
    st.session_state.target_allocation = {}


# ================================================================================
# ユーティリティ関数
# ================================================================================

def format_currency(value):
    """
    金額を日本円形式でフォーマット
    
    Args:
        value (float): フォーマットする金額
        
    Returns:
        str: フォーマットされた金額文字列
    """
    if pd.isna(value):
        return "¥0"
    return f"¥{value:,.0f}"


def format_percentage(value):
    """
    パーセンテージをフォーマット
    
    Args:
        value (float): フォーマットするパーセンテージ（小数形式）
        
    Returns:
        str: フォーマットされたパーセンテージ文字列
    """
    if pd.isna(value):
        return "0.00%"
    return f"{value:.2f}%"


def get_ticker_info(ticker_symbol):
    """
    Tickerシンボルから株価情報を取得
    
    Args:
        ticker_symbol (str): 株式のティッカーシンボル
        
    Returns:
        dict: 株価情報を含む辞書、エラー時はNone
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        if hist.empty:
            return None
            
        current_price = hist['Close'].iloc[-1]
        
        return {
            'symbol': ticker_symbol,
            'name': info.get('longName', ticker_symbol),
            'current_price': current_price,
            'currency': info.get('currency', 'USD'),
            'previous_close': info.get('previousClose', current_price),
        }
    except Exception as e:
        st.error(f"エラー: {ticker_symbol} の情報取得に失敗しました - {str(e)}")
        return None


def get_historical_data(ticker_symbol, period="1y"):
    """
    過去の株価データを取得
    
    Args:
        ticker_symbol (str): 株式のティッカーシンボル
        period (str): 取得期間（デフォルト: 1年）
        
    Returns:
        pd.DataFrame: 過去の株価データ
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        return hist
    except Exception as e:
        st.error(f"エラー: {ticker_symbol} の履歴データ取得に失敗しました - {str(e)}")
        return pd.DataFrame()


def calculate_portfolio_metrics(portfolio_df):
    """
    ポートフォリオの総合指標を計算
    
    Args:
        portfolio_df (pd.DataFrame): ポートフォリオデータ
        
    Returns:
        dict: 計算された指標
    """
    if portfolio_df.empty:
        return {
            'total_value': 0,
            'total_cost': 0,
            'total_gain_loss': 0,
            'total_gain_loss_pct': 0,
            'best_performer': None,
            'worst_performer': None
        }
    
    total_value = portfolio_df['現在価値'].sum()
    total_cost = portfolio_df['取得価額'].sum()
    total_gain_loss = portfolio_df['損益'].sum()
    total_gain_loss_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    best_performer = portfolio_df.loc[portfolio_df['損益率(%)'].idxmax()] if len(portfolio_df) > 0 else None
    worst_performer = portfolio_df.loc[portfolio_df['損益率(%)'].idxmin()] if len(portfolio_df) > 0 else None
    
    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_gain_loss': total_gain_loss,
        'total_gain_loss_pct': total_gain_loss_pct,
        'best_performer': best_performer,
        'worst_performer': worst_performer
    }


def run_monte_carlo_simulation(portfolio_df, days=252, simulations=10000):
    """
    モンテカルロシミュレーションを実行
    
    Args:
        portfolio_df (pd.DataFrame): ポートフォリオデータ
        days (int): シミュレーション日数
        simulations (int): シミュレーション回数
        
    Returns:
        dict: シミュレーション結果
    """
    if portfolio_df.empty:
        return None
    
    try:
        # 各銘柄の過去データ取得
        returns_data = []
        weights = []
        
        for _, row in portfolio_df.iterrows():
            hist = get_historical_data(row['ティッカー'], period="1y")
            if not hist.empty:
                returns = hist['Close'].pct_change().dropna()
                returns_data.append(returns)
                weights.append(row['現在価値'])
        
        if not returns_data:
            return None
        
        # ウェイトの正規化
        total_value = sum(weights)
        weights = [w / total_value for w in weights]
        
        # リターンデータを結合
        returns_df = pd.concat(returns_data, axis=1)
        returns_df.columns = [f"Asset_{i}" for i in range(len(returns_data))]
        returns_df = returns_df.dropna()
        
        # 平均リターンと共分散行列
        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()
        
        # モンテカルロシミュレーション実行
        initial_portfolio = total_value
        simulation_results = np.zeros((simulations, days))
        
        for i in range(simulations):
            daily_returns = np.random.multivariate_normal(mean_returns, cov_matrix, days)
            portfolio_returns = np.dot(daily_returns, weights)
            portfolio_values = initial_portfolio * np.cumprod(1 + portfolio_returns)
            simulation_results[i] = portfolio_values
        
        # 統計情報計算
        final_values = simulation_results[:, -1]
        
        return {
            'simulation_results': simulation_results,
            'initial_value': initial_portfolio,
            'mean_final_value': np.mean(final_values),
            'median_final_value': np.median(final_values),
            'percentile_5': np.percentile(final_values, 5),
            'percentile_25': np.percentile(final_values, 25),
            'percentile_75': np.percentile(final_values, 75),
            'percentile_95': np.percentile(final_values, 95),
            'max_value': np.max(final_values),
            'min_value': np.min(final_values),
            'days': days,
            'simulations': simulations
        }
    except Exception as e:
        st.error(f"モンテカルロシミュレーションエラー: {str(e)}")
        return None


def get_stock_news(ticker_symbol, num_articles=5):
    """
    株式関連ニュースを取得
    
    Args:
        ticker_symbol (str): 株式のティッカーシンボル
        num_articles (int): 取得する記事数
        
    Returns:
        list: ニュース記事のリスト
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        return news[:num_articles] if news else []
    except Exception as e:
        st.error(f"ニュース取得エラー: {str(e)}")
        return []


def create_shareable_url(portfolio_data):
    """
    共有可能なURLを生成
    
    Args:
        portfolio_data (list): ポートフォリオデータ
        
    Returns:
        str: 共有用URL
    """
    try:
        portfolio_json = json.dumps(portfolio_data)
        params = {'portfolio': portfolio_json}
        base_url = "https://stock-portfolio-pro-3rv7hhykj6dcwxzqpopvl8.streamlit.app/"
        return f"{base_url}?{urlencode(params)}"
    except Exception as e:
        st.error(f"URL生成エラー: {str(e)}")
        return None


def load_portfolio_from_url():
    """
    URLパラメータからポートフォリオをロード
    
    Returns:
        list: ポートフォリオデータ、なければNone
    """
    try:
        query_params = st.query_params
        if 'portfolio' in query_params:
            portfolio_json = query_params['portfolio']
            return json.loads(portfolio_json)
        return None
    except Exception as e:
        st.error(f"URLからの読込エラー: {str(e)}")
        return None


def search_ticker(query):
    """
    ティッカーシンボルを検索
    
    Args:
        query (str): 検索クエリ
        
    Returns:
        list: マッチするティッカーシンボルのリスト
    """
    # よく使われる日米の株式ティッカー
    common_tickers = {
        # 米国株
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corporation',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation',
        'JPM': 'JPMorgan Chase & Co.',
        'V': 'Visa Inc.',
        'WMT': 'Walmart Inc.',
        'DIS': 'The Walt Disney Company',
        'NFLX': 'Netflix Inc.',
        'BA': 'Boeing Company',
        'INTC': 'Intel Corporation',
        'AMD': 'Advanced Micro Devices',
        # 日本株
        '7203.T': 'トヨタ自動車',
        '6758.T': 'ソニーグループ',
        '9984.T': 'ソフトバンクグループ',
        '6861.T': 'キーエンス',
        '8306.T': '三菱UFJフィナンシャル・グループ',
        '6902.T': 'デンソー',
        '7974.T': '任天堂',
        '9432.T': '日本電信電話',
        '8035.T': '東京エレクトロン',
        '4063.T': '信越化学工業',
    }
    
    query_upper = query.upper()
    results = []
    
    for ticker, name in common_tickers.items():
        if query_upper in ticker.upper() or query.lower() in name.lower():
            results.append(f"{ticker} - {name}")
    
    return results[:10]  # 最大10件


def get_dividend_data(ticker_symbol):
    """
    配当データを取得
    
    Args:
        ticker_symbol (str): 株式のティッカーシンボル
        
    Returns:
        pd.DataFrame: 配当データ
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        dividends = ticker.dividends
        
        if dividends.empty:
            return pd.DataFrame()
        
        # DataFrameに変換
        div_df = pd.DataFrame({
            'Date': dividends.index,
            'Dividend': dividends.values
        })
        div_df['Year'] = div_df['Date'].dt.year
        div_df['Month'] = div_df['Date'].dt.month
        
        return div_df
    except Exception as e:
        st.error(f"配当データ取得エラー ({ticker_symbol}): {str(e)}")
        return pd.DataFrame()


def calculate_efficient_frontier(portfolio_df, num_portfolios=5000):
    """
    効率的フロンティアを計算
    
    Args:
        portfolio_df (pd.DataFrame): ポートフォリオデータ
        num_portfolios (int): ランダムポートフォリオの数
        
    Returns:
        dict: 効率的フロンティアのデータ
    """
    if portfolio_df.empty or len(portfolio_df) < 2:
        return None
    
    try:
        # 各銘柄の過去データ取得
        returns_data = []
        tickers = []
        
        for _, row in portfolio_df.iterrows():
            hist = get_historical_data(row['ティッカー'], period="1y")
            if not hist.empty:
                returns = hist['Close'].pct_change().dropna()
                returns_data.append(returns)
                tickers.append(row['ティッカー'])
        
        if len(returns_data) < 2:
            return None
        
        # リターンデータを結合
        returns_df = pd.concat(returns_data, axis=1)
        returns_df.columns = tickers
        returns_df = returns_df.dropna()
        
        # 平均リターンと共分散行列
        mean_returns = returns_df.mean() * 252  # 年率化
        cov_matrix = returns_df.cov() * 252  # 年率化
        
        # 現在のポートフォリオのウェイト
        current_weights = portfolio_df['現在価値'].values / portfolio_df['現在価値'].sum()
        current_return = np.dot(current_weights, mean_returns)
        current_risk = np.sqrt(np.dot(current_weights.T, np.dot(cov_matrix, current_weights)))
        
        # ランダムポートフォリオ生成
        results = np.zeros((4, num_portfolios))
        
        for i in range(num_portfolios):
            # ランダムウェイト生成
            weights = np.random.random(len(tickers))
            weights /= weights.sum()
            
            # ポートフォリオのリターンとリスク計算
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # シャープレシオ計算（リスクフリーレート0と仮定）
            sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
            
            results[0, i] = portfolio_risk
            results[1, i] = portfolio_return
            results[2, i] = sharpe_ratio
            results[3, i] = i
        
        # 最小分散ポートフォリオ
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(len(tickers)))
        initial_guess = [1. / len(tickers) for _ in range(len(tickers))]
        
        min_var_result = minimize(
            portfolio_variance,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        min_var_weights = min_var_result.x
        min_var_return = np.dot(min_var_weights, mean_returns)
        min_var_risk = np.sqrt(portfolio_variance(min_var_weights))
        
        # 最大シャープレシオポートフォリオ
        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
        
        max_sharpe_result = minimize(
            negative_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        max_sharpe_weights = max_sharpe_result.x
        max_sharpe_return = np.dot(max_sharpe_weights, mean_returns)
        max_sharpe_risk = np.sqrt(np.dot(max_sharpe_weights.T, np.dot(cov_matrix, max_sharpe_weights)))
        
        return {
            'results': results,
            'tickers': tickers,
            'current_weights': current_weights,
            'current_return': current_return,
            'current_risk': current_risk,
            'min_var_weights': min_var_weights,
            'min_var_return': min_var_return,
            'min_var_risk': min_var_risk,
            'max_sharpe_weights': max_sharpe_weights,
            'max_sharpe_return': max_sharpe_return,
            'max_sharpe_risk': max_sharpe_risk,
        }
    except Exception as e:
        st.error(f"効率的フロンティア計算エラー: {str(e)}")
        return None


# ================================================================================
# メインアプリケーション
# ================================================================================

def main():
    """
    メインアプリケーション関数
    """
    # ヘッダー
    st.title("📊 株式ポートフォリオ管理システム")
    st.markdown("**プロフェッショナル投資家向け総合分析プラットフォーム**")
    st.markdown("---")
    
    # URLからポートフォリオをロード
    url_portfolio = load_portfolio_from_url()
    if url_portfolio and not st.session_state.portfolio:
        st.session_state.portfolio = url_portfolio
        st.success("✅ URLからポートフォリオを読み込みました")
    
    # ================================================================================
    # サイドバー: ポートフォリオ入力
    # ================================================================================
    
    with st.sidebar:
        st.markdown("## ⚙️ ポートフォリオ設定")
        
        # ================================================================================
        # 銘柄追加セクション
        # ================================================================================
        
        st.markdown("### 📈 銘柄追加")
        
        with st.container():
            # ティッカー検索
            search_query = st.text_input(
                "🔍 ティッカー検索",
                placeholder="AAPL, GOOGL, 7203.T など",
                help="銘柄名またはティッカーシンボルで検索",
                key="ticker_search"
            )
            
            if search_query:
                search_results = search_ticker(search_query)
                if search_results:
                    selected = st.selectbox(
                        "検索結果から選択",
                        search_results,
                        key="search_results"
                    )
                    ticker_symbol = selected.split(" - ")[0] if selected else ""
                else:
                    st.info("💡 該当する銘柄が見つかりませんでした")
                    ticker_symbol = search_query
            else:
                ticker_symbol = st.text_input(
                    "ティッカーシンボル",
                    placeholder="AAPL",
                    help="Yahoo Financeのティッカーシンボル",
                    key="ticker_input"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                shares = st.number_input(
                    "株数",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    format="%.2f",
                    key="shares_input"
                )
            with col2:
                purchase_price = st.number_input(
                    "取得単価 ($)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="price_input"
                )
            
            if st.button("➕ 銘柄を追加", key="add_stock"):
                if ticker_symbol and shares > 0 and purchase_price > 0:
                    ticker_info = get_ticker_info(ticker_symbol)
                    if ticker_info:
                        st.session_state.portfolio.append({
                            'ticker': ticker_symbol,
                            'shares': shares,
                            'purchase_price': purchase_price,
                            'name': ticker_info['name']
                        })
                        st.success(f"✅ {ticker_symbol} を追加しました")
                        st.rerun()
                else:
                    st.warning("⚠️ すべての項目を入力してください")
        
        # ================================================================================
        # 保有銘柄リスト
        # ================================================================================
        
        if st.session_state.portfolio:
            st.markdown("---")
            st.markdown("### 💼 保有銘柄一覧")
            
            st.info(f"📊 **合計: {len(st.session_state.portfolio)} 銘柄**")
            
            for idx, holding in enumerate(st.session_state.portfolio):
                with st.expander(f"**{holding['ticker']}** ({holding['shares']:.0f}株)", expanded=False):
                    st.markdown(f"**📌 {holding['name']}**")
                    st.markdown(f"**株数:** {holding['shares']:.2f}")
                    st.markdown(f"**取得単価:** ${holding['purchase_price']:.2f}")
                    st.markdown(f"**投資額:** ${holding['shares'] * holding['purchase_price']:.2f}")
                    
                    if st.button("🗑️ 削除", key=f"delete_{idx}"):
                        st.session_state.portfolio.pop(idx)
                        st.rerun()
            
            # ================================================================================
            # ポートフォリオ管理ボタン
            # ================================================================================
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ クリア", key="clear_portfolio"):
                    st.session_state.portfolio = []
                    st.session_state.target_allocation = {}
                    st.rerun()
            
            with col2:
                if st.button("🔗 URL共有", key="share_url"):
                    url = create_shareable_url(st.session_state.portfolio)
                    if url:
                        st.code(url, language=None)
                        st.info("💡 このURLでポートフォリオを共有できます")
        
        # ================================================================================
        # リバランス設定
        # ================================================================================
        
        if st.session_state.portfolio:
            st.markdown("---")
            st.markdown("### ⚖️ リバランス設定")
            
            st.info("💡 各銘柄の目標配分比率を設定（合計100%）")
            
            # 目標配分の入力
            total_target = 0
            
            with st.container():
                for holding in st.session_state.portfolio:
                    ticker = holding['ticker']
                    current_value = st.session_state.target_allocation.get(ticker, 0)
                    
                    target = st.slider(
                        f"**{ticker}**",
                        min_value=0,
                        max_value=100,
                        value=int(current_value),
                        step=5,
                        format="%d%%",
                        key=f"target_{ticker}",
                        help=f"{holding['name']}の目標配分比率"
                    )
                    st.session_state.target_allocation[ticker] = target
                    total_target += target
            
            # バリデーション表示
            st.markdown("---")
            
            if total_target == 100:
                st.success(f"✅ **合計: {total_target}%**")
            elif total_target < 100:
                st.warning(f"⚠️ **合計: {total_target}%** (残り {100-total_target}%)")
            else:
                st.error(f"❌ **合計: {total_target}%** (超過 {total_target-100}%)")
            
            # リセットボタン
            if st.button("🔄 配分をリセット", key="reset_allocation"):
                st.session_state.target_allocation = {}
                st.rerun()
    
    # ================================================================================
    # メインコンテンツ
    # ================================================================================
    
    if not st.session_state.portfolio:
        # ウェルカム画面
        st.info("👈 **サイドバーから銘柄を追加してポートフォリオを作成してください**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            ### 📊 リアルタイム分析
            - 現在価格の自動取得
            - 損益の即座計算
            - パフォーマンス追跡
            """)
        with col2:
            st.markdown("""
            ### 🎲 モンテカルロ
            - 将来価値予測
            - リスク分析
            - 信頼区間表示
            """)
        with col3:
            st.markdown("""
            ### 📰 ニュース統合
            - 最新ニュース
            - 銘柄別フィード
            - 投資判断支援
            """)
        
        st.markdown("---")
        st.markdown("""
        ### 🆕 新機能
        
        #### ⚖️ リバランス提案
        - 目標配分vs現状配分の比較
        - 売買推奨金額の自動計算
        - 視覚的な配分分析
        
        #### 💰 配当追跡
        - 月別配当カレンダー
        - 配当履歴の可視化
        - 配当利回りランキング
        
        #### 📈 効率的フロンティア
        - モダンポートフォリオ理論
        - 最適配分の提案
        - リスク・リターン分析
        """)
        
        return
    
    # ポートフォリオデータフレーム作成
    portfolio_data = []
    
    for holding in st.session_state.portfolio:
        ticker_info = get_ticker_info(holding['ticker'])
        if ticker_info:
            current_value = ticker_info['current_price'] * holding['shares']
            cost_basis = holding['purchase_price'] * holding['shares']
            gain_loss = current_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
            
            portfolio_data.append({
                'ティッカー': holding['ticker'],
                '銘柄名': holding['name'],
                '株数': holding['shares'],
                '取得単価': holding['purchase_price'],
                '現在価格': ticker_info['current_price'],
                '取得価額': cost_basis,
                '現在価値': current_value,
                '損益': gain_loss,
                '損益率(%)': gain_loss_pct,
                '通貨': ticker_info['currency']
            })
    
    portfolio_df = pd.DataFrame(portfolio_data)
    
    # タブ作成
    tabs = st.tabs([
        "📊 ダッシュボード",
        "🔬 分析",
        "💰 配当",
        "🎲 シミュレーション",
        "📰 ニュース"
    ])
    
    # ================================================================================
    # タブ1: ダッシュボード
    # ================================================================================
    
    with tabs[0]:
        # KPI表示
        metrics = calculate_portfolio_metrics(portfolio_df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">総資産価値</div>
                <div class="kpi-value">{format_currency(metrics['total_value'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">総取得価額</div>
                <div class="kpi-value">{format_currency(metrics['total_cost'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            gain_loss_color = "🟢" if metrics['total_gain_loss'] >= 0 else "🔴"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">総損益 {gain_loss_color}</div>
                <div class="kpi-value">{format_currency(metrics['total_gain_loss'])}</div>
                <div class="kpi-change">{format_percentage(metrics['total_gain_loss_pct'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if metrics['best_performer'] is not None:
                best_ticker = metrics['best_performer']['ティッカー']
                best_pct = metrics['best_performer']['損益率(%)']
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">最高パフォーマー</div>
                    <div class="kpi-value">{best_ticker}</div>
                    <div class="kpi-change">+{format_percentage(best_pct)}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ポートフォリオ構成
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="section-header">💼 ポートフォリオ構成</div>', unsafe_allow_html=True)
            
            # 円グラフ
            fig_pie = px.pie(
                portfolio_df,
                values='現在価値',
                names='ティッカー',
                title='銘柄別構成比',
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header">📊 パフォーマンスランキング</div>', unsafe_allow_html=True)
            
            # パフォーマンスランキング
            top_performers = portfolio_df.nlargest(5, '損益率(%)')
            for _, row in top_performers.iterrows():
                delta_color = "normal" if row['損益率(%)'] >= 0 else "inverse"
                st.metric(
                    label=row['ティッカー'],
                    value=format_currency(row['現在価値']),
                    delta=f"{row['損益率(%)']:.2f}%",
                    delta_color=delta_color
                )
        
        # 詳細テーブル
        st.markdown('<div class="section-header">📋 保有銘柄詳細</div>', unsafe_allow_html=True)
        
        # 表示用にフォーマット
        display_df = portfolio_df.copy()
        display_df['取得単価'] = display_df['取得単価'].apply(lambda x: f"${x:.2f}")
        display_df['現在価格'] = display_df['現在価格'].apply(lambda x: f"${x:.2f}")
        display_df['取得価額'] = display_df['取得価額'].apply(format_currency)
        display_df['現在価値'] = display_df['現在価値'].apply(format_currency)
        display_df['損益'] = display_df['損益'].apply(format_currency)
        display_df['損益率(%)'] = display_df['損益率(%)'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    
    # ================================================================================
    # タブ2: 分析
    # ================================================================================
    
    with tabs[1]:
        st.markdown('<div class="section-header">📈 リスク・リターン分析</div>', unsafe_allow_html=True)
        
        # 各銘柄の過去1年のリターン計算
        returns_data = []
        for _, row in portfolio_df.iterrows():
            hist = get_historical_data(row['ティッカー'], period="1y")
            if not hist.empty:
                total_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                volatility = hist['Close'].pct_change().std() * np.sqrt(252) * 100
                
                returns_data.append({
                    'ティッカー': row['ティッカー'],
                    '年間リターン(%)': total_return,
                    'ボラティリティ(%)': volatility,
                    '保有比率(%)': (row['現在価値'] / metrics['total_value']) * 100
                })
        
        if returns_data:
            returns_df = pd.DataFrame(returns_data)
            
            # バブルチャート
            fig_bubble = px.scatter(
                returns_df,
                x='ボラティリティ(%)',
                y='年間リターン(%)',
                size='保有比率(%)',
                color='ティッカー',
                hover_name='ティッカー',
                title='リスク・リターン マップ',
                labels={
                    'ボラティリティ(%)': 'リスク (ボラティリティ %)',
                    '年間リターン(%)': 'リターン (%)'
                }
            )
            fig_bubble.update_layout(height=500)
            st.plotly_chart(fig_bubble, use_container_width=True)
            
            # 相関マトリックス
            st.markdown('<div class="section-header">🔗 相関マトリックス</div>', unsafe_allow_html=True)
            
            correlation_data = []
            tickers = portfolio_df['ティッカー'].tolist()
            
            for ticker in tickers:
                hist = get_historical_data(ticker, period="1y")
                if not hist.empty:
                    correlation_data.append(hist['Close'].pct_change())
            
            if len(correlation_data) > 1:
                corr_df = pd.concat(correlation_data, axis=1)
                corr_df.columns = tickers
                corr_matrix = corr_df.corr()
                
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    aspect='auto',
                    color_continuous_scale='RdBu_r',
                    title='銘柄間相関係数'
                )
                st.plotly_chart(fig_corr, use_container_width=True)
        
        # リバランス分析
        if st.session_state.target_allocation and sum(st.session_state.target_allocation.values()) == 100:
            st.markdown("---")
            st.markdown('<div class="section-header">⚖️ リバランス分析</div>', unsafe_allow_html=True)
            
            # 現在の配分を計算
            total_value = portfolio_df['現在価値'].sum()
            current_allocation = {}
            
            for _, row in portfolio_df.iterrows():
                ticker = row['ティッカー']
                current_pct = (row['現在価値'] / total_value) * 100
                current_allocation[ticker] = current_pct
            
            # 配分比較データ作成
            rebalance_data = []
            for ticker in st.session_state.target_allocation.keys():
                target = st.session_state.target_allocation[ticker]
                current = current_allocation.get(ticker, 0)
                
                # 必要な売買金額を計算
                target_value = total_value * (target / 100)
                current_value = portfolio_df[portfolio_df['ティッカー'] == ticker]['現在価値'].iloc[0] if ticker in portfolio_df['ティッカー'].values else 0
                trade_amount = target_value - current_value
                
                rebalance_data.append({
                    'ティッカー': ticker,
                    '現在配分(%)': current,
                    '目標配分(%)': target,
                    '差分(%)': target - current,
                    '売買金額': trade_amount
                })
            
            rebalance_df = pd.DataFrame(rebalance_data)
            
            # 配分比較グラフ
            fig_rebalance = go.Figure()
            
            fig_rebalance.add_trace(go.Bar(
                name='現在配分',
                x=rebalance_df['ティッカー'],
                y=rebalance_df['現在配分(%)'],
                marker_color='lightblue'
            ))
            
            fig_rebalance.add_trace(go.Bar(
                name='目標配分',
                x=rebalance_df['ティッカー'],
                y=rebalance_df['目標配分(%)'],
                marker_color='darkblue'
            ))
            
            fig_rebalance.update_layout(
                title='現在配分 vs 目標配分',
                xaxis_title='ティッカー',
                yaxis_title='配分比率 (%)',
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_rebalance, use_container_width=True)
            
            # リバランス推奨テーブル
            st.markdown("#### 📋 リバランス推奨取引")
            
            display_rebalance = rebalance_df.copy()
            display_rebalance['現在配分(%)'] = display_rebalance['現在配分(%)'].apply(lambda x: f"{x:.2f}%")
            display_rebalance['目標配分(%)'] = display_rebalance['目標配分(%)'].apply(lambda x: f"{x:.2f}%")
            display_rebalance['差分(%)'] = display_rebalance['差分(%)'].apply(lambda x: f"{x:+.2f}%")
            
            def format_trade(amount):
                if amount > 0:
                    return f"🟢 買い増し {format_currency(amount)}"
                elif amount < 0:
                    return f"🔴 売却 {format_currency(abs(amount))}"
                else:
                    return "⚪ 調整不要"
            
            display_rebalance['推奨取引'] = rebalance_df['売買金額'].apply(format_trade)
            display_rebalance = display_rebalance.drop('売買金額', axis=1)
            
            st.dataframe(display_rebalance, use_container_width=True, hide_index=True)
            
            # アラート
            max_diff = rebalance_df['差分(%)'].abs().max()
            if max_diff > 5:
                st.warning(f"⚠️ 最大乖離: {max_diff:.2f}% - リバランスを検討してください")
            else:
                st.success("✅ ポートフォリオは目標配分に近い状態です")
        
        # 効率的フロンティア
        st.markdown("---")
        st.markdown('<div class="section-header">📊 効率的フロンティア</div>', unsafe_allow_html=True)
        
        if st.button("効率的フロンティアを計算", use_container_width=True):
            with st.spinner("計算中..."):
                frontier_data = calculate_efficient_frontier(portfolio_df, num_portfolios=5000)
            
            if frontier_data:
                # プロット
                fig_frontier = go.Figure()
                
                # ランダムポートフォリオ
                fig_frontier.add_trace(go.Scatter(
                    x=frontier_data['results'][0],
                    y=frontier_data['results'][1] * 100,
                    mode='markers',
                    marker=dict(
                        size=3,
                        color=frontier_data['results'][2],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="シャープレシオ")
                    ),
                    name='ランダムポートフォリオ',
                    hovertemplate='リスク: %{x:.2%}<br>リターン: %{y:.2f}%<extra></extra>'
                ))
                
                # 現在のポートフォリオ
                fig_frontier.add_trace(go.Scatter(
                    x=[frontier_data['current_risk']],
                    y=[frontier_data['current_return'] * 100],
                    mode='markers',
                    marker=dict(size=20, color='red', symbol='star', line=dict(width=2, color='white')),
                    name='現在のポートフォリオ',
                    hovertemplate='現在<br>リスク: %{x:.2%}<br>リターン: %{y:.2f}%<extra></extra>'
                ))
                
                # 最小分散ポートフォリオ
                fig_frontier.add_trace(go.Scatter(
                    x=[frontier_data['min_var_risk']],
                    y=[frontier_data['min_var_return'] * 100],
                    mode='markers',
                    marker=dict(size=15, color='green', symbol='diamond', line=dict(width=2, color='white')),
                    name='最小分散',
                    hovertemplate='最小分散<br>リスク: %{x:.2%}<br>リターン: %{y:.2f}%<extra></extra>'
                ))
                
                # 最大シャープレシオ
                fig_frontier.add_trace(go.Scatter(
                    x=[frontier_data['max_sharpe_risk']],
                    y=[frontier_data['max_sharpe_return'] * 100],
                    mode='markers',
                    marker=dict(size=15, color='gold', symbol='star', line=dict(width=2, color='black')),
                    name='最大シャープレシオ',
                    hovertemplate='最大シャープレシオ<br>リスク: %{x:.2%}<br>リターン: %{y:.2f}%<extra></extra>'
                ))
                
                fig_frontier.update_layout(
                    title='効率的フロンティア',
                    xaxis_title='リスク (年率ボラティリティ)',
                    yaxis_title='期待リターン (年率 %)',
                    height=600,
                    hovermode='closest'
                )
                
                fig_frontier.update_xaxes(tickformat='.1%')
                
                st.plotly_chart(fig_frontier, use_container_width=True)
                
                # 推奨配分比較
                st.markdown("#### 📋 推奨ポートフォリオ配分")
                
                allocation_comparison = pd.DataFrame({
                    'ティッカー': frontier_data['tickers'],
                    '現在配分(%)': frontier_data['current_weights'] * 100,
                    '最小分散(%)': frontier_data['min_var_weights'] * 100,
                    '最大シャープレシオ(%)': frontier_data['max_sharpe_weights'] * 100
                })
                
                # フォーマット
                for col in ['現在配分(%)', '最小分散(%)', '最大シャープレシオ(%)']:
                    allocation_comparison[col] = allocation_comparison[col].apply(lambda x: f"{x:.2f}%")
                
                st.dataframe(allocation_comparison, use_container_width=True, hide_index=True)
                
                # サマリー統計
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-label">現在のポートフォリオ</div>
                        <div class="kpi-value">{frontier_data['current_return']*100:.2f}%</div>
                        <div class="kpi-change">リスク: {frontier_data['current_risk']*100:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-label">最小分散</div>
                        <div class="kpi-value">{frontier_data['min_var_return']*100:.2f}%</div>
                        <div class="kpi-change">リスク: {frontier_data['min_var_risk']*100:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    sharpe = frontier_data['max_sharpe_return'] / frontier_data['max_sharpe_risk']
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-label">最大シャープレシオ</div>
                        <div class="kpi-value">{frontier_data['max_sharpe_return']*100:.2f}%</div>
                        <div class="kpi-change">シャープ: {sharpe:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("効率的フロンティアの計算に失敗しました。少なくとも2銘柄が必要です。")
    
    # ================================================================================
    # タブ3: 配当
    # ================================================================================
    
    with tabs[2]:
        st.markdown('<div class="section-header">💰 配当分析</div>', unsafe_allow_html=True)
        
        # 各銘柄の配当データを取得
        all_dividends = []
        dividend_summary = []
        
        for _, row in portfolio_df.iterrows():
            ticker = row['ティッカー']
            shares = row['株数']
            
            div_df = get_dividend_data(ticker)
            
            if not div_df.empty:
                div_df['Ticker'] = ticker
                div_df['TotalDividend'] = div_df['Dividend'] * shares
                all_dividends.append(div_df)
                
                # サマリー統計
                recent_dividends = div_df[div_df['Year'] == div_df['Year'].max()]
                annual_dividend = recent_dividends['TotalDividend'].sum()
                dividend_count = len(recent_dividends)
                avg_dividend = div_df['Dividend'].mean()
                
                # 配当利回り計算
                current_price = row['現在価格']
                div_yield = (annual_dividend / shares / current_price * 100) if current_price > 0 else 0
                
                dividend_summary.append({
                    'ティッカー': ticker,
                    '年間配当額': annual_dividend,
                    '配当回数/年': dividend_count,
                    '平均配当/株': avg_dividend,
                    '配当利回り(%)': div_yield
                })
        
        if all_dividends:
            combined_div = pd.concat(all_dividends, ignore_index=True)
            
            # 配当利回りランキング
            st.markdown("#### 🏆 配当利回りランキング")
            
            if dividend_summary:
                div_summary_df = pd.DataFrame(dividend_summary)
                div_summary_df = div_summary_df.sort_values('配当利回り(%)', ascending=False)
                
                col1, col2, col3 = st.columns(3)
                
                for idx, (i, col) in enumerate(zip(range(min(3, len(div_summary_df))), [col1, col2, col3])):
                    row = div_summary_df.iloc[i]
                    medal = ["🥇", "🥈", "🥉"][idx]
                    
                    with col:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="kpi-label">{medal} {row['ティッカー']}</div>
                            <div class="kpi-value">{row['配当利回り(%)']:.2f}%</div>
                            <div class="kpi-change">年間: {format_currency(row['年間配当額'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # 月別配当カレンダー
            st.markdown("---")
            st.markdown("#### 📅 月別配当カレンダー")
            
            # 直近2年分のデータをフィルタ
            current_year = datetime.now().year
            recent_div = combined_div[combined_div['Year'] >= current_year - 1].copy()
            
            if not recent_div.empty:
                # 月別集計
                monthly_div = recent_div.groupby(['Year', 'Month', 'Ticker'])['TotalDividend'].sum().reset_index()
                monthly_div['YearMonth'] = monthly_div['Year'].astype(str) + '-' + monthly_div['Month'].astype(str).str.zfill(2)
                
                # スタックバーチャート
                fig_monthly = px.bar(
                    monthly_div,
                    x='YearMonth',
                    y='TotalDividend',
                    color='Ticker',
                    title='月別配当受取額',
                    labels={'TotalDividend': '配当額 (¥)', 'YearMonth': '年月'},
                    barmode='stack'
                )
                
                fig_monthly.update_layout(height=400)
                st.plotly_chart(fig_monthly, use_container_width=True)
            
            # 年間配当推移
            st.markdown("---")
            st.markdown("#### 📈 年間配当収入推移")
            
            yearly_div = combined_div.groupby(['Year', 'Ticker'])['TotalDividend'].sum().reset_index()
            
            fig_yearly = px.line(
                yearly_div,
                x='Year',
                y='TotalDividend',
                color='Ticker',
                title='年間配当収入の推移',
                labels={'TotalDividend': '配当額 (¥)', 'Year': '年'},
                markers=True
            )
            
            fig_yearly.update_layout(height=400)
            st.plotly_chart(fig_yearly, use_container_width=True)
            
            # 配当サマリーテーブル
            st.markdown("---")
            st.markdown("#### 📋 配当サマリー")
            
            if dividend_summary:
                display_summary = div_summary_df.copy()
                display_summary['年間配当額'] = display_summary['年間配当額'].apply(format_currency)
                display_summary['平均配当/株'] = display_summary['平均配当/株'].apply(lambda x: f"${x:.2f}")
                display_summary['配当利回り(%)'] = display_summary['配当利回り(%)'].apply(lambda x: f"{x:.2f}%")
                
                st.dataframe(display_summary, use_container_width=True, hide_index=True)
                
                # 合計配当
                total_annual = div_summary_df['年間配当額'].sum()
                st.info(f"💰 **年間配当収入合計: {format_currency(total_annual)}**")
        else:
            st.info("💡 配当データが見つかりませんでした。配当を支払っている銘柄を追加してください。")
    
    # ================================================================================
    # タブ4: シミュレーション
    # ================================================================================
    
    with tabs[3]:
        st.markdown('<div class="section-header">🎲 モンテカルロシミュレーション</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            sim_days = st.slider("シミュレーション期間（営業日）", 30, 1260, 252)
        with col2:
            sim_count = st.selectbox("シミュレーション回数", [1000, 5000, 10000], index=1)
        
        if st.button("🚀 シミュレーション実行", use_container_width=True):
            with st.spinner("シミュレーション実行中..."):
                results = run_monte_carlo_simulation(portfolio_df, days=sim_days, simulations=sim_count)
                st.session_state.simulation_results = results
        
        if st.session_state.simulation_results:
            results = st.session_state.simulation_results
            
            # 結果サマリー
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">現在価値</div>
                    <div class="kpi-value">{format_currency(results['initial_value'])}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">予測中央値</div>
                    <div class="kpi-value">{format_currency(results['median_final_value'])}</div>
                    <div class="kpi-change">{((results['median_final_value']/results['initial_value']-1)*100):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">95%信頼区間下限</div>
                    <div class="kpi-value">{format_currency(results['percentile_5'])}</div>
                    <div class="kpi-change">{((results['percentile_5']/results['initial_value']-1)*100):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">95%信頼区間上限</div>
                    <div class="kpi-value">{format_currency(results['percentile_95'])}</div>
                    <div class="kpi-change">{((results['percentile_95']/results['initial_value']-1)*100):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            # シミュレーション結果グラフ
            st.markdown("---")
            st.markdown("#### 📊 シミュレーション結果")
            
            fig_sim = go.Figure()
            
            # ランダムに100本のパスを表示
            num_paths_to_plot = min(100, results['simulations'])
            indices = np.random.choice(results['simulations'], num_paths_to_plot, replace=False)
            
            for idx in indices:
                fig_sim.add_trace(go.Scatter(
                    y=results['simulation_results'][idx],
                    mode='lines',
                    line=dict(width=0.5, color='lightblue'),
                    opacity=0.3,
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # 中央値
            median_path = np.median(results['simulation_results'], axis=0)
            fig_sim.add_trace(go.Scatter(
                y=median_path,
                mode='lines',
                name='中央値',
                line=dict(width=3, color='blue')
            ))
            
            # 信頼区間
            percentile_5_path = np.percentile(results['simulation_results'], 5, axis=0)
            percentile_95_path = np.percentile(results['simulation_results'], 95, axis=0)
            
            fig_sim.add_trace(go.Scatter(
                y=percentile_95_path,
                mode='lines',
                name='95%上限',
                line=dict(width=2, color='green', dash='dash')
            ))
            
            fig_sim.add_trace(go.Scatter(
                y=percentile_5_path,
                mode='lines',
                name='5%下限',
                line=dict(width=2, color='red', dash='dash')
            ))
            
            fig_sim.update_layout(
                title=f'モンテカルロシミュレーション ({results["simulations"]:,}回, {results["days"]}営業日)',
                xaxis_title='営業日',
                yaxis_title='ポートフォリオ価値 (¥)',
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_sim, use_container_width=True)
            
            # 最終価値の分布
            st.markdown("---")
            st.markdown("#### 📊 最終価値の分布")
            
            final_values = results['simulation_results'][:, -1]
            
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=final_values,
                nbinsx=50,
                name='最終価値分布',
                marker_color='lightblue'
            ))
            
            # 統計線を追加
            fig_hist.add_vline(x=results['median_final_value'], line_dash="dash", line_color="blue", annotation_text="中央値")
            fig_hist.add_vline(x=results['percentile_5'], line_dash="dash", line_color="red", annotation_text="5%")
            fig_hist.add_vline(x=results['percentile_95'], line_dash="dash", line_color="green", annotation_text="95%")
            
            fig_hist.update_layout(
                title='最終ポートフォリオ価値の分布',
                xaxis_title='最終価値 (¥)',
                yaxis_title='頻度',
                height=400
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # 統計テーブル
            st.markdown("#### 📋 統計サマリー")
            
            stats_data = {
                '指標': [
                    '初期価値',
                    '平均最終価値',
                    '中央値',
                    '最小値',
                    '5パーセンタイル',
                    '25パーセンタイル',
                    '75パーセンタイル',
                    '95パーセンタイル',
                    '最大値'
                ],
                '金額': [
                    format_currency(results['initial_value']),
                    format_currency(results['mean_final_value']),
                    format_currency(results['median_final_value']),
                    format_currency(results['min_value']),
                    format_currency(results['percentile_5']),
                    format_currency(results['percentile_25']),
                    format_currency(results['percentile_75']),
                    format_currency(results['percentile_95']),
                    format_currency(results['max_value'])
                ],
                '変化率': [
                    '0.00%',
                    f"{((results['mean_final_value']/results['initial_value']-1)*100):+.2f}%",
                    f"{((results['median_final_value']/results['initial_value']-1)*100):+.2f}%",
                    f"{((results['min_value']/results['initial_value']-1)*100):+.2f}%",
                    f"{((results['percentile_5']/results['initial_value']-1)*100):+.2f}%",
                    f"{((results['percentile_25']/results['initial_value']-1)*100):+.2f}%",
                    f"{((results['percentile_75']/results['initial_value']-1)*100):+.2f}%",
                    f"{((results['percentile_95']/results['initial_value']-1)*100):+.2f}%",
                    f"{((results['max_value']/results['initial_value']-1)*100):+.2f}%"
                ]
            }
            
            st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
    
    # ================================================================================
    # タブ5: ニュース
    # ================================================================================
    
    with tabs[4]:
        st.markdown('<div class="section-header">📰 最新ニュース</div>', unsafe_allow_html=True)
        
        selected_ticker = st.selectbox(
            "銘柄を選択",
            portfolio_df['ティッカー'].tolist()
        )
        
        if selected_ticker:
            ticker_name = portfolio_df[portfolio_df['ティッカー'] == selected_ticker]['銘柄名'].iloc[0]
            st.markdown(f"### {ticker_name} ({selected_ticker})")
            
            news_articles = get_stock_news(selected_ticker, num_articles=10)
            
            if news_articles:
                for article in news_articles:
                    with st.container():
                        st.markdown(f"#### [{article.get('title', 'タイトルなし')}]({article.get('link', '#')})")
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(article.get('summary', 'サマリーなし')[:300] + "...")
                        with col2:
                            timestamp = article.get('providerPublishTime')
                            if timestamp:
                                pub_date = datetime.fromtimestamp(timestamp)
                                st.caption(f"📅 {pub_date.strftime('%Y-%m-%d %H:%M')}")
                            
                            publisher = article.get('publisher', '不明')
                            st.caption(f"📰 {publisher}")
                        
                        st.markdown("---")
            else:
                st.info("ニュースが見つかりませんでした")


# ================================================================================
# アプリケーション実行
# ================================================================================

if __name__ == "__main__":
    main()
