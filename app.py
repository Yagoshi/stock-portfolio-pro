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
from scipy.optimize import minimize
from datetime import datetime, timedelta
import json
import base64
import urllib.parse
import io
import time
from typing import Dict, List, Tuple, Optional

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
    # ════════════════════════════════════════════════════════
    # 米国株 - テクノロジー
    # ════════════════════════════════════════════════════════
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet (Google) Class A",
    "GOOG": "Alphabet (Google) Class C",
    "AMZN": "Amazon",
    "META": "Meta Platforms (Facebook)",
    "NVDA": "NVIDIA",
    "TSLA": "Tesla",
    "AMD": "Advanced Micro Devices",
    "INTC": "Intel",
    "AVGO": "Broadcom",
    "ORCL": "Oracle",
    "ADBE": "Adobe",
    "CRM": "Salesforce",
    "CSCO": "Cisco Systems",
    "ACN": "Accenture",
    "IBM": "IBM",
    "QCOM": "Qualcomm",
    "TXN": "Texas Instruments",
    "AMAT": "Applied Materials",
    "MU": "Micron Technology",
    "LRCX": "Lam Research",
    "KLAC": "KLA Corporation",
    "SNPS": "Synopsys",
    "CDNS": "Cadence Design Systems",
    "MRVL": "Marvell Technology",
    "NXPI": "NXP Semiconductors",
    "SHOP": "Shopify",
    "SQ": "Block (Square)",
    "PYPL": "PayPal",
    "SNOW": "Snowflake",
    "PLTR": "Palantir",
    "CRWD": "CrowdStrike",
    "NET": "Cloudflare",
    "DDOG": "Datadog",
    "ZS": "Zscaler",
    "OKTA": "Okta",
    "TEAM": "Atlassian",
    "NOW": "ServiceNow",
    "WDAY": "Workday",
    "PANW": "Palo Alto Networks",
    "FTNT": "Fortinet",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - 通信・メディア・エンターテイメント
    # ════════════════════════════════════════════════════════
    "NFLX": "Netflix",
    "DIS": "Walt Disney",
    "CMCSA": "Comcast",
    "T": "AT&T",
    "VZ": "Verizon",
    "TMUS": "T-Mobile",
    "CHTR": "Charter Communications",
    "EA": "Electronic Arts",
    "TTWO": "Take-Two Interactive",
    "RBLX": "Roblox",
    "U": "Unity Software",
    "SPOT": "Spotify",
    "PINS": "Pinterest",
    "SNAP": "Snap",
    "TWTR": "Twitter",
    "MTCH": "Match Group",
    "WBD": "Warner Bros Discovery",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - 金融
    # ════════════════════════════════════════════════════════
    "JPM": "JPMorgan Chase",
    "BAC": "Bank of America",
    "WFC": "Wells Fargo",
    "C": "Citigroup",
    "GS": "Goldman Sachs",
    "MS": "Morgan Stanley",
    "BLK": "BlackRock",
    "SCHW": "Charles Schwab",
    "AXP": "American Express",
    "V": "Visa",
    "MA": "Mastercard",
    "COIN": "Coinbase",
    "SOFI": "SoFi Technologies",
    "HOOD": "Robinhood",
    "AFRM": "Affirm",
    "SQ": "Block (Square)",
    "USB": "U.S. Bancorp",
    "PNC": "PNC Financial",
    "TFC": "Truist Financial",
    "COF": "Capital One",
    "BK": "Bank of New York Mellon",
    "STT": "State Street",
    "AIG": "American International Group",
    "MET": "MetLife",
    "PRU": "Prudential Financial",
    "ALL": "Allstate",
    "PGR": "Progressive",
    "TRV": "Travelers",
    "CB": "Chubb",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - ヘルスケア・バイオテクノロジー
    # ════════════════════════════════════════════════════════
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth Group",
    "PFE": "Pfizer",
    "ABBV": "AbbVie",
    "LLY": "Eli Lilly",
    "MRK": "Merck",
    "TMO": "Thermo Fisher Scientific",
    "ABT": "Abbott Laboratories",
    "DHR": "Danaher",
    "BMY": "Bristol Myers Squibb",
    "AMGN": "Amgen",
    "GILD": "Gilead Sciences",
    "CVS": "CVS Health",
    "CI": "Cigna",
    "ISRG": "Intuitive Surgical",
    "REGN": "Regeneron Pharmaceuticals",
    "VRTX": "Vertex Pharmaceuticals",
    "SYK": "Stryker",
    "BSX": "Boston Scientific",
    "MDT": "Medtronic",
    "ELV": "Elevance Health",
    "BIIB": "Biogen",
    "MRNA": "Moderna",
    "ZTS": "Zoetis",
    "HCA": "HCA Healthcare",
    "IDXX": "IDEXX Laboratories",
    "IQV": "IQVIA",
    "A": "Agilent Technologies",
    "BAX": "Baxter International",
    "BDX": "Becton Dickinson",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - 消費財・小売
    # ════════════════════════════════════════════════════════
    "WMT": "Walmart",
    "HD": "Home Depot",
    "COST": "Costco",
    "MCD": "McDonald's",
    "NKE": "Nike",
    "SBUX": "Starbucks",
    "TGT": "Target",
    "LOW": "Lowe's",
    "TJX": "TJX Companies",
    "BKNG": "Booking Holdings",
    "ABNB": "Airbnb",
    "MAR": "Marriott International",
    "HLT": "Hilton Worldwide",
    "YUM": "Yum! Brands",
    "CMG": "Chipotle Mexican Grill",
    "ROST": "Ross Stores",
    "DG": "Dollar General",
    "DLTR": "Dollar Tree",
    "BBY": "Best Buy",
    "EBAY": "eBay",
    "ETSY": "Etsy",
    "W": "Wayfair",
    "CHWY": "Chewy",
    "LULU": "Lululemon",
    "DECK": "Deckers Outdoor",
    "ULTA": "Ulta Beauty",
    "EL": "Estée Lauder",
    "CL": "Colgate-Palmolive",
    "PG": "Procter & Gamble",
    "KO": "Coca-Cola",
    "PEP": "PepsiCo",
    "MDLZ": "Mondelez International",
    "KHC": "Kraft Heinz",
    "GIS": "General Mills",
    "K": "Kellogg",
    "HSY": "Hershey",
    "MO": "Altria Group",
    "PM": "Philip Morris International",
    "BUD": "Anheuser-Busch InBev",
    "TAP": "Molson Coors",
    "STZ": "Constellation Brands",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - エネルギー
    # ════════════════════════════════════════════════════════
    "XOM": "Exxon Mobil",
    "CVX": "Chevron",
    "COP": "ConocoPhillips",
    "SLB": "Schlumberger",
    "EOG": "EOG Resources",
    "MPC": "Marathon Petroleum",
    "PSX": "Phillips 66",
    "VLO": "Valero Energy",
    "OXY": "Occidental Petroleum",
    "HAL": "Halliburton",
    "BKR": "Baker Hughes",
    "KMI": "Kinder Morgan",
    "WMB": "Williams Companies",
    "OKE": "ONEOK",
    "LNG": "Cheniere Energy",
    "FANG": "Diamondback Energy",
    "DVN": "Devon Energy",
    "HES": "Hess",
    "MRO": "Marathon Oil",
    "APA": "APA Corporation",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - 産業・製造
    # ════════════════════════════════════════════════════════
    "BA": "Boeing",
    "GE": "General Electric",
    "CAT": "Caterpillar",
    "HON": "Honeywell",
    "UPS": "United Parcel Service",
    "RTX": "Raytheon Technologies",
    "LMT": "Lockheed Martin",
    "DE": "Deere & Company",
    "MMM": "3M",
    "GD": "General Dynamics",
    "NOC": "Northrop Grumman",
    "EMR": "Emerson Electric",
    "ETN": "Eaton",
    "ITW": "Illinois Tool Works",
    "PH": "Parker-Hannifin",
    "CMI": "Cummins",
    "PCAR": "PACCAR",
    "ROK": "Rockwell Automation",
    "FDX": "FedEx",
    "NSC": "Norfolk Southern",
    "UNP": "Union Pacific",
    "CSX": "CSX Corporation",
    "LUV": "Southwest Airlines",
    "DAL": "Delta Air Lines",
    "UAL": "United Airlines",
    "AAL": "American Airlines",
    "ALK": "Alaska Air Group",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - 素材・化学
    # ════════════════════════════════════════════════════════
    "LIN": "Linde",
    "APD": "Air Products and Chemicals",
    "SHW": "Sherwin-Williams",
    "ECL": "Ecolab",
    "DD": "DuPont",
    "DOW": "Dow",
    "NEM": "Newmont",
    "FCX": "Freeport-McMoRan",
    "NUE": "Nucor",
    "STLD": "Steel Dynamics",
    "VMC": "Vulcan Materials",
    "MLM": "Martin Marietta Materials",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - 不動産・REIT
    # ════════════════════════════════════════════════════════
    "AMT": "American Tower",
    "PLD": "Prologis",
    "CCI": "Crown Castle",
    "EQIX": "Equinix",
    "PSA": "Public Storage",
    "WELL": "Welltower",
    "DLR": "Digital Realty Trust",
    "O": "Realty Income",
    "SBAC": "SBA Communications",
    "AVB": "AvalonBay Communities",
    "EQR": "Equity Residential",
    "VTR": "Ventas",
    "SPG": "Simon Property Group",
    "ARE": "Alexandria Real Estate",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - 公益事業
    # ════════════════════════════════════════════════════════
    "NEE": "NextEra Energy",
    "DUK": "Duke Energy",
    "SO": "Southern Company",
    "D": "Dominion Energy",
    "AEP": "American Electric Power",
    "EXC": "Exelon",
    "SRE": "Sempra Energy",
    "XEL": "Xcel Energy",
    "WEC": "WEC Energy Group",
    "ED": "Consolidated Edison",
    "AWK": "American Water Works",
    
    # ════════════════════════════════════════════════════════
    # 米国株 - ETF（主要インデックス・セクター・テーマ）
    # ════════════════════════════════════════════════════════
    "SPY": "SPDR S&P 500 ETF",
    "VOO": "Vanguard S&P 500 ETF",
    "IVV": "iShares Core S&P 500 ETF",
    "QQQ": "Invesco QQQ (NASDAQ-100)",
    "VTI": "Vanguard Total Stock Market ETF",
    "DIA": "SPDR Dow Jones Industrial Average ETF",
    "IWM": "iShares Russell 2000 ETF",
    "VTV": "Vanguard Value ETF",
    "VUG": "Vanguard Growth ETF",
    "VIG": "Vanguard Dividend Appreciation ETF",
    "SCHD": "Schwab U.S. Dividend Equity ETF",
    "VYM": "Vanguard High Dividend Yield ETF",
    "XLK": "Technology Select Sector SPDR",
    "XLF": "Financial Select Sector SPDR",
    "XLV": "Health Care Select Sector SPDR",
    "XLE": "Energy Select Sector SPDR",
    "XLY": "Consumer Discretionary Select Sector SPDR",
    "XLP": "Consumer Staples Select Sector SPDR",
    "XLI": "Industrial Select Sector SPDR",
    "XLB": "Materials Select Sector SPDR",
    "XLU": "Utilities Select Sector SPDR",
    "XLRE": "Real Estate Select Sector SPDR",
    "XLC": "Communication Services Select Sector SPDR",
    "VGT": "Vanguard Information Technology ETF",
    "VDE": "Vanguard Energy ETF",
    "VFH": "Vanguard Financials ETF",
    "VHT": "Vanguard Health Care ETF",
    "VNQ": "Vanguard Real Estate ETF",
    "ARKK": "ARK Innovation ETF",
    "ARKG": "ARK Genomic Revolution ETF",
    "ARKW": "ARK Next Generation Internet ETF",
    "ARKF": "ARK Fintech Innovation ETF",
    "ARKQ": "ARK Autonomous Technology & Robotics ETF",
    "SOXX": "iShares Semiconductor ETF",
    "SMH": "VanEck Semiconductor ETF",
    "IBB": "iShares Biotechnology ETF",
    "XBI": "SPDR S&P Biotech ETF",
    "FINX": "Global X FinTech ETF",
    "HACK": "ETFMG Prime Cyber Security ETF",
    "BOTZ": "Global X Robotics & AI ETF",
    "LIT": "Global X Lithium & Battery Tech ETF",
    "TAN": "Invesco Solar ETF",
    "ICLN": "iShares Global Clean Energy ETF",
    "JETS": "U.S. Global Jets ETF",
    "XRT": "SPDR S&P Retail ETF",
    "ITB": "iShares U.S. Home Construction ETF",
    "GDX": "VanEck Gold Miners ETF",
    "SLV": "iShares Silver Trust",
    "GLD": "SPDR Gold Trust",
    "USO": "United States Oil Fund",
    "UNG": "United States Natural Gas Fund",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "AGG": "iShares Core U.S. Aggregate Bond ETF",
    "BND": "Vanguard Total Bond Market ETF",
    "LQD": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
    "HYG": "iShares iBoxx $ High Yield Corporate Bond ETF",
    "EMB": "iShares J.P. Morgan USD Emerging Markets Bond ETF",
    "VEA": "Vanguard FTSE Developed Markets ETF",
    "VWO": "Vanguard FTSE Emerging Markets ETF",
    "IEMG": "iShares Core MSCI Emerging Markets ETF",
    "EFA": "iShares MSCI EAFE ETF",
    "EEM": "iShares MSCI Emerging Markets ETF",
    "FXI": "iShares China Large-Cap ETF",
    "EWJ": "iShares MSCI Japan ETF",
    "EWZ": "iShares MSCI Brazil ETF",
    "EWG": "iShares MSCI Germany ETF",
    "EWU": "iShares MSCI United Kingdom ETF",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 自動車・輸送機器
    # ════════════════════════════════════════════════════════
    "7203.T": "トヨタ自動車",
    "7267.T": "本田技研工業 (ホンダ)",
    "7201.T": "日産自動車",
    "7269.T": "スズキ",
    "7270.T": "SUBARU (スバル)",
    "7261.T": "マツダ",
    "7211.T": "三菱自動車工業",
    "5108.T": "ブリヂストン",
    "7259.T": "アイシン",
    "6902.T": "デンソー",
    "7202.T": "いすゞ自動車",
    "7205.T": "日野自動車",
    "7272.T": "ヤマハ発動機",
    "7276.T": "小糸製作所",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 電機・精密機器
    # ════════════════════════════════════════════════════════
    "6758.T": "ソニーグループ",
    "6501.T": "日立製作所",
    "6752.T": "パナソニック ホールディングス",
    "6503.T": "三菱電機",
    "6702.T": "富士通",
    "6701.T": "NEC",
    "6594.T": "日本電産",
    "6841.T": "横河電機",
    "6857.T": "アドバンテスト",
    "6861.T": "キーエンス",
    "6273.T": "SMC",
    "6954.T": "ファナック",
    "6383.T": "ダイフク",
    "6976.T": "太陽誘電",
    "6963.T": "ローム",
    "6971.T": "京セラ",
    "6762.T": "TDK",
    "6723.T": "ルネサスエレクトロニクス",
    "7731.T": "ニコン",
    "7733.T": "オリンパス",
    "7735.T": "SCREEN ホールディングス",
    "7741.T": "HOYA",
    "7751.T": "キヤノン",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 半導体・電子部品
    # ════════════════════════════════════════════════════════
    "8035.T": "東京エレクトロン",
    "6920.T": "レーザーテック",
    "6146.T": "ディスコ",
    "6981.T": "村田製作所",
    "6971.T": "京セラ",
    "6952.T": "カシオ計算機",
    "6967.T": "新光電気工業",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 情報通信・インターネット
    # ════════════════════════════════════════════════════════
    "9984.T": "ソフトバンクグループ",
    "9432.T": "日本電信電話 (NTT)",
    "9433.T": "KDDI",
    "9434.T": "ソフトバンク",
    "4755.T": "楽天グループ",
    "4689.T": "ヤフー (LINEヤフー)",
    "4704.T": "トレンドマイクロ",
    "3659.T": "ネクソン",
    "9697.T": "カプコン",
    "7974.T": "任天堂",
    "6178.T": "日本郵政",
    "9602.T": "東宝",
    "9735.T": "セコム",
    "9613.T": "NTTデータグループ",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 金融
    # ════════════════════════════════════════════════════════
    "8306.T": "三菱UFJフィナンシャル・グループ",
    "8316.T": "三井住友フィナンシャルグループ",
    "8411.T": "みずほフィナンシャルグループ",
    "8591.T": "オリックス",
    "8604.T": "野村ホールディングス",
    "8601.T": "大和証券グループ本社",
    "7182.T": "ゆうちょ銀行",
    "8750.T": "第一生命ホールディングス",
    "8766.T": "東京海上ホールディングス",
    "8725.T": "MS&ADインシュアランスグループホールディングス",
    "8630.T": "SOMPOホールディングス",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 商社
    # ════════════════════════════════════════════════════════
    "8058.T": "三菱商事",
    "8001.T": "伊藤忠商事",
    "8031.T": "三井物産",
    "8053.T": "住友商事",
    "8002.T": "丸紅",
    "8015.T": "豊田通商",
    "2768.T": "双日",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 医薬品・ヘルスケア
    # ════════════════════════════════════════════════════════
    "4502.T": "武田薬品工業",
    "4503.T": "アステラス製薬",
    "4568.T": "第一三共",
    "4507.T": "塩野義製薬",
    "4523.T": "エーザイ",
    "4519.T": "中外製薬",
    "4541.T": "日医工",
    "7261.T": "マツダ",
    "6869.T": "シスメックス",
    "7453.T": "良品計画",
    "7509.T": "アインホールディングス",
    "4921.T": "ファンケル",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 化学・素材
    # ════════════════════════════════════════════════════════
    "4063.T": "信越化学工業",
    "4005.T": "住友化学",
    "4183.T": "三井化学",
    "4188.T": "三菱ケミカルグループ",
    "4452.T": "花王",
    "3401.T": "帝人",
    "3402.T": "東レ",
    "4151.T": "協和キリン",
    "4911.T": "資生堂",
    "4612.T": "日本ペイントホールディングス",
    "5020.T": "ENEOS ホールディングス",
    "5401.T": "日本製鉄",
    "5411.T": "JFEホールディングス",
    "5714.T": "DOWA ホールディングス",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 食品・飲料
    # ════════════════════════════════════════════════════════
    "2502.T": "アサヒグループホールディングス",
    "2503.T": "キリンホールディングス",
    "2501.T": "サッポロホールディングス",
    "2269.T": "明治ホールディングス",
    "2282.T": "日本ハム",
    "2801.T": "キッコーマン",
    "2802.T": "味の素",
    "2871.T": "ニチレイ",
    "2002.T": "日清製粉グループ本社",
    "2914.T": "日本たばこ産業 (JT)",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 小売・サービス
    # ════════════════════════════════════════════════════════
    "3382.T": "セブン&アイ・ホールディングス",
    "8267.T": "イオン",
    "9983.T": "ファーストリテイリング (ユニクロ)",
    "9843.T": "ニトリホールディングス",
    "3086.T": "J.フロント リテイリング",
    "3099.T": "三越伊勢丹ホールディングス",
    "8279.T": "ヤオコー",
    "2651.T": "ローソン",
    "3048.T": "ビックカメラ",
    "9831.T": "ヤマダホールディングス",
    "9873.T": "日本KFCホールディングス",
    "9861.T": "吉野家ホールディングス",
    "2702.T": "日本マクドナルドホールディングス",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 不動産
    # ════════════════════════════════════════════════════════
    "8801.T": "三井不動産",
    "8802.T": "三菱地所",
    "8830.T": "住友不動産",
    "1928.T": "積水ハウス",
    "1925.T": "大和ハウス工業",
    "1963.T": "日揮ホールディングス",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 運輸・物流
    # ════════════════════════════════════════════════════════
    "9020.T": "東日本旅客鉄道 (JR東日本)",
    "9021.T": "西日本旅客鉄道 (JR西日本)",
    "9022.T": "東海旅客鉄道 (JR東海)",
    "9062.T": "日本通運",
    "9064.T": "ヤマトホールディングス",
    "9101.T": "日本郵船",
    "9107.T": "川崎汽船",
    "9202.T": "ANAホールディングス",
    "9201.T": "日本航空 (JAL)",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - エンターテイメント・レジャー
    # ════════════════════════════════════════════════════════
    "4661.T": "オリエンタルランド (東京ディズニーリゾート)",
    "6098.T": "リクルートホールディングス",
    "9766.T": "コナミグループ",
    "9684.T": "スクウェア・エニックス・ホールディングス",
    "7832.T": "バンダイナムコホールディングス",
    "4324.T": "電通グループ",
    "4324.T": "電通グループ",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 電力・ガス
    # ════════════════════════════════════════════════════════
    "9501.T": "東京電力ホールディングス",
    "9502.T": "中部電力",
    "9503.T": "関西電力",
    "9531.T": "東京ガス",
    "9532.T": "大阪ガス",
    
    # ════════════════════════════════════════════════════════
    # 日本株 - 建設
    # ════════════════════════════════════════════════════════
    "1801.T": "大成建設",
    "1802.T": "大林組",
    "1803.T": "清水建設",
    "1812.T": "鹿島建設",
    "1821.T": "三井住友建設",
    "5201.T": "AGC",
    "5332.T": "TOTO",
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

