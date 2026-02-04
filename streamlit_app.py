"""
Situational Awareness LP - Portfolio Performance Tracker
Streamlit version
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from scipy.stats import norm
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xml.etree.ElementTree as ET
import json
import re

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="SA LP Portfolio Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONSTANTS & DATA
# ============================================
SEC_CIK = "0002045724"

# Default holdings data (will be overridden by fetched data if available)
DEFAULT_HOLDINGS_DATA = {
    'Q4-2024': {
        'reportDate': '2024-12-31',
        'filedDate': '2025-02-11',
        'periodStart': '2024-10-01',
        'periodEnd': '2024-12-31',
        'holdings': [
            {'ticker': 'MRVL', 'name': 'Marvell Technology Inc', 'shares': 785896, 'value': 86802213, 'type': 'stock'},
            {'ticker': 'VST', 'name': 'Vistra Corp', 'shares': 428397, 'value': 59063094, 'type': 'stock'},
            {'ticker': 'VRT', 'name': 'Vertiv Holdings Co', 'shares': 455146, 'value': 51709137, 'type': 'stock'},
            {'ticker': 'TLN', 'name': 'Talen Energy Corp', 'shares': 138878, 'value': 27979751, 'type': 'stock'},
            {'ticker': 'CEG', 'name': 'Constellation Energy Corp', 'shares': 96400, 'value': 21565644, 'type': 'stock'},
            {'ticker': 'MOD', 'name': 'Modine Mfg Co', 'shares': 66367, 'value': 7693926, 'type': 'stock'},
        ]
    },
    'Q1-2025': {
        'reportDate': '2025-03-31',
        'filedDate': '2025-05-14',
        'periodStart': '2025-01-01',
        'periodEnd': '2025-03-31',
        'holdings': [
            {'ticker': 'INTC', 'name': 'Intel Corp', 'shares': 20237400, 'value': 459591354, 'type': 'call'},
            {'ticker': 'AVGO', 'name': 'Broadcom Inc', 'shares': 700000, 'value': 117201000, 'type': 'stock'},
            {'ticker': 'ONTO', 'name': 'Onto Innovation Inc', 'shares': 586717, 'value': 71192241, 'type': 'stock'},
            {'ticker': 'VST', 'name': 'Vistra Corp', 'shares': 525846, 'value': 61755354, 'type': 'stock'},
            {'ticker': 'MOD', 'name': 'Modine Mfg Co', 'shares': 716824, 'value': 55016242, 'type': 'stock'},
            {'ticker': 'EQT', 'name': 'EQT Corp', 'shares': 989398, 'value': 52863535, 'type': 'stock'},
            {'ticker': 'CRWV', 'name': 'CoreWeave Inc', 'shares': 1225000, 'value': 45423000, 'type': 'stock'},
            {'ticker': 'CEG', 'name': 'Constellation Energy Corp', 'shares': 183400, 'value': 36978942, 'type': 'stock'},
            {'ticker': 'CORZ', 'name': 'Core Scientific Inc', 'shares': 4521578, 'value': 32736225, 'type': 'stock'},
            {'ticker': 'TLN', 'name': 'Talen Energy Corp', 'shares': 148395, 'value': 29630030, 'type': 'stock'},
            {'ticker': 'APLD', 'name': 'Applied Digital Corp', 'shares': 4035600, 'value': 22680072, 'type': 'stock'},
            {'ticker': 'IREN', 'name': 'IREN Limited', 'shares': 3366130, 'value': 20499732, 'type': 'stock'},
        ]
    },
    'Q2-2025': {
        'reportDate': '2025-06-30',
        'filedDate': '2025-08-14',
        'periodStart': '2025-04-01',
        'periodEnd': '2025-06-30',
        'holdings': [
            {'ticker': 'SMH', 'name': 'VanEck Semiconductor ETF', 'shares': 2044100, 'value': 570058608, 'type': 'put'},
            {'ticker': 'INTC', 'name': 'Intel Corp', 'shares': 20237400, 'value': 453317760, 'type': 'call'},
            {'ticker': 'AVGO', 'name': 'Broadcom Inc', 'shares': 1191606, 'value': 328466194, 'type': 'stock'},
            {'ticker': 'VST', 'name': 'Vistra Corp', 'shares': 1274178, 'value': 246948438, 'type': 'stock'},
            {'ticker': 'CORZ', 'name': 'Core Scientific Inc', 'shares': 7994038, 'value': 136458229, 'type': 'stock'},
            {'ticker': 'EQT', 'name': 'EQT Corp', 'shares': 2145345, 'value': 125116520, 'type': 'stock'},
            {'ticker': 'CEG', 'name': 'Constellation Energy Corp', 'shares': 319200, 'value': 103024992, 'type': 'stock'},
            {'ticker': 'IREN', 'name': 'IREN Limited', 'shares': 6400384, 'value': 93253595, 'type': 'stock'},
            {'ticker': 'APLD', 'name': 'Applied Digital Corp', 'shares': 6591800, 'value': 66379426, 'type': 'stock'},
        ]
    },
    'Q3-2025': {
        'reportDate': '2025-09-30',
        'filedDate': '2025-11-14',
        'periodStart': '2025-07-01',
        'periodEnd': '2025-09-30',
        'holdings': [
            {'ticker': 'INTC', 'name': 'Intel Corp', 'shares': 20237400, 'value': 678964770, 'type': 'call'},
            {'ticker': 'CRWV', 'name': 'CoreWeave Inc', 'shares': 4115456, 'value': 563200154, 'type': 'stock'},
            {'ticker': 'CORZ', 'name': 'Core Scientific Inc', 'shares': 20180534, 'value': 362038780, 'type': 'stock'},
            {'ticker': 'IREN', 'name': 'IREN Limited', 'shares': 7220421, 'value': 338854358, 'type': 'stock'},
            {'ticker': 'CRWV', 'name': 'CoreWeave Inc (Call)', 'shares': 2314500, 'value': 316739325, 'type': 'call'},
            {'ticker': 'NVDA', 'name': 'NVIDIA Corp', 'shares': 1600000, 'value': 298528000, 'type': 'put'},
            {'ticker': 'VST', 'name': 'Vistra Corp', 'shares': 1287910, 'value': 252327327, 'type': 'stock'},
            {'ticker': 'SMH', 'name': 'VanEck Semiconductor ETF', 'shares': 600000, 'value': 195816000, 'type': 'put'},
            {'ticker': 'CRWV', 'name': 'CoreWeave Inc (Put)', 'shares': 1400000, 'value': 191590000, 'type': 'put'},
            {'ticker': 'APLD', 'name': 'Applied Digital Corp', 'shares': 6064155, 'value': 139111716, 'type': 'stock'},
            {'ticker': 'GLXY', 'name': 'Galaxy Digital Inc', 'shares': 2737500, 'value': 92554875, 'type': 'stock'},
            {'ticker': 'AVGO', 'name': 'Broadcom Inc', 'shares': 230000, 'value': 75879300, 'type': 'put'},
            {'ticker': 'TSM', 'name': 'Taiwan Semiconductor', 'shares': 270000, 'value': 75408300, 'type': 'put'},
            {'ticker': 'CIFR', 'name': 'Cipher Mining Inc', 'shares': 5740493, 'value': 72272807, 'type': 'stock'},
            {'ticker': 'RIOT', 'name': 'Riot Platforms Inc', 'shares': 3592699, 'value': 68369062, 'type': 'stock'},
            {'ticker': 'LITE', 'name': 'Lumentum Holdings Inc', 'shares': 417600, 'value': 67947696, 'type': 'stock'},
            {'ticker': 'EQT', 'name': 'EQT Corp', 'shares': 1217386, 'value': 66262320, 'type': 'stock'},
            {'ticker': 'MU', 'name': 'Micron Technology Inc', 'shares': 300000, 'value': 50196000, 'type': 'put'},
            {'ticker': 'SEI', 'name': 'Solaris Energy Infras Inc', 'shares': 1150300, 'value': 45977491, 'type': 'stock'},
            {'ticker': 'BE', 'name': 'Bloom Energy Corp', 'shares': 3048002, 'value': 43890344, 'type': 'stock'},
            {'ticker': 'TSEM', 'name': 'Tower Semiconductor Ltd', 'shares': 470600, 'value': 34024380, 'type': 'stock'},
            {'ticker': 'HUT', 'name': 'Hut 8 Corp', 'shares': 599000, 'value': 20851190, 'type': 'stock'},
            {'ticker': 'WDC', 'name': 'Western Digital Corp', 'shares': 152821, 'value': 18347689, 'type': 'stock'},
            {'ticker': 'COHR', 'name': 'Coherent Corp', 'shares': 154400, 'value': 16631968, 'type': 'stock'},
            {'ticker': 'BTDR', 'name': 'Bitdeer Technologies Group', 'shares': 929600, 'value': 15886864, 'type': 'stock'},
            {'ticker': 'SNDK', 'name': 'SanDisk Corp', 'shares': 115000, 'value': 12903000, 'type': 'stock'},
            {'ticker': 'BE', 'name': 'Bloom Energy Corp (Call)', 'shares': 145800, 'value': 12330306, 'type': 'call'},
            {'ticker': 'STX', 'name': 'Seagate Technology', 'shares': 48567, 'value': 11464726, 'type': 'stock'},
        ]
    }
}

CUSIP_TO_TICKER = {
    '573874104': 'MRVL', '92840M102': 'VST', '92535P101': 'VRT',
    '87425E103': 'TLN', '21037T109': 'CEG', '607828100': 'MOD',
    '458140100': 'INTC', '11135F101': 'AVGO', '682529107': 'ONTO',
    '26856L103': 'EQT', '21872J107': 'CRWV', '21871X109': 'CORZ',
    'G4701H208': 'IREN', '03831W108': 'APLD', '78464A714': 'SMH',
    '67066G104': 'NVDA', '874039100': 'TSM', '595112103': 'MU',
    '093671105': 'BE', '36254L100': 'GLXY', '87612E106': 'TSEM',
    '17469E108': 'CIFR', '767292105': 'RIOT', '55024U109': 'LITE',
    '83417Q105': 'SEI', '44267D107': 'HUT', '958102105': 'WDC',
    '19247G107': 'COHR', 'G1241V102': 'BTDR', '80004C209': 'SNDK',
    '81211L102': 'STX',
}

NAME_TO_TICKER = {
    'MARVELL': 'MRVL', 'VISTRA': 'VST', 'VERTIV': 'VRT',
    'TALEN': 'TLN', 'CONSTELLATION ENERGY': 'CEG', 'MODINE': 'MOD',
    'INTEL': 'INTC', 'BROADCOM': 'AVGO', 'ONTO INNOVATION': 'ONTO',
    'EQT CORP': 'EQT', 'COREWEAVE': 'CRWV', 'CORE SCIENTIFIC': 'CORZ',
    'IREN': 'IREN', 'APPLIED DIGITAL': 'APLD', 'VANECK SEMICONDUCTOR': 'SMH',
    'NVIDIA': 'NVDA', 'TAIWAN SEMICONDUCTOR': 'TSM', 'MICRON': 'MU',
    'BLOOM ENERGY': 'BE', 'GALAXY DIGITAL': 'GLXY', 'TOWER SEMICONDUCTOR': 'TSEM',
    'CIPHER MINING': 'CIFR', 'RIOT': 'RIOT', 'LUMENTUM': 'LITE',
    'SOLARIS': 'SEI', 'HUT 8': 'HUT', 'WESTERN DIGITAL': 'WDC',
    'COHERENT': 'COHR', 'BITDEER': 'BTDR', 'SANDISK': 'SNDK', 'SEAGATE': 'STX',
}

DEFAULT_IVS = {
    'INTC': 45, 'SMH': 30, 'NVDA': 50, 'CRWV': 65,
    'AVGO': 35, 'TSM': 35, 'MU': 50, 'BE': 60,
}


# ============================================
# BLACK-SCHOLES
# ============================================
def black_scholes(S, K, T, r, sigma, is_call):
    """Calculate Black-Scholes option price."""
    if T <= 0:
        return max(0, S - K if is_call else K - S)
    if sigma <= 0:
        return max(0, S - K if is_call else K - S)

    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if is_call:
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def year_fraction(from_date, to_date):
    """Calculate year fraction between two dates."""
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
    return (to_date - from_date).days / 365.25


# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def init_session_state():
    if 'holdings_data' not in st.session_state:
        st.session_state.holdings_data = DEFAULT_HOLDINGS_DATA.copy()
    if 'quarter_order' not in st.session_state:
        st.session_state.quarter_order = sorted(
            st.session_state.holdings_data.keys(),
            key=lambda q: (q.split('-')[1], q.split('-')[0])
        )
    if 'option_config' not in st.session_state:
        st.session_state.option_config = {}
    if 'price_cache' not in st.session_state:
        st.session_state.price_cache = {}
    if 'performance_data' not in st.session_state:
        st.session_state.performance_data = None
    if 'last_13f_check' not in st.session_state:
        st.session_state.last_13f_check = None


# ============================================
# PRICE FETCHING
# ============================================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_prices(ticker, start_date, end_date):
    """Fetch historical prices using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        if df.empty:
            return {}
        prices = {d.strftime('%Y-%m-%d'): row['Close'] for d, row in df.iterrows()}
        return prices
    except Exception as e:
        st.warning(f"Failed to fetch {ticker}: {e}")
        return {}