/* Hide Streamlit branding but keep sidebar toggle */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: transparent;
    backdrop-filter: none;
}
/* Hide deploy button only */
.stDeployButton {display: none;}

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


@st.cache_data(ttl=3600)
def fetch_dividend_history(ticker: str) -> pd.DataFrame:
    """配当履歴を取得"""
    try:
        stock = yf.Ticker(ticker)
        dividends = stock.dividends
        if not dividends.empty:
            df = dividends.to_frame(name="Dividend")
            df.index.name = "Date"
            return df
    except Exception:
        pass
    return pd.DataFrame()


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
# 8.5 ★新機能★ 効率的フロンティア関連の関数
# ============================================================

def calculate_portfolio_performance(weights: np.ndarray, mean_returns: np.ndarray,
                                   cov_matrix: np.ndarray) -> Tuple[float, float]:
    """
    ポートフォリオのリターンとボラティリティを計算
    
    Args:
        weights: 各銘柄の投資比率
        mean_returns: 各銘柄の平均リターン（年率）
        cov_matrix: 共分散行列（年率）
    
    Returns:
        (リターン, ボラティリティ) のタプル
    """
    portfolio_return = np.sum(weights * mean_returns)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return portfolio_return, portfolio_volatility


def negative_sharpe_ratio(weights: np.ndarray, mean_returns: np.ndarray,
                          cov_matrix: np.ndarray, risk_free_rate: float) -> float:
    """
    シャープレシオの負値を返す（最小化のため）
    
    Args:
        weights: 各銘柄の投資比率
        mean_returns: 各銘柄の平均リターン（年率）
        cov_matrix: 共分散行列（年率）
        risk_free_rate: 無リスク金利
    
    Returns:
        -シャープレシオ
    """
    p_return, p_volatility = calculate_portfolio_performance(weights, mean_returns, cov_matrix)
    sharpe = (p_return - risk_free_rate) / p_volatility if p_volatility > 0 else 0
    return -sharpe


def portfolio_variance(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """ポートフォリオの分散を計算"""
    return np.dot(weights.T, np.dot(cov_matrix, weights))


def generate_efficient_frontier_data(portfolio: list, period: str = "1y",
                                    n_portfolios: int = 5000) -> Optional[Dict]:
    """
    効率的フロンティアのデータを生成
    
    Args:
        portfolio: ポートフォリオリスト
        period: データ取得期間
        n_portfolios: ランダムポートフォリオの数
    
    Returns:
        効率的フロンティアのデータ辞書 or None
    """
    if len(portfolio) < 2:
        return None
    
    # 各銘柄の過去データを取得
    tickers = [item["ticker"] for item in portfolio]
    price_data = []
    
    for ticker in tickers:
        data = fetch_stock_data(ticker, period=period)
        if not data.empty:
            price_data.append(data[["Close"]].rename(columns={"Close": ticker}))
    
    if len(price_data) < 2:
        return None
    
    # 価格データを結合
    prices = pd.concat(price_data, axis=1).dropna()
    
    if prices.empty or len(prices) < 20:
        return None
    
    # リターンを計算
    returns = prices.pct_change().dropna()
    
    # 年率換算の平均リターンと共分散行列
    mean_returns = returns.mean() * TRADING_DAYS
    cov_matrix = returns.cov() * TRADING_DAYS
    
    num_assets = len(tickers)
    
    # 現在のポートフォリオの配分を計算
    exchange_rate = get_exchange_rate()
    current_weights = []
    total_value = 0.0
    
    for item in portfolio:
        ticker = item["ticker"]
        info = fetch_stock_info(ticker)
        current_price = info["current_price"]
        if current_price == 0:
            hist = fetch_stock_data(ticker, period="5d")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
        
        is_jpy = ".T" in ticker or ".JP" in ticker
        value = current_price * item["shares"]
        if not is_jpy:
            value *= exchange_rate
        
        total_value += value
    
    for item in portfolio:
        ticker = item["ticker"]
        info = fetch_stock_info(ticker)
        current_price = info["current_price"]
        if current_price == 0:
            hist = fetch_stock_data(ticker, period="5d")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
        
        is_jpy = ".T" in ticker or ".JP" in ticker
        value = current_price * item["shares"]
        if not is_jpy:
            value *= exchange_rate
        
        weight = value / total_value if total_value > 0 else 0
        current_weights.append(weight)
    
    current_weights = np.array(current_weights)
    
    # ランダムポートフォリオを生成
    np.random.seed(42)
    portfolio_returns = []
    portfolio_volatilities = []
    portfolio_weights_list = []
    
    for _ in range(n_portfolios):
        # ランダムな重み（合計1）
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        
        p_return, p_volatility = calculate_portfolio_performance(
            weights, mean_returns.values, cov_matrix.values
        )
        
        portfolio_returns.append(p_return)
        portfolio_volatilities.append(p_volatility)
        portfolio_weights_list.append(weights)
    
    # 最小分散ポートフォリオを計算
    constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for _ in range(num_assets))
    initial_guess = num_assets * [1.0 / num_assets]
    
    min_var_result = minimize(
        portfolio_variance,
        initial_guess,
        args=(cov_matrix.values,),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    
    min_var_weights = min_var_result.x
    min_var_return, min_var_volatility = calculate_portfolio_performance(
        min_var_weights, mean_returns.values, cov_matrix.values
    )
    
    # 最大シャープレシオ・ポートフォリオを計算
    max_sharpe_result = minimize(
        negative_sharpe_ratio,
        initial_guess,
        args=(mean_returns.values, cov_matrix.values, RISK_FREE_RATE),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    
    max_sharpe_weights = max_sharpe_result.x
    max_sharpe_return, max_sharpe_volatility = calculate_portfolio_performance(
        max_sharpe_weights, mean_returns.values, cov_matrix.values
    )
    
    # 現在のポートフォリオのパフォーマンス
    current_return, current_volatility = calculate_portfolio_performance(
        current_weights, mean_returns.values, cov_matrix.values
    )
    
    return {
        "tickers": tickers,
        "random_portfolios": {
            "returns": portfolio_returns,
            "volatilities": portfolio_volatilities,
            "weights": portfolio_weights_list,
        },
        "current_portfolio": {
            "weights": current_weights,
            "return": current_return,
            "volatility": current_volatility,
        },
        "min_variance": {
            "weights": min_var_weights,
            "return": min_var_return,
            "volatility": min_var_volatility,
        },
        "max_sharpe": {
            "weights": max_sharpe_weights,
            "return": max_sharpe_return,
            "volatility": max_sharpe_volatility,
        },
    }


def create_efficient_frontier_chart(frontier_data: Dict) -> go.Figure:
    """
    効率的フロンティアのチャート作成
    
    Args:
        frontier_data: generate_efficient_frontier_data() の戻り値
    
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # ランダムポートフォリオの散布図
    random = frontier_data["random_portfolios"]
    returns = np.array(random["returns"]) * 100
    volatilities = np.array(random["volatilities"]) * 100
    
    # シャープレシオでカラーマップ
    sharpe_ratios = (returns / 100 - RISK_FREE_RATE) / (volatilities / 100)
    
    fig.add_trace(
        go.Scatter(
            x=volatilities,
            y=returns,
            mode="markers",
            marker=dict(
                size=4,
                color=sharpe_ratios,
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(
                    title="Sharpe<br>Ratio",
                    titleside="right",
                    tickmode="linear",
                    tick0=0,
                    dtick=0.5,
                ),
                line=dict(width=0),
            ),
            name="ランダムポートフォリオ",
            hovertemplate="リスク: %{x:.2f}%<br>リターン: %{y:.2f}%<extra></extra>",
        )
    )
    
    # 現在のポートフォリオ
    current = frontier_data["current_portfolio"]
    fig.add_trace(
        go.Scatter(
            x=[current["volatility"] * 100],
            y=[current["return"] * 100],
            mode="markers",
            marker=dict(
                size=20,
                color="#F59E0B",
                symbol="star",
                line=dict(color="#1A1F2E", width=2),
            ),
            name="現在のポートフォリオ",
            hovertemplate="リスク: %{x:.2f}%<br>リターン: %{y:.2f}%<extra></extra>",
        )
    )
    
    # 最小分散ポートフォリオ
    min_var = frontier_data["min_variance"]
    fig.add_trace(
        go.Scatter(
            x=[min_var["volatility"] * 100],
            y=[min_var["return"] * 100],
            mode="markers",
            marker=dict(
                size=18,
                color="#3B82F6",
                symbol="diamond",
                line=dict(color="#1A1F2E", width=2),
            ),
            name="最小分散ポートフォリオ",
            hovertemplate="リスク: %{x:.2f}%<br>リターン: %{y:.2f}%<extra></extra>",
        )
    )
    
    # 最大シャープレシオ・ポートフォリオ
    max_sharpe = frontier_data["max_sharpe"]
    fig.add_trace(
        go.Scatter(
            x=[max_sharpe["volatility"] * 100],
            y=[max_sharpe["return"] * 100],
            mode="markers",
            marker=dict(
                size=18,
                color="#00D4AA",
                symbol="star-triangle-up",
                line=dict(color="#1A1F2E", width=2),
            ),
            name="最大シャープレシオ",
            hovertemplate="リスク: %{x:.2f}%<br>リターン: %{y:.2f}%<extra></extra>",
        )
    )
    
    fig.update_layout(**base_layout(
        xaxis_title="リスク（年率ボラティリティ %）",
        yaxis_title="リターン（年率 %）",
        hovermode="closest",
        height=520,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(26, 31, 46, 0.8)",
            bordercolor="#2A3040",
            borderwidth=1,
        ),
    ))
    
    return fig


# ============================================================
# 8.6 ★新機能★ リバランス関連の関数
# ============================================================

def calculate_rebalance_actions(portfolio: list, target_allocations: Dict[str, float],
                               exchange_rate: float) -> pd.DataFrame:
    """
    リバランスのための売買アクションを計算
    
    Args:
        portfolio: 現在のポートフォリオ
        target_allocations: 目標配分（銘柄: %）
        exchange_rate: 為替レート
    
    Returns:
        売買アクション一覧のDataFrame
    """
    # 現在の総資産価値を計算
    total_value = 0.0
    current_values = {}
    
    for item in portfolio:
        ticker = item["ticker"]
        info = fetch_stock_info(ticker)
        current_price = info["current_price"]
        if current_price == 0:
            hist = fetch_stock_data(ticker, period="5d")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
        
        is_jpy = ".T" in ticker or ".JP" in ticker
        value = current_price * item["shares"]
        if not is_jpy:
            value *= exchange_rate
        
        current_values[ticker] = value
        total_value += value
    
    # リバランスアクションを計算
    actions = []
    
    for ticker, current_value in current_values.items():
        current_pct = (current_value / total_value * 100) if total_value > 0 else 0
        target_pct = target_allocations.get(ticker, 0)
        
        target_value = total_value * (target_pct / 100)
        diff_value = target_value - current_value
        diff_pct = target_pct - current_pct
        
        # 銘柄情報を取得
        item = next((x for x in portfolio if x["ticker"] == ticker), None)
        info = fetch_stock_info(ticker)
        current_price = info["current_price"]
        if current_price == 0:
            hist = fetch_stock_data(ticker, period="5d")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
        
        if abs(diff_value) > 100:  # 100円以上の差がある場合のみ表示
            action = "買い増し" if diff_value > 0 else "売却"
            actions.append({
                "銘柄": ticker,
                "現在配分": f"{current_pct:.2f}%",
                "目標配分": f"{target_pct:.2f}%",
                "差分": f"{diff_pct:+.2f}%",
                "アクション": action,
                "金額": f"¥{abs(diff_value):,.0f}",
                "株数": f"{int(abs(diff_value) / current_price) if current_price > 0 else 0}株",
            })
    
    return pd.DataFrame(actions)


def create_rebalance_comparison_chart(portfolio: list, target_allocations: Dict[str, float],
                                     exchange_rate: float) -> go.Figure:
    """
    現在配分 vs 目標配分の比較チャート
    
    Args:
        portfolio: ポートフォリオリスト
        target_allocations: 目標配分
        exchange_rate: 為替レート
    
    Returns:
        Plotly Figure
    """
    # 現在配分を計算
    total_value = 0.0
    current_allocations = {}
    
    for item in portfolio:
        ticker = item["ticker"]
        info = fetch_stock_info(ticker)
        current_price = info["current_price"]
        if current_price == 0:
            hist = fetch_stock_data(ticker, period="5d")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
        
        is_jpy = ".T" in ticker or ".JP" in ticker
        value = current_price * item["shares"]
        if not is_jpy:
            value *= exchange_rate
        
        current_allocations[ticker] = value
        total_value += value
    
    # パーセントに変換
    tickers = list(current_allocations.keys())
    current_pcts = [current_allocations[t] / total_value * 100 if total_value > 0 else 0
                   for t in tickers]
    target_pcts = [target_allocations.get(t, 0) for t in tickers]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            name="現在の配分",
            x=tickers,
            y=current_pcts,
            marker=dict(color="#3B82F6", line=dict(color="#1A1F2E", width=1)),
            text=[f"{v:.1f}%" for v in current_pcts],
            textposition="outside",
        )
    )
    
    fig.add_trace(
        go.Bar(
            name="目標配分",
            x=tickers,
            y=target_pcts,
            marker=dict(color="#00D4AA", line=dict(color="#1A1F2E", width=1)),
            text=[f"{v:.1f}%" for v in target_pcts],
            textposition="outside",
        )
    )
    
    fig.update_layout(**base_layout(
        barmode="group",
        xaxis_title="銘柄",
        yaxis_title="配分比率 (%)",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    ))
    
    return fig


# ============================================================
# 8.7 ★新機能★ 配当関連の関数
# ============================================================

def aggregate_dividend_by_month(portfolio: list) -> pd.DataFrame:
    """
    月別の配当収入を集計
    
    Args:
        portfolio: ポートフォリオリスト
    
    Returns:
        月別配当収入のDataFrame（銘柄別にカラム分け）
    """
    exchange_rate = get_exchange_rate()
    all_dividends = {}
    
    for item in portfolio:
        ticker = item["ticker"]
        div_history = fetch_dividend_history(ticker)
        
        if not div_history.empty:
            # インデックスをタイムゾーン非依存のdatetimeに変換
            if isinstance(div_history.index, pd.DatetimeIndex):
                # タイムゾーンを削除（UTC正規化）
                div_history.index = div_history.index.tz_localize(None)
            else:
                div_history.index = pd.to_datetime(div_history.index).tz_localize(None)
            
            # 配当金額に保有株数を掛ける
            div_history["Amount"] = div_history["Dividend"] * item["shares"]
            
            # 通貨変換
            is_jpy = ".T" in ticker or ".JP" in ticker
            if not is_jpy:
                div_history["Amount"] *= exchange_rate
            
            # 月次に集計
            monthly = div_history.resample("M")["Amount"].sum()
            
            all_dividends[ticker] = monthly
    
    if not all_dividends:
        return pd.DataFrame()
    
    # 全銘柄の配当を結合
    df = pd.DataFrame(all_dividends).fillna(0)
    df.index = df.index.strftime("%Y-%m")
    
    return df


def calculate_dividend_metrics(portfolio: list) -> pd.DataFrame:
    """
    各銘柄の配当指標を計算
    
    Args:
        portfolio: ポートフォリオリスト
    
    Returns:
        配当指標一覧のDataFrame
    """
    metrics_list = []
    exchange_rate = get_exchange_rate()
    
    for item in portfolio:
        ticker = item["ticker"]
        
        # 基本情報
        info = fetch_stock_info(ticker)
        current_price = info["current_price"]
        if current_price == 0:
            hist = fetch_stock_data(ticker, period="5d")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
        
        # 配当履歴
        div_history = fetch_dividend_history(ticker)
        
        if not div_history.empty:
            # インデックスをタイムゾーン非依存のdatetimeに変換
            if isinstance(div_history.index, pd.DatetimeIndex):
                # タイムゾーンを削除（UTC正規化）
                div_history.index = div_history.index.tz_localize(None)
            else:
                div_history.index = pd.to_datetime(div_history.index).tz_localize(None)
            
            # 年間配当金（過去1年分）- タイムゾーン非依存
            one_year_ago = pd.Timestamp(datetime.now()).tz_localize(None) - pd.Timedelta(days=365)
            recent_divs = div_history[div_history.index > one_year_ago]
            annual_dividend = recent_divs["Dividend"].sum() if not recent_divs.empty else 0
            
            # 配当頻度（年間支払い回数）
            frequency = len(recent_divs)
            
            # 配当利回り（現在価格ベース）
            dividend_yield = (annual_dividend / current_price * 100) if current_price > 0 else 0
            
            # 増配傾向の分析（過去3年）
            three_years_ago = pd.Timestamp(datetime.now()).tz_localize(None) - pd.Timedelta(days=3*365)
            recent_divs_3y = div_history[div_history.index > three_years_ago]["Dividend"]
            
            if len(recent_divs_3y) >= 2:
                trend = "増配" if recent_divs_3y.iloc[-1] > recent_divs_3y.iloc[0] else "減配"
            else:
                trend = "不明"
            
            # 年間受取額（保有株数ベース）
            annual_income = annual_dividend * item["shares"]
            is_jpy = ".T" in ticker or ".JP" in ticker
            if not is_jpy:
                annual_income *= exchange_rate
            
            metrics_list.append({
                "銘柄": ticker,
                "配当利回り": f"{dividend_yield:.2f}%",
                "年間配当": f"¥{annual_income:,.0f}",
                "支払頻度": f"年{frequency}回",
                "傾向": trend,
            })
    
    return pd.DataFrame(metrics_list)


def create_dividend_calendar_chart(monthly_dividends: pd.DataFrame) -> go.Figure:
    """
    月別配当収入のスタック棒グラフ
    
    Args:
        monthly_dividends: aggregate_dividend_by_month() の戻り値
    
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    colors = ["#00D4AA", "#3B82F6", "#8B5CF6", "#F59E0B", "#FF4B6E",
              "#06B6D4", "#EC4899", "#84CC16", "#F97316", "#6366F1"]
    
    for i, ticker in enumerate(monthly_dividends.columns):
        fig.add_trace(
            go.Bar(
                name=ticker,
                x=monthly_dividends.index,
                y=monthly_dividends[ticker],
                marker=dict(
                    color=colors[i % len(colors)],
                    line=dict(color="#1A1F2E", width=1),
                ),
                hovertemplate=f"<b>{ticker}</b><br>月: %{{x}}<br>配当: ¥%{{y:,.0f}}<extra></extra>",
            )
        )
    
    fig.update_layout(**base_layout(
        barmode="stack",
        xaxis_title="月",
        yaxis_title="配当収入 (¥)",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            tickangle=-45,
            gridcolor="#2A3040",
        ),
    ))
    
    return fig


def create_annual_dividend_chart(monthly_dividends: pd.DataFrame) -> go.Figure:
    """
    年間配当収入の推移チャート
    
    Args:
        monthly_dividends: aggregate_dividend_by_month() の戻り値
    
    Returns:
        Plotly Figure
    """
    if monthly_dividends.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="配当データが不足しています",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="#8B95A5"),
        )
        fig.update_layout(**base_layout())
        return fig
    
    # 年次に集計
    monthly_dividends_copy = monthly_dividends.copy()
    monthly_dividends_copy.index = pd.to_datetime(monthly_dividends_copy.index)
    annual_total = monthly_dividends_copy.resample("Y").sum().sum(axis=1)
    
    years = annual_total.index.year
    amounts = annual_total.values
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=years,
            y=amounts,
            mode="lines+markers",
            line=dict(color="#00D4AA", width=3),
            marker=dict(size=10, color="#00D4AA", line=dict(color="#1A1F2E", width=2)),
            fill="tozeroy",
            fillcolor="rgba(0, 212, 170, 0.1)",
            hovertemplate="年: %{x}<br>配当収入: ¥%{y:,.0f}<extra></extra>",
        )
    )
    
    fig.update_layout(**base_layout(
        xaxis_title="年",
        yaxis_title="年間配当収入 (¥)",
        hovermode="x unified",
        height=350,
        xaxis=dict(
            dtick=1,
            gridcolor="#2A3040",
        ),
    ))
    
    return fig