@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_live_quote(ticker):
    """Fetch current price and previous close."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current = info.get('regularMarketPrice') or info.get('currentPrice')
        prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
        if current and prev_close:
            change = ((current - prev_close) / prev_close) * 100
            return {'price': current, 'previousClose': prev_close, 'change': change}
    except Exception as e:
        pass
    return None


def fetch_iv(ticker):
    """Fetch implied volatility from options chain."""
    try:
        stock = yf.Ticker(ticker)
        exp_dates = stock.options
        if not exp_dates:
            return DEFAULT_IVS.get(ticker, 40)

        # Get nearest expiration
        opt = stock.option_chain(exp_dates[0])
        calls = opt.calls
        puts = opt.puts

        # Get ATM IV
        current_price = stock.info.get('regularMarketPrice', 0)
        if current_price and not calls.empty:
            calls['strike_diff'] = abs(calls['strike'] - current_price)
            atm_call = calls.loc[calls['strike_diff'].idxmin()]
            if atm_call['impliedVolatility'] > 0:
                return round(atm_call['impliedVolatility'] * 100)

        return DEFAULT_IVS.get(ticker, 40)
    except:
        return DEFAULT_IVS.get(ticker, 40)


# ============================================
# 13F FETCHING
# ============================================
def guess_ticker_from_name(name):
    """Try to identify ticker from issuer name."""
    name_upper = name.upper()
    for key, ticker in NAME_TO_TICKER.items():
        if key in name_upper:
            return ticker
    return None


def fetch_13f_data():
    """Fetch 13F filings from SEC EDGAR."""
    try:
        # Fetch submissions
        url = f"https://data.sec.gov/submissions/CIK{SEC_CIK}.json"
        headers = {'User-Agent': 'SA-Tracker research@example.com'}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        submissions = resp.json()

        # Find 13F filings
        filings = submissions.get('filings', {}).get('recent', submissions)
        forms = filings.get('form', [])
        accessions = filings.get('accessionNumber', [])
        report_dates = filings.get('reportDate', [])
        filed_dates = filings.get('filingDate', [])

        thirteen_f_filings = []
        for i, form in enumerate(forms):
            if form in ('13F-HR', '13F-HR/A'):
                thirteen_f_filings.append({
                    'accession': accessions[i],
                    'reportDate': report_dates[i],
                    'filedDate': filed_dates[i],
                })

        if not thirteen_f_filings:
            return None, "No 13F filings found"

        # Parse each filing
        new_holdings = {}
        for filing in thirteen_f_filings:
            holdings = parse_13f_filing(filing, headers)
            if holdings:
                quarter = get_quarter_from_date(filing['reportDate'])
                period = get_quarter_period(quarter)
                new_holdings[quarter] = {
                    'reportDate': filing['reportDate'],
                    'filedDate': filing['filedDate'],
                    'periodStart': period['start'],
                    'periodEnd': period['end'],
                    'holdings': holdings,
                }

        return new_holdings, None

    except Exception as e:
        return None, str(e)


def parse_13f_filing(filing, headers):
    """Parse a single 13F filing."""
    try:
        accession_clean = filing['accession'].replace('-', '')
        cik_clean = SEC_CIK.lstrip('0')
        base_url = f"https://www.sec.gov/Archives/edgar/data/{cik_clean}/{accession_clean}"

        # Try to find infotable.xml
        for filename in ['infotable.xml', 'primary_doc.xml']:
            try:
                resp = requests.get(f"{base_url}/{filename}", headers=headers, timeout=30)
                if resp.ok and ('informationTable' in resp.text or 'infoTable' in resp.text):
                    return parse_infotable_xml(resp.text)
            except:
                continue

        # Try index.json to find the file
        try:
            resp = requests.get(f"{base_url}/index.json", headers=headers, timeout=30)
            if resp.ok:
                index_data = resp.json()
                items = index_data.get('directory', {}).get('item', [])
                for item in items:
                    name = item.get('name', '')
                    if 'infotable' in name.lower() and name.endswith('.xml'):
                        xml_resp = requests.get(f"{base_url}/{name}", headers=headers, timeout=30)
                        if xml_resp.ok:
                            return parse_infotable_xml(xml_resp.text)
        except:
            pass

        return None
    except:
        return None


def parse_infotable_xml(xml_content):
    """Parse SEC infotable XML."""
    holdings = []
    try:
        # Remove namespace prefixes for easier parsing
        xml_clean = re.sub(r'ns\d+:', '', xml_content)
        xml_clean = re.sub(r'xmlns[^"]*"[^"]*"', '', xml_clean)

        root = ET.fromstring(xml_clean)

        # Find all infoTable entries
        for table in root.iter():
            if 'infoTable' in table.tag or 'informationTable' in table.tag:
                for entry in table:
                    if 'infoTable' in entry.tag.lower():
                        holding = parse_info_entry(entry)
                        if holding:
                            holdings.append(holding)
            elif table.tag.lower().endswith('infotable'):
                holding = parse_info_entry(table)
                if holding:
                    holdings.append(holding)
    except Exception as e:
        st.warning(f"XML parse error: {e}")

    return holdings


def parse_info_entry(entry):
    """Parse a single infoTable entry."""
    try:
        def get_text(names):
            for name in names:
                for el in entry.iter():
                    if el.tag.lower().endswith(name.lower()) and el.text:
                        return el.text.strip()
            return ''

        name_of_issuer = get_text(['nameOfIssuer'])
        title_of_class = get_text(['titleOfClass'])
        cusip = get_text(['cusip'])
        value_str = get_text(['value'])
        shares_str = get_text(['sshPrnamt'])

        if not name_of_issuer or not value_str:
            return None

        value = int(value_str.replace(',', '')) * 1000
        shares = int(shares_str.replace(',', '')) if shares_str else 0

        # Determine ticker
        ticker = CUSIP_TO_TICKER.get(cusip) or guess_ticker_from_name(name_of_issuer)
        if not ticker:
            ticker = name_of_issuer.split()[0].upper()[:5]

        # Determine type
        title_upper = title_of_class.upper()
        if 'CALL' in title_upper:
            pos_type = 'call'
        elif 'PUT' in title_upper:
            pos_type = 'put'
        else:
            pos_type = 'stock'

        name = name_of_issuer
        if pos_type != 'stock':
            name = f"{name_of_issuer} ({pos_type.title()})"

        return {
            'ticker': ticker,
            'name': name,
            'shares': shares,
            'value': value,
            'type': pos_type,
            'cusip': cusip,
        }
    except:
        return None


def get_quarter_from_date(date_str):
    """Get quarter string from date."""
    date = datetime.strptime(date_str, '%Y-%m-%d')
    month = date.month
    year = date.year
    if month <= 3:
        q = 'Q1'
    elif month <= 6:
        q = 'Q2'
    elif month <= 9:
        q = 'Q3'
    else:
        q = 'Q4'
    return f"{q}-{year}"


def get_quarter_period(quarter_str):
    """Get start and end dates for a quarter."""
    q, year = quarter_str.split('-')
    periods = {
        'Q1': {'start': f'{year}-01-01', 'end': f'{year}-03-31'},
        'Q2': {'start': f'{year}-04-01', 'end': f'{year}-06-30'},
        'Q3': {'start': f'{year}-07-01', 'end': f'{year}-09-30'},
        'Q4': {'start': f'{year}-10-01', 'end': f'{year}-12-31'},
    }
    return periods[q]


# ============================================
# PORTFOLIO CALCULATIONS
# ============================================
def get_option_key(quarter, ticker, opt_type, shares):
    """Generate unique key for option config."""
    return f"{quarter}-{ticker}-{opt_type}-{shares}"


def calculate_performance(holdings_data, quarter_order, option_config, portfolio_mode='full'):
    """Calculate portfolio performance over time."""
    all_dates = set()
    ticker_prices = {}

    # Get all unique tickers
    all_tickers = {'SPY', 'QQQ'}
    for q in quarter_order:
        for h in holdings_data[q]['holdings']:
            all_tickers.add(h['ticker'])

    # Fetch prices
    start_date = '2024-10-01'
    end_date = datetime.now().strftime('%Y-%m-%d')

    progress = st.progress(0)
    tickers_list = list(all_tickers)
    for i, ticker in enumerate(tickers_list):
        prices = fetch_prices(ticker, start_date, end_date)
        if prices:
            ticker_prices[ticker] = prices
            all_dates.update(prices.keys())
        progress.progress((i + 1) / len(tickers_list))
    progress.empty()

    sorted_dates = sorted(all_dates)
    if not sorted_dates:
        return None

    # Calculate daily portfolio values
    portfolio_values = []
    spy_values = []
    qqq_values = []

    portfolio_value = 100
    spy_value = 100
    qqq_value = 100

    prev_prices = {}
    prev_option_prices = {}
    risk_free_rate = 0.05

    for date in sorted_dates:
        # Determine active quarter
        active_quarter = quarter_order[0]
        for q in quarter_order:
            if date >= holdings_data[q]['reportDate']:
                active_quarter = q

        holdings = holdings_data[active_quarter]['holdings']
        stock_holdings = [h for h in holdings if h['type'] == 'stock']
        option_holdings = [h for h in holdings if h['type'] in ('call', 'put')]

        # Calculate total portfolio value
        total_stock_value = sum(h['value'] for h in stock_holdings)
        total_option_premium = 0

        if portfolio_mode == 'full':
            for h in option_holdings:
                key = get_option_key(active_quarter, h['ticker'], h['type'], h['shares'])
                config = option_config.get(key, {})
                if config.get('calculatedPremium'):
                    total_option_premium += config['calculatedPremium']

        total_portfolio_value = total_stock_value + total_option_premium if portfolio_mode == 'full' else total_stock_value

        portfolio_return = 0

        # Stock returns
        for h in stock_holdings:
            prices = ticker_prices.get(h['ticker'], {})
            if date not in prices:
                continue

            current_price = prices[date]
            prev_price = prev_prices.get(h['ticker'])

            if prev_price and prev_price > 0:
                stock_return = (current_price - prev_price) / prev_price
                weight = h['value'] / total_portfolio_value if total_portfolio_value > 0 else 0
                portfolio_return += stock_return * weight

            prev_prices[h['ticker']] = current_price

        # Option returns (full mode only)
        if portfolio_mode == 'full':
            for h in option_holdings:
                key = get_option_key(active_quarter, h['ticker'], h['type'], h['shares'])
                config = option_config.get(key, {})

                if not all(config.get(k) for k in ('strike', 'expiry', 'iv')):
                    continue

                prices = ticker_prices.get(h['ticker'], {})
                if date not in prices:
                    continue

                spot = prices[date]
                T = year_fraction(date, config['expiry'])
                option_price = black_scholes(
                    spot, config['strike'], T, risk_free_rate,
                    config['iv'] / 100, h['type'] == 'call'
                )

                opt_key = f"{key}-price"
                prev_opt_price = prev_option_prices.get(opt_key)

                if prev_opt_price and prev_opt_price > 0.01 and config.get('calculatedPremium'):
                    opt_return = (option_price - prev_opt_price) / prev_opt_price
                    weight = config['calculatedPremium'] / total_portfolio_value if total_portfolio_value > 0 else 0
                    portfolio_return += opt_return * weight

                prev_option_prices[opt_key] = option_price
                prev_prices[h['ticker']] = spot

        portfolio_value *= (1 + portfolio_return)

        # Benchmarks
        if 'SPY' in ticker_prices and date in ticker_prices['SPY']:
            p = ticker_prices['SPY'][date]
            if prev_prices.get('SPY', 0) > 0:
                spy_value *= (1 + (p - prev_prices['SPY']) / prev_prices['SPY'])
            prev_prices['SPY'] = p

        if 'QQQ' in ticker_prices and date in ticker_prices['QQQ']:
            p = ticker_prices['QQQ'][date]
            if prev_prices.get('QQQ', 0) > 0:
                qqq_value *= (1 + (p - prev_prices['QQQ']) / prev_prices['QQQ'])
            prev_prices['QQQ'] = p

        portfolio_values.append({'date': date, 'value': portfolio_value})
        spy_values.append({'date': date, 'value': spy_value})
        qqq_values.append({'date': date, 'value': qqq_value})

    return {
        'portfolio': portfolio_values,
        'spy': spy_values,
        'qqq': qqq_values,
        'ticker_prices': ticker_prices,
    }


def calculate_metrics(values):
    """Calculate performance metrics."""
    if len(values) < 2:
        return {'total_return': 0, 'ytd_return': 0, 'sharpe': 0, 'max_drawdown': 0}

    total_return = (values[-1]['value'] / values[0]['value'] - 1) * 100

    # YTD return
    jan_2026 = next((p for p in values if p['date'] >= '2026-01-01'), None)
    ytd_return = ((values[-1]['value'] / jan_2026['value']) - 1) * 100 if jan_2026 else 0

    # Daily returns for Sharpe
    returns = []
    for i in range(1, len(values)):
        returns.append((values[i]['value'] - values[i-1]['value']) / values[i-1]['value'])

    avg_return = np.mean(returns)
    std_return = np.std(returns)
    sharpe = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0

    # Max drawdown
    peak = values[0]['value']
    max_dd = 0
    for p in values:
        if p['value'] > peak:
            peak = p['value']
        dd = (peak - p['value']) / peak
        max_dd = max(max_dd, dd)

    return {
        'total_return': total_return,
        'ytd_return': ytd_return,
        'sharpe': sharpe,
        'max_drawdown': max_dd * 100,
    }


def calculate_weights_for_date(date, holdings_data, quarter_order, option_config, ticker_prices, portfolio_mode):
    """Calculate portfolio weights for a specific date."""
    # Determine active quarter
    active_quarter = quarter_order[0]
    for q in quarter_order:
        if date >= holdings_data[q]['reportDate']:
            active_quarter = q

    holdings = holdings_data[active_quarter]['holdings']
    stock_holdings = [h for h in holdings if h['type'] == 'stock']
    option_holdings = [h for h in holdings if h['type'] in ('call', 'put')]

    weights = []
    total_value = 0
    risk_free_rate = 0.05

    # Stock values
    for h in stock_holdings:
        prices = ticker_prices.get(h['ticker'], {})
        if date not in prices:
            continue

        price = prices[date]
        value = h['shares'] * price
        total_value += value
        weights.append({
            'ticker': h['ticker'],
            'type': 'stock',
            'shares': h['shares'],
            'price': price,
            'value': value,
        })

    # Option values (full mode only)
    if portfolio_mode == 'full':
        for h in option_holdings:
            key = get_option_key(active_quarter, h['ticker'], h['type'], h['shares'])
            config = option_config.get(key, {})

            if not all(config.get(k) for k in ('strike', 'expiry', 'iv')):
                continue

            prices = ticker_prices.get(h['ticker'], {})
            if date not in prices:
                continue

            spot = prices[date]
            T = year_fraction(date, config['expiry'])
            opt_price = black_scholes(
                spot, config['strike'], T, risk_free_rate,
                config['iv'] / 100, h['type'] == 'call'
            )
            value = opt_price * h['shares']

            if value > 0:
                total_value += value
                weights.append({
                    'ticker': h['ticker'],
                    'type': h['type'],
                    'shares': h['shares'],
                    'price': opt_price,
                    'value': value,
                    'strike': config['strike'],
                    'expiry': config['expiry'],
                })

    # Calculate percentages
    for w in weights:
        w['weight'] = (w['value'] / total_value * 100) if total_value > 0 else 0

    # Sort by weight
    weights.sort(key=lambda x: x['weight'], reverse=True)

    return {
        'date': date,
        'quarter': active_quarter,
        'total_value': total_value,
        'weights': weights,
    }


# ============================================
# UI COMPONENTS
# ============================================
def format_currency(value):
    """Format value as currency."""
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    if value >= 1e6:
        return f"${value/1e6:.0f}M"
    return f"${value/1e3:.0f}K"


def render_performance_chart(data, selected_range='ALL'):
    """Render the performance chart with Plotly."""
    portfolio = data['portfolio']
    spy = data['spy']
    qqq = data['qqq']

    # Filter by range
    if selected_range != 'ALL':
        days = {'1D': 2, '1W': 7, '1M': 30, '3M': 90, '6M': 180}.get(selected_range, 0)
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            portfolio = [p for p in portfolio if p['date'] >= cutoff]
            spy = [p for p in spy if p['date'] >= cutoff]
            qqq = [p for p in qqq if p['date'] >= cutoff]

    if not portfolio:
        st.warning("No data for selected range")
        return None

    # Rebase to 100
    base_port = portfolio[0]['value']
    base_spy = spy[0]['value'] if spy else 1
    base_qqq = qqq[0]['value'] if qqq else 1

    portfolio = [{'date': p['date'], 'value': p['value'] / base_port * 100} for p in portfolio]
    spy = [{'date': p['date'], 'value': p['value'] / base_spy * 100} for p in spy]
    qqq = [{'date': p['date'], 'value': p['value'] / base_qqq * 100} for p in qqq]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[p['date'] for p in portfolio],
        y=[p['value'] for p in portfolio],
        name='SA LP',
        line=dict(color='#2c5282', width=2),
        fill='tozeroy',
        fillcolor='rgba(44, 82, 130, 0.1)',
    ))

    fig.add_trace(go.Scatter(
        x=[p['date'] for p in spy],
        y=[p['value'] for p in spy],
        name='SPY',
        line=dict(color='#718096', width=1.5, dash='dash'),
    ))

    fig.add_trace(go.Scatter(
        x=[p['date'] for p in qqq],
        y=[p['value'] for p in qqq],
        name='QQQ',
        line=dict(color='#a0aec0', width=1.5, dash='dot'),
    ))

    fig.update_layout(
        title=None,
        xaxis_title=None,
        yaxis_title='Return (%)',
        yaxis=dict(tickformat='.0f', ticksuffix='%', tickvals=[v for v in range(50, 200, 10)]),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=0, r=0, t=30, b=0),
        height=400,
    )

    # Subtract 100 from y-axis labels to show as return %
    fig.update_yaxes(ticktext=[f"{v-100:+.0f}%" for v in range(50, 200, 10)])

    return fig, portfolio


def render_holdings_table(quarter, holdings_data, option_config):
    """Render holdings table for a quarter."""
    data = holdings_data[quarter]
    holdings = data['holdings']

    stocks = [h for h in holdings if h['type'] == 'stock']
    options = [h for h in holdings if h['type'] in ('call', 'put')]

    # Calculate totals
    total_stock_value = sum(h['value'] for h in stocks)
    total_option_premium = 0
    for h in options:
        key = get_option_key(quarter, h['ticker'], h['type'], h['shares'])
        config = option_config.get(key, {})
        if config.get('calculatedPremium'):
            total_option_premium += config['calculatedPremium']

    total_value = total_stock_value + total_option_premium

    st.markdown(f"**Report Date:** {data['reportDate']} | **Total Value:** {format_currency(total_value)} | **Positions:** {len(holdings)}")

    # Stocks table
    if stocks:
        st.markdown("##### Stock Positions")
        stock_df = pd.DataFrame([{
            'Ticker': h['ticker'],
            'Name': h['name'],
            'Shares': f"{h['shares']:,}",
            'Value': format_currency(h['value']),
            'Weight': f"{h['value']/total_value*100:.1f}%" if total_value > 0 else '—',
        } for h in stocks])
        st.dataframe(stock_df, use_container_width=True, hide_index=True)

    # Options table
    if options:
        st.markdown("##### Options Positions")
        opt_rows = []
        for h in options:
            key = get_option_key(quarter, h['ticker'], h['type'], h['shares'])
            config = option_config.get(key, {})
            premium = config.get('calculatedPremium', 0)
            weight = premium / total_value * 100 if total_value > 0 and premium else 0
            opt_rows.append({
                'Ticker': h['ticker'],
                'Type': h['type'].upper(),
                'Notional': format_currency(h['value']),
                'Strike': f"${config.get('strike', '—')}",
                'Expiry': config.get('expiry', '—'),
                'IV': f"{config.get('iv', '—')}%",
                'Premium': format_currency(premium) if premium else '—',
                'Weight': f"{weight:.1f}%" if weight else '—',
            })
        st.dataframe(pd.DataFrame(opt_rows), use_container_width=True, hide_index=True)


# ============================================
# MAIN APP
# ============================================
def main():
    init_session_state()

    st.title("📈 Situational Awareness LP")
    st.caption("Portfolio Performance Tracker · CIK 0002045724")

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        # Portfolio mode
        portfolio_mode = st.radio(
            "Portfolio Mode",
            ['Full Portfolio', 'Equities Only'],
            help="Full Portfolio includes options valued with Black-Scholes"
        )
        mode = 'full' if portfolio_mode == 'Full Portfolio' else 'equities'

        st.divider()

        # 13F Data section
        st.subheader("13F Data")
        last_check = st.session_state.last_13f_check
        if last_check:
            st.caption(f"Last checked: {last_check}")
        else:
            st.caption("Using built-in data")

        if st.button("Check for Updates", use_container_width=True):
            with st.spinner("Fetching from SEC EDGAR..."):
                new_data, error = fetch_13f_data()
                if error:
                    st.error(f"Error: {error}")
                elif new_data:
                    # Merge with existing
                    st.session_state.holdings_data.update(new_data)
                    st.session_state.quarter_order = sorted(
                        st.session_state.holdings_data.keys(),
                        key=lambda q: (q.split('-')[1], q.split('-')[0])
                    )
                    st.session_state.last_13f_check = datetime.now().strftime('%Y-%m-%d %H:%M')
                    st.session_state.performance_data = None  # Clear cache
                    st.success(f"Updated {len(new_data)} quarters")
                    st.rerun()

        st.divider()

        # Time range
        st.subheader("Time Range")
        time_range = st.selectbox(
            "Select Range",
            ['ALL', '6M', '3M', '1M', '1W'],
            label_visibility='collapsed'
        )

    # Main content
    tab1, tab2, tab3 = st.tabs(["📊 Performance", "⚙️ Options Config", "📋 Holdings"])

    # Options Config Tab
    with tab2:
        st.header("Options Configuration")
        st.info("Configure strike, expiry, and IV for each option position. Premium is calculated using Black-Scholes.")

        # Get all options across quarters
        all_options = []
        for q in st.session_state.quarter_order:
            for h in st.session_state.holdings_data[q]['holdings']:
                if h['type'] in ('call', 'put'):
                    all_options.append({**h, 'quarter': q})

        if not all_options:
            st.write("No options positions found.")
        else:
            # Create editable dataframe
            for opt in all_options:
                key = get_option_key(opt['quarter'], opt['ticker'], opt['type'], opt['shares'])
                config = st.session_state.option_config.get(key, {})

                col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1.5])

                with col1:
                    st.text(f"{opt['quarter']}")
                with col2:
                    st.text(f"{opt['ticker']} {opt['type'].upper()}")
                with col3:
                    strike = st.number_input(
                        "Strike",
                        value=float(config.get('strike', 0)),
                        min_value=0.0,
                        step=1.0,
                        key=f"strike_{key}",
                        label_visibility='collapsed'
                    )
                with col4:
                    expiry = st.date_input(
                        "Expiry",
                        value=datetime.strptime(config['expiry'], '%Y-%m-%d') if config.get('expiry') else None,
                        key=f"expiry_{key}",
                        label_visibility='collapsed'
                    )
                with col5:
                    iv = st.number_input(
                        "IV",
                        value=float(config.get('iv', fetch_iv(opt['ticker']))),
                        min_value=1.0,
                        max_value=300.0,
                        step=1.0,
                        key=f"iv_{key}",
                        label_visibility='collapsed'
                    )
                with col6:
                    # Calculate premium
                    if strike > 0 and expiry and iv > 0:
                        spot = opt['value'] / opt['shares']
                        report_date = st.session_state.holdings_data[opt['quarter']]['reportDate']
                        T = year_fraction(report_date, expiry.strftime('%Y-%m-%d'))
                        if T > 0:
                            opt_price = black_scholes(spot, strike, T, 0.05, iv/100, opt['type'] == 'call')
                            premium = opt_price * opt['shares']
                            st.text(f"Premium: {format_currency(premium)}")

                            # Save config
                            st.session_state.option_config[key] = {
                                'strike': strike,
                                'expiry': expiry.strftime('%Y-%m-%d'),
                                'iv': iv,
                                'calculatedPremium': premium,
                            }
                        else:
                            st.text("Expired")
                    else:
                        st.text("Configure →")

                st.divider()

    # Performance Tab
    with tab1:
        # Check if options are configured (for full mode)
        options_configured = True
        if mode == 'full':
            for q in st.session_state.quarter_order:
                for h in st.session_state.holdings_data[q]['holdings']:
                    if h['type'] in ('call', 'put'):
                        key = get_option_key(q, h['ticker'], h['type'], h['shares'])
                        config = st.session_state.option_config.get(key, {})
                        if not all(config.get(k) for k in ('strike', 'expiry', 'iv')):
                            options_configured = False
                            break

        if mode == 'full' and not options_configured:
            st.warning("⚠️ Configure all options in the **Options Config** tab before calculating full portfolio performance.")

        # Calculate button
        if st.button("Calculate Performance", type="primary", disabled=(mode == 'full' and not options_configured)):
            with st.spinner("Fetching prices and calculating performance..."):
                data = calculate_performance(
                    st.session_state.holdings_data,
                    st.session_state.quarter_order,
                    st.session_state.option_config,
                    mode
                )
                st.session_state.performance_data = data

        # Display results
        if st.session_state.performance_data:
            data = st.session_state.performance_data

            # Chart
            fig, filtered_portfolio = render_performance_chart(data, time_range)
            if fig:
                # Make chart clickable
                selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="perf_chart")

                # Check if a point was clicked
                if selected_points and selected_points.selection and selected_points.selection.points:
                    point = selected_points.selection.points[0]
                    clicked_date = filtered_portfolio[point['point_index']]['date']

                    # Show weights panel
                    weights_data = calculate_weights_for_date(
                        clicked_date,
                        st.session_state.holdings_data,
                        st.session_state.quarter_order,
                        st.session_state.option_config,
                        data['ticker_prices'],
                        mode
                    )

                    st.subheader(f"Portfolio Weights - {clicked_date}")
                    st.caption(f"Quarter: {weights_data['quarter']} | Total Value: {format_currency(weights_data['total_value'])}")

                    # Display as cards
                    cols = st.columns(4)
                    for i, w in enumerate(weights_data['weights']):
                        with cols[i % 4]:
                            type_emoji = "📈" if w['type'] == 'stock' else ("📞" if w['type'] == 'call' else "📉")
                            st.metric(
                                label=f"{type_emoji} {w['ticker']}",
                                value=f"{w['weight']:.1f}%",
                                delta=format_currency(w['value']),
                                delta_color="off"
                            )

            # Metrics
            metrics = calculate_metrics(filtered_portfolio)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                color = "normal" if metrics['total_return'] >= 0 else "inverse"
                st.metric("Total Return", f"{metrics['total_return']:+.1f}%")
            with col2:
                st.metric("YTD Return", f"{metrics['ytd_return']:+.1f}%" if metrics['ytd_return'] else "—")
            with col3:
                st.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
            with col4:
                st.metric("Max Drawdown", f"-{metrics['max_drawdown']:.1f}%")

    # Holdings Tab
    with tab3:
        st.header("Quarterly Holdings")

        selected_quarter = st.selectbox(
            "Select Quarter",
            st.session_state.quarter_order[::-1],  # Reverse to show latest first
            label_visibility='collapsed'
        )

        render_holdings_table(selected_quarter, st.session_state.holdings_data, st.session_state.option_config)

    # Footer
    st.divider()
    st.caption("Data from [SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0002045724&type=13F) and Yahoo Finance. Not financial advice.")


if __name__ == "__main__":
    main()