# ============================================================
# 8.8 ★新機能★ 注目株スキャン関連の関数
# ============================================================

def get_sector_for_ticker(ticker: str) -> str:
    """ティッカーからセクターを推定"""
    # テクノロジー
    tech_tickers = {"AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "AMD", "INTC", 
                   "AVGO", "ORCL", "ADBE", "CRM", "CSCO", "ACN", "IBM", "QCOM", "TXN", 
                   "AMAT", "MU", "LRCX", "KLAC", "SNPS", "CDNS", "MRVL", "NXPI", "SHOP", 
                   "PYPL", "SNOW", "PLTR", "CRWD", "NET", "DDOG", "ZS", "OKTA", "TEAM", 
                   "NOW", "WDAY", "PANW", "FTNT", "6758.T", "6501.T", "6752.T", "6503.T", 
                   "6702.T", "6701.T", "6594.T", "6841.T", "6857.T", "6861.T", "8035.T", 
                   "6920.T", "6146.T", "6981.T", "6723.T"}
    
    # 金融
    finance_tickers = {"JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "SCHW", "AXP", "V", "MA", 
                      "COIN", "SOFI", "HOOD", "AFRM", "USB", "PNC", "TFC", "COF", "BK", "STT", 
                      "AIG", "MET", "PRU", "ALL", "PGR", "TRV", "CB", "8306.T", "8316.T", 
                      "8411.T", "8591.T", "8604.T", "8601.T", "7182.T", "8750.T", "8766.T", 
                      "8725.T", "8630.T"}
    
    # ヘルスケア
    healthcare_tickers = {"JNJ", "UNH", "PFE", "ABBV", "LLY", "MRK", "TMO", "ABT", "DHR", "BMY", 
                         "AMGN", "GILD", "CVS", "CI", "ISRG", "REGN", "VRTX", "SYK", "BSX", 
                         "MDT", "ELV", "BIIB", "MRNA", "ZTS", "HCA", "IDXX", "IQV", "A", "BAX", 
                         "BDX", "4502.T", "4503.T", "4568.T", "4507.T", "4523.T", "4519.T"}
    
    # エネルギー
    energy_tickers = {"XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL", 
                     "BKR", "KMI", "WMB", "OKE", "LNG", "FANG", "DVN", "HES", "MRO", "APA", 
                     "5020.T", "5401.T", "5411.T"}
    
    # 消費財
    consumer_tickers = {"WMT", "HD", "COST", "MCD", "NKE", "SBUX", "TGT", "LOW", "TJX", "BKNG", 
                       "ABNB", "MAR", "HLT", "YUM", "CMG", "ROST", "DG", "DLTR", "BBY", "EBAY", 
                       "ETSY", "W", "CHWY", "LULU", "DECK", "ULTA", "EL", "CL", "PG", "KO", 
                       "PEP", "MDLZ", "KHC", "GIS", "K", "HSY", "3382.T", "8267.T", "9983.T", 
                       "9843.T", "2502.T", "2503.T", "2914.T"}
    
    # 自動車・輸送
    auto_tickers = {"TSLA", "7203.T", "7267.T", "7201.T", "7269.T", "7270.T", "7261.T", "7211.T", 
                   "5108.T", "7259.T", "6902.T", "BA", "LUV", "DAL", "UAL", "AAL", "ALK", 
                   "9020.T", "9021.T", "9022.T", "9062.T", "9064.T", "9202.T", "9201.T"}
    
    # 通信・メディア
    comm_tickers = {"NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR", "EA", "TTWO", "RBLX", 
                   "U", "SPOT", "PINS", "SNAP", "MTCH", "WBD", "9984.T", "9432.T", "9433.T", 
                   "9434.T", "4755.T", "4689.T", "7974.T"}
    
    # 産業
    industrial_tickers = {"GE", "CAT", "HON", "UPS", "RTX", "LMT", "DE", "MMM", "GD", "NOC", 
                         "EMR", "ETN", "ITW", "PH", "CMI", "PCAR", "ROK", "FDX", "NSC", "UNP", 
                         "CSX", "1801.T", "1802.T", "1803.T", "1812.T"}
    
    # 不動産
    reit_tickers = {"AMT", "PLD", "CCI", "EQIX", "PSA", "WELL", "DLR", "O", "SBAC", "AVB", 
                   "EQR", "VTR", "SPG", "ARE", "8801.T", "8802.T", "8830.T", "1928.T", "1925.T"}
    
    # 素材・化学
    materials_tickers = {"LIN", "APD", "SHW", "ECL", "DD", "DOW", "NEM", "FCX", "NUE", "STLD", 
                        "VMC", "MLM", "4063.T", "4005.T", "4183.T", "4188.T", "4452.T", "3401.T"}
    
    # セクター判定
    if ticker in tech_tickers:
        return "テクノロジー"
    elif ticker in finance_tickers:
        return "金融"
    elif ticker in healthcare_tickers:
        return "ヘルスケア"
    elif ticker in energy_tickers:
        return "エネルギー"
    elif ticker in consumer_tickers:
        return "消費財・小売"
    elif ticker in auto_tickers:
        return "自動車・輸送"
    elif ticker in comm_tickers:
        return "通信・メディア"
    elif ticker in industrial_tickers:
        return "産業・製造"
    elif ticker in reit_tickers:
        return "不動産"
    elif ticker in materials_tickers:
        return "素材・化学"
    else:
        return "その他"


def scan_trending_stocks(num_stocks: int = 100) -> pd.DataFrame:
    """
    TICKER_CATALOGから注目株をスキャン（直近3日間の値動き）
    
    Args:
        num_stocks: スキャンする銘柄数
    
    Returns:
        トレンド銘柄のDataFrame
    """
    results = []
    
    # TICKER_CATALOGからランダムにサンプリング（計算時間短縮のため）
    all_tickers = list(TICKER_CATALOG.keys())
    
    # ETFを除外（個別株のみ）
    non_etf_tickers = [t for t in all_tickers if not any(
        etf in t for etf in ["SPY", "VOO", "QQQ", "VTI", "DIA", "IWM", "VTV", "VUG", 
                             "VIG", "SCHD", "VYM", "XL", "ARK", "VGT", "VDE", "VFH", 
                             "VHT", "VNQ", "SOXX", "SMH", "IBB", "XBI", "FINX", "HACK", 
                             "BOTZ", "LIT", "TAN", "ICLN", "JETS", "XRT", "ITB", "GDX", 
                             "SLV", "GLD", "USO", "UNG", "TLT", "AGG", "BND", "LQD", 
                             "HYG", "EMB", "VEA", "VWO", "IEMG", "EFA", "EEM", "FXI", 
                             "EWJ", "EWZ", "EWG", "EWU"]
    )]
    
    # サンプリング
    import random
    random.seed(42)
    sample_tickers = random.sample(non_etf_tickers, min(num_stocks, len(non_etf_tickers)))
    
    for ticker in sample_tickers:
        try:
            # 過去5日分のデータを取得（3日間の変動を計算）
            hist = fetch_stock_data(ticker, period="5d")
            
            if hist.empty or len(hist) < 4:
                continue
            
            # 3日前と現在の価格
            price_3d_ago = float(hist["Close"].iloc[0])
            current_price = float(hist["Close"].iloc[-1])
            
            if price_3d_ago == 0:
                continue
            
            # 3日間のリターン
            return_3d = (current_price - price_3d_ago) / price_3d_ago * 100
            
            # ボラティリティ（標準偏差）
            returns = hist["Close"].pct_change().dropna()
            volatility = returns.std() * 100 if len(returns) > 0 else 0
            
            # 出来高の変化（直近vs平均）
            volume_avg = hist["Volume"].mean()
            volume_recent = hist["Volume"].iloc[-1]
            volume_ratio = (volume_recent / volume_avg) if volume_avg > 0 else 0
            
            # セクター判定
            sector = get_sector_for_ticker(ticker)
            
            # 銘柄名
            name = TICKER_CATALOG.get(ticker, ticker)
            
            results.append({
                "ticker": ticker,
                "name": name,
                "sector": sector,
                "return_3d": return_3d,
                "volatility": volatility,
                "current_price": current_price,
                "volume_ratio": volume_ratio,
            })
            
        except Exception:
            continue
    
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    
    # 絶対リターンでソート（上昇・下落両方を含む）
    df["abs_return"] = df["return_3d"].abs()
    df = df.sort_values("abs_return", ascending=False)
    
    return df


def create_trending_stocks_chart(df: pd.DataFrame, sector: str = None, 
                                 top_n: int = 20) -> go.Figure:
    """
    注目株のチャート作成
    
    Args:
        df: scan_trending_stocks() の戻り値
        sector: フィルターするセクター（Noneの場合は全セクター）
        top_n: 表示する銘柄数
    
    Returns:
        Plotly Figure
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="データが見つかりませんでした",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="#8B95A5"),
        )
        fig.update_layout(**base_layout())
        return fig
    
    # セクターでフィルター
    if sector:
        df = df[df["sector"] == sector].copy()
    
    # 上位N件
    df = df.head(top_n).copy()
    
    # 色分け（上昇=緑、下落=赤）
    colors = ["#00D4AA" if r > 0 else "#FF4B6E" for r in df["return_3d"]]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=df["return_3d"],
            y=df["ticker"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="#1A1F2E", width=1),
            ),
            text=[f"{r:+.2f}%" for r in df["return_3d"]],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "3日間リターン: %{x:.2f}%<br>"
                "<extra></extra>"
            ),
        )
    )
    
    fig.update_layout(**base_layout(
        xaxis_title="3日間リターン (%)",
        yaxis_title="",
        height=max(400, top_n * 25),
        yaxis=dict(
            autorange="reversed",
            gridcolor="#2A3040",
        ),
        xaxis=dict(
            gridcolor="#2A3040",
            zeroline=True,
            zerolinecolor="#8B95A5",
            zerolinewidth=2,
        ),
    ))
    
    return fig


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

            # 株数入力
            shares = st.number_input("保有株数", min_value=0.0, value=0.0, step=1.0)
            
            # 入力方法の選択
            st.markdown("##### 📊 取得価格の入力方法")
            input_method = st.radio(
                "入力方法を選択",
                ["取得単価を入力", "現在の評価額を入力"],
                horizontal=True,
                help="取得単価がわからない場合は、現在の評価額から自動計算します。",
            )
            
            col1, col2 = st.columns(2)
            
            if input_method == "取得単価を入力":
                with col1:
                    cost_price = st.number_input(
                        "取得単価（1株あたり）", 
                        min_value=0.0, 
                        value=0.0, 
                        step=0.01,
                        help="購入時の1株あたりの価格",
                    )
                with col2:
                    st.caption("")  # スペーサー
                    st.caption("")  # スペーサー
                    if cost_price > 0 and shares > 0:
                        total_cost = cost_price * shares
                        st.metric("取得総額", f"¥{total_cost:,.0f}")
                    
                current_value_input = None
                
            else:  # 現在の評価額を入力
                with col1:
                    current_value_input = st.number_input(
                        "現在の評価額（総額）", 
                        min_value=0.0, 
                        value=0.0, 
                        step=100.0,
                        help="現在この銘柄が何円分になっているか",
                    )
                with col2:
                    st.caption("")  # スペーサー
                    st.caption("")  # スペーサー
                    if current_value_input > 0 and shares > 0:
                        implied_price = current_value_input / shares
                        st.metric("推定取得単価", f"¥{implied_price:,.2f}")
                
                cost_price = None
            
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

                if ticker and shares > 0:
                    # 取得単価の計算
                    if input_method == "取得単価を入力":
                        if cost_price <= 0:
                            st.error("取得単価を入力してください")
                            st.stop()
                        final_cost_price = cost_price
                    else:  # 現在の評価額から逆算
                        if current_value_input <= 0:
                            st.error("現在の評価額を入力してください")
                            st.stop()
                        
                        # 現在価格を取得
                        with st.spinner(f"{ticker} の現在価格を取得中..."):
                            info = fetch_stock_info(ticker)
                            current_price = info["current_price"]
                            
                            if current_price == 0:
                                hist = fetch_stock_data(ticker, period="5d")
                                if not hist.empty:
                                    current_price = float(hist["Close"].iloc[-1])
                            
                            if current_price == 0:
                                st.error(f"{ticker} の現在価格を取得できませんでした")
                                st.stop()
                        
                        # 取得単価を逆算
                        # 現在の評価額 = 現在価格 × 株数
                        # 取得単価 = 現在価格 × (現在の評価額 / (現在価格 × 株数))
                        actual_current_value = current_price * shares
                        final_cost_price = current_price * (current_value_input / actual_current_value)
                    
                    st.session_state["portfolio"].append({
                        "ticker": ticker,
                        "shares": shares,
                        "cost_price": final_cost_price,
                        "buy_date": str(buy_date),
                    })
                    st.success(f"✅ {ticker} を追加しました！")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("ティッカーと株数を正しく入力してください")

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

    # ─── タブ（7つに拡張：注目の株タブを追加） ───
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["📋 概要", "📈 チャート", "🔬 分析", "🏢 個別銘柄", "🔮 シミュレーション", "💰 配当", "🔥 注目の株"]
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
            
            st.markdown("---")

            # ============================================================
            # ★新機能★ リバランス分析
            # ============================================================
            st.markdown(
                '<div class="section-header">🔄 リバランス分析</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "目標とする資産配分を設定して、現在のポートフォリオとの差分を確認できます。"
            )

            st.markdown("##### 目標配分の設定")
            st.caption("各銘柄の目標配分（%）を入力してください（合計100%）")

            target_allocations = {}
            
            # 3列レイアウトで目標配分を入力
            num_tickers = len(portfolio)
            cols_per_row = 3
            num_rows = (num_tickers + cols_per_row - 1) // cols_per_row
            
            for row in range(num_rows):
                cols = st.columns(cols_per_row)
                for col_idx in range(cols_per_row):
                    ticker_idx = row * cols_per_row + col_idx
                    if ticker_idx < num_tickers:
                        ticker = portfolio[ticker_idx]["ticker"]
                        with cols[col_idx]:
                            target_pct = st.number_input(
                                f"{ticker}",
                                min_value=0.0,
                                max_value=100.0,
                                value=100.0 / num_tickers,
                                step=1.0,
                                key=f"target_{ticker}",
                                format="%.1f",
                            )
                            target_allocations[ticker] = target_pct

            total_target = sum(target_allocations.values())
            
            if abs(total_target - 100.0) > 0.1:
                st.warning(f"⚠️ 目標配分の合計が{total_target:.1f}%です。100%に調整してください。")
            else:
                st.success(f"✅ 目標配分の合計: {total_target:.1f}%")

                # 比較チャート
                st.markdown("##### 現在配分 vs 目標配分")
                st.plotly_chart(
                    create_rebalance_comparison_chart(
                        portfolio, target_allocations, exchange_rate
                    ),
                    use_container_width=True,
                )

                # 売買アクション
                st.markdown("##### 推奨売買アクション")
                actions_df = calculate_rebalance_actions(
                    portfolio, target_allocations, exchange_rate
                )

                if not actions_df.empty:
                    st.dataframe(actions_df, use_container_width=True, hide_index=True)
                else:
                    st.info("リバランスの必要はありません（目標配分と現在配分が一致しています）")

            st.markdown("---")

            # ============================================================
            # ★新機能★ 効率的フロンティア
            # ============================================================
            st.markdown(
                '<div class="section-header">📊 効率的フロンティア（Modern Portfolio Theory）</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "リスク（ボラティリティ）とリターンの関係を可視化し、"
                "最適なポートフォリオ配分を探索します。"
            )

            if len(portfolio) < 2:
                st.info("効率的フロンティアの分析には2銘柄以上が必要です。")
            else:
                with st.spinner("効率的フロンティアを計算中..."):
                    frontier_data = generate_efficient_frontier_data(
                        portfolio, period="1y", n_portfolios=3000
                    )

                if frontier_data:
                    # チャート表示
                    st.plotly_chart(
                        create_efficient_frontier_chart(frontier_data),
                        use_container_width=True,
                    )

                    # 推奨配分の比較テーブル
                    st.markdown("##### 最適ポートフォリオ配分の比較")

                    tickers = frontier_data["tickers"]
                    current_weights = frontier_data["current_portfolio"]["weights"]
                    min_var_weights = frontier_data["min_variance"]["weights"]
                    max_sharpe_weights = frontier_data["max_sharpe"]["weights"]

                    comparison_df = pd.DataFrame(
                        {
                            "銘柄": tickers,
                            "現在の配分": [f"{w*100:.1f}%" for w in current_weights],
                            "最小分散": [f"{w*100:.1f}%" for w in min_var_weights],
                            "最大シャープレシオ": [f"{w*100:.1f}%" for w in max_sharpe_weights],
                        }
                    )

                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

                    # パフォーマンスサマリー
                    st.markdown("##### パフォーマンスサマリー")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**現在のポートフォリオ**")
                        st.metric(
                            "年率リターン",
                            f"{frontier_data['current_portfolio']['return']*100:.2f}%",
                        )
                        st.metric(
                            "年率リスク",
                            f"{frontier_data['current_portfolio']['volatility']*100:.2f}%",
                        )
                        sharpe = (
                            (frontier_data['current_portfolio']['return'] - RISK_FREE_RATE)
                            / frontier_data['current_portfolio']['volatility']
                        )
                        st.metric("シャープレシオ", f"{sharpe:.3f}")

                    with col2:
                        st.markdown("**最小分散ポートフォリオ**")
                        st.metric(
                            "年率リターン",
                            f"{frontier_data['min_variance']['return']*100:.2f}%",
                        )
                        st.metric(
                            "年率リスク",
                            f"{frontier_data['min_variance']['volatility']*100:.2f}%",
                        )
                        sharpe = (
                            (frontier_data['min_variance']['return'] - RISK_FREE_RATE)
                            / frontier_data['min_variance']['volatility']
                        )
                        st.metric("シャープレシオ", f"{sharpe:.3f}")

                    with col3:
                        st.markdown("**最大シャープレシオ**")
                        st.metric(
                            "年率リターン",
                            f"{frontier_data['max_sharpe']['return']*100:.2f}%",
                        )
                        st.metric(
                            "年率リスク",
                            f"{frontier_data['max_sharpe']['volatility']*100:.2f}%",
                        )
                        sharpe = (
                            (frontier_data['max_sharpe']['return'] - RISK_FREE_RATE)
                            / frontier_data['max_sharpe']['volatility']
                        )
                        st.metric("シャープレシオ", f"{sharpe:.3f}")

                else:
                    st.info("効率的フロンティアの計算に必要なデータが不足しています。")
                    
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
    # ★新機能★ タブ6: 配当分析
    # ============================================================
    with tab6:
        st.markdown(
            '<div class="section-header">💰 配当カレンダー & 配当追跡</div>',
            unsafe_allow_html=True,
        )
        st.caption("保有銘柄からの配当収入を可視化し、配当戦略を最適化します。")

        # 月別配当収入の集計
        with st.spinner("配当データを取得中..."):
            monthly_dividends = aggregate_dividend_by_month(portfolio)

        if not monthly_dividends.empty:
            # 月別配当カレンダー
            st.markdown("##### 月別配当収入（過去実績）")
            st.plotly_chart(
                create_dividend_calendar_chart(monthly_dividends),
                use_container_width=True,
            )

            # 年間配当推移
            st.markdown("##### 年間配当収入の推移")
            st.plotly_chart(
                create_annual_dividend_chart(monthly_dividends),
                use_container_width=True,
            )

            # 配当サマリーKPI
            st.markdown("##### 配当サマリー")
            
            # 総配当収入を計算
            total_dividends = monthly_dividends.sum().sum()
            annual_average = total_dividends / max(1, len(monthly_dividends) / 12)
            
            # 最も配当が多かった月
            monthly_totals = monthly_dividends.sum(axis=1)
            if not monthly_totals.empty:
                best_month = monthly_totals.idxmax()
                best_month_amount = monthly_totals.max()
            else:
                best_month = "N/A"
                best_month_amount = 0

            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(
                    kpi_card(
                        "累積配当収入",
                        format_jpy(total_dividends),
                        "全期間合計",
                    ),
                    unsafe_allow_html=True,
                )
            
            with col2:
                st.markdown(
                    kpi_card(
                        "年間配当（推定）",
                        format_jpy(annual_average),
                        "平均値",
                    ),
                    unsafe_allow_html=True,
                )
            
            with col3:
                st.markdown(
                    kpi_card(
                        "最高月間配当",
                        format_jpy(best_month_amount),
                        f"{best_month}",
                    ),
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # 配当指標テーブル
            st.markdown("##### 銘柄別配当指標")
            dividend_metrics = calculate_dividend_metrics(portfolio)
            
            if not dividend_metrics.empty:
                st.dataframe(dividend_metrics, use_container_width=True, hide_index=True)

                # 配当利回りランキング
                st.markdown("##### 配当利回りランキング（保有銘柄内）")
                
                # 配当利回りでソート
                ranking_df = dividend_metrics.copy()
                ranking_df["配当利回り_数値"] = ranking_df["配当利回り"].str.replace("%", "").astype(float)
                ranking_df = ranking_df.sort_values("配当利回り_数値", ascending=False)
                ranking_df = ranking_df.drop(columns=["配当利回り_数値"])
                
                # 上位3銘柄をKPIカード形式で表示
                if len(ranking_df) >= 3:
                    col1, col2, col3 = st.columns(3)
                    
                    for idx, (col, rank) in enumerate(zip([col1, col2, col3], [1, 2, 3])):
                        if idx < len(ranking_df):
                            row = ranking_df.iloc[idx]
                            with col:
                                st.markdown(
                                    kpi_card(
                                        f"#{rank} {row['銘柄']}",
                                        row["配当利回り"],
                                        f"{row['年間配当']} / 年",
                                    ),
                                    unsafe_allow_html=True,
                                )
                elif len(ranking_df) > 0:
                    st.dataframe(ranking_df, use_container_width=True, hide_index=True)

            else:
                st.info("配当データが見つかりませんでした。")

        else:
            st.info(
                "配当データが見つかりませんでした。保有銘柄に配当支払い実績がない可能性があります。"
            )

    # ============================================================
    # ★新機能★ タブ7: 注目の株（トレンドスキャン）
    # ============================================================
    with tab7:
        st.markdown(
            '<div class="section-header">🔥 注目の株 - 直近3日間の値動きランキング</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "主要銘柄の中から、直近3日間で大きく値動きしている注目株を業界別にスキャンします。"
            "上昇・下落の両方を含む「話題の銘柄」を発見できます。"
        )
        
        # スキャン実行ボタン
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 「スキャン開始」ボタンをクリックして、最新の注目株を取得してください。")
        with col2:
            scan_button = st.button("🔍 スキャン開始", use_container_width=True, type="primary")
        
        if scan_button or "trending_stocks_data" in st.session_state:
            if scan_button:
                with st.spinner("主要銘柄をスキャン中...（100銘柄を分析します）"):
                    trending_df = scan_trending_stocks(num_stocks=100)
                    st.session_state["trending_stocks_data"] = trending_df
                    st.session_state["trending_scan_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            trending_df = st.session_state.get("trending_stocks_data", pd.DataFrame())
            scan_time = st.session_state.get("trending_scan_time", "")
            
            if not trending_df.empty:
                st.success(f"✅ スキャン完了！ {len(trending_df)}銘柄のデータを取得しました（{scan_time}）")
                
                # セクター別フィルター
                st.markdown("##### 業界別フィルター")
                sectors = ["全業界"] + sorted(trending_df["sector"].unique().tolist())
                selected_sector = st.selectbox(
                    "業界を選択",
                    sectors,
                    key="trending_sector_filter",
                )
                
                # 表示件数
                col1, col2 = st.columns(2)
                with col1:
                    show_count = st.slider(
                        "表示件数",
                        min_value=5,
                        max_value=50,
                        value=20,
                        step=5,
                        key="trending_show_count",
                    )
                
                with col2:
                    sort_option = st.radio(
                        "ソート順",
                        ["上昇率順", "下落率順", "値動き大きい順"],
                        horizontal=True,
                        key="trending_sort_option",
                    )
                
                # データのフィルタリングとソート
                filtered_df = trending_df.copy()
                
                if selected_sector != "全業界":
                    filtered_df = filtered_df[filtered_df["sector"] == selected_sector]
                
                if sort_option == "上昇率順":
                    filtered_df = filtered_df.sort_values("return_3d", ascending=False)
                elif sort_option == "下落率順":
                    filtered_df = filtered_df.sort_values("return_3d", ascending=True)
                else:  # 値動き大きい順
                    filtered_df = filtered_df.sort_values("abs_return", ascending=False)
                
                filtered_df = filtered_df.head(show_count)
                
                # チャート表示
                st.markdown("##### ランキングチャート")
                st.plotly_chart(
                    create_trending_stocks_chart(
                        filtered_df,
                        sector=None,
                        top_n=show_count,
                    ),
                    use_container_width=True,
                )
                
                # トップ3をKPIカード表示
                st.markdown("##### 注目トップ3")
                
                if len(filtered_df) >= 3:
                    top3 = filtered_df.head(3)
                    col1, col2, col3 = st.columns(3)
                    
                    for idx, (col, rank) in enumerate(zip([col1, col2, col3], [1, 2, 3])):
                        if idx < len(top3):
                            row = top3.iloc[idx]
                            is_loss = row["return_3d"] < 0
                            
                            with col:
                                st.markdown(
                                    kpi_card(
                                        f"#{rank} {row['ticker']}",
                                        row["name"],
                                        f"3日間: {row['return_3d']:+.2f}%",
                                        is_loss=is_loss,
                                    ),
                                    unsafe_allow_html=True,
                                )
                
                # 詳細テーブル
                st.markdown("##### 詳細データ")
                
                display_df = filtered_df[[
                    "ticker", "name", "sector", "return_3d", "current_price", 
                    "volatility", "volume_ratio"
                ]].copy()
                
                display_df.columns = [
                    "ティッカー", "銘柄名", "業界", "3日間リターン(%)", 
                    "現在価格", "ボラティリティ(%)", "出来高比率"
                ]
                
                # フォーマット
                display_df["3日間リターン(%)"] = display_df["3日間リターン(%)"].apply(
                    lambda x: f"{x:+.2f}%"
                )
                display_df["現在価格"] = display_df["現在価格"].apply(
                    lambda x: f"{x:,.2f}"
                )
                display_df["ボラティリティ(%)"] = display_df["ボラティリティ(%)"].apply(
                    lambda x: f"{x:.2f}%"
                )
                display_df["出来高比率"] = display_df["出来高比率"].apply(
                    lambda x: f"{x:.2f}x"
                )
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # 業界別サマリー
                st.markdown("##### 業界別サマリー")
                
                sector_summary = trending_df.groupby("sector").agg({
                    "return_3d": ["mean", "max", "min", "count"]
                }).round(2)
                
                sector_summary.columns = ["平均リターン(%)", "最高リターン(%)", "最低リターン(%)", "銘柄数"]
                sector_summary = sector_summary.sort_values("平均リターン(%)", ascending=False)
                
                st.dataframe(sector_summary, use_container_width=True)
                
            else:
                st.warning("データの取得に失敗しました。もう一度スキャンしてください。")


# ============================================================
# 12. main
# ============================================================

def main():
    inject_css()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
