import requests
import urllib.parse
import pandas as pd
import time
import os


def get_scrape_token():
    token = os.environ.get("SCRAPE_DO_TOKEN")
    if not token:
        return None
    return token


def get_bitcoin_price():
    scrape_token = get_scrape_token()
    if not scrape_token:
        return {"error": "SCRAPE_DO_TOKEN not configured"}
    target_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    encoded_url = urllib.parse.quote(target_url)
    scrape_url = f"http://api.scrape.do/?url={encoded_url}&token={scrape_token}"
    
    try:
        response = requests.get(scrape_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if "bitcoin" in data:
                return data["bitcoin"]
        return {"error": "Failed to fetch data"}
    except Exception as e:
        return {"error": str(e)}


def get_ethereum_price():
    scrape_token = get_scrape_token()
    if not scrape_token:
        return {"error": "SCRAPE_DO_TOKEN not configured"}
    target_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true"
    encoded_url = urllib.parse.quote(target_url)
    scrape_url = f"http://api.scrape.do/?url={encoded_url}&token={scrape_token}"
    
    try:
        response = requests.get(scrape_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if "ethereum" in data:
                return data["ethereum"]
        return {"error": "Failed to fetch data"}
    except Exception as e:
        return {"error": str(e)}


def get_fear_greed_index():
    scrape_token = get_scrape_token()
    if not scrape_token:
        return {"error": "SCRAPE_DO_TOKEN not configured"}
    
    try:
        # Calculate time range (last 30 days)
        end_ts = int(time.time())
        start_ts = end_ts - (30 * 24 * 60 * 60)
        
        target_url = f"https://api.coinmarketcap.com/data-api/v3/fear-greed/chart?start={start_ts}&end={end_ts}&convertId=2781"
        encoded_url = urllib.parse.quote(target_url)
        scrape_url = f"http://api.scrape.do/?url={encoded_url}&token={scrape_token}"
        
        response = requests.get(scrape_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'dataList' in data['data'] and data['data']['dataList']:
                latest = data['data']['dataList'][-1]
                return {
                    "value": int(latest['score']),
                    "classification": latest['name'],
                    "timestamp": latest['timestamp'],
                    "btc_price": float(latest['btcPrice']),
                    "history": data['data']['dataList']
                }
        return {"error": "Failed to fetch data"}
    except Exception as e:
        return {"error": str(e)}


def get_global_market_metrics():
    scrape_token = get_scrape_token()
    if not scrape_token:
        return {"error": "SCRAPE_DO_TOKEN not configured"}
    
    try:
        target_url = "https://api.coinmarketcap.com/data-api/v4/global-metrics/quotes/historical?convertId=2781&range=1y"
        encoded_url = urllib.parse.quote(target_url)
        scrape_url = f"http://api.scrape.do/?url={encoded_url}&token={scrape_token}"
        
        response = requests.get(scrape_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'points' in data['data'] and data['data']['points']:
                latest = data['data']['points'][-1]
                total_market_cap = float(latest['marketCap'])
                btc_market_cap = float(latest['btcValue'])
                eth_market_cap = float(latest['ethValue'])
                
                # Calculate dominance
                btc_dominance = (btc_market_cap / total_market_cap) * 100
                eth_dominance = (eth_market_cap / total_market_cap) * 100
                
                # Calculate 24h change
                btc_change = 0
                eth_change = 0
                if len(data['data']['points']) >= 2:
                    prev = data['data']['points'][-2]
                    prev_total = float(prev['marketCap'])
                    prev_btc = float(prev['btcValue'])
                    prev_eth = float(prev['ethValue'])
                    
                    prev_btc_dom = (prev_btc / prev_total) * 100
                    prev_eth_dom = (prev_eth / prev_total) * 100
                    
                    btc_change = btc_dominance - prev_btc_dom
                    eth_change = eth_dominance - prev_eth_dom
                
                return {
                    "total_market_cap": total_market_cap,
                    "total_volume": float(latest['volume']),
                    "btc_market_cap": btc_market_cap,
                    "eth_market_cap": eth_market_cap,
                    "btc_dominance": btc_dominance,
                    "eth_dominance": eth_dominance,
                    "btc_24h_change": btc_change,
                    "eth_24h_change": eth_change,
                    "timestamp": latest['timestamp']
                }
        return {"error": "Failed to fetch data"}
    except Exception as e:
        return {"error": str(e)}


def get_dominance_metrics():
    # This function is now integrated into get_global_market_metrics
    # Keeping it for backward compatibility
    market = get_global_market_metrics()
    if "error" not in market:
        return {
            "btc_dominance": market["btc_dominance"],
            "eth_dominance": market["eth_dominance"],
            "btc_24h_change": market["btc_24h_change"],
            "eth_24h_change": market["eth_24h_change"],
            "timestamp": market["timestamp"]
        }
    return market


def get_cmc_hot_tokens(limit=10):
    url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing"
    params = {
        "start": "1",
        "limit": str(limit),
        "sortBy": "market_cap",
        "sortType": "desc",
        "convert": "USD"
    }
    try:
        response = requests.get(url, headers={"Accept": "application/json"})
        data = response.json()
        tokens = []
        for item in data.get("data", {}).get("cryptoCurrencyList", []):
            tokens.append({
                "name": item.get("name"),
                "symbol": item.get("symbol"),
                "price": item.get("quotes", [{}])[0].get("price"),
                "change_24h": item.get("quotes", [{}])[0].get("percentChange24h"),
                "market_cap": item.get("quotes", [{}])[0].get("marketCap")
            })
        return tokens
    except Exception as e:
        return {"error": str(e)}


def get_prediction_markets():
    scrape_token = get_scrape_token()
    if not scrape_token:
        return {"error": "SCRAPE_DO_TOKEN not configured"}
    
    try:
        target_url = "https://dapi.coinmarketcap.com/aggr/predict/v2/events?platforms=all&frequency=all&status=open&topic=trending&tagId=&sortBy=trending&sortType=desc&search="
        encoded_url = urllib.parse.quote(target_url)
        scrape_url = f"http://api.scrape.do/?url={encoded_url}&token={scrape_token}"
        
        response = requests.get(scrape_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and isinstance(data['data'], dict):
                events = data['data'].get('events', [])
                markets = []
                
                for event in events[:10]:
                    markets_list = event.get('markets', [])
                    if markets_list:
                        first_market = markets_list[0]
                        prices = first_market.get('prices', [])
                        yes_prob = 0
                        no_prob = 0
                        
                        if prices:
                            outcome_prices = prices[0].get('outcomePrices', [0, 0])
                            yes_prob = outcome_prices[0] if len(outcome_prices) > 0 else 0
                            no_prob = outcome_prices[1] if len(outcome_prices) > 1 else 0
                        
                        markets.append({
                            "topic": event.get('title', 'N/A'),
                            "platform": event.get('source', {}).get('sourceName', 'N/A'),
                            "yes_prob": yes_prob,
                            "no_prob": no_prob,
                            "volume": f"${event.get('totalVolumeUsd', 0)/1e6:.2f}M",
                            "buy_link": event.get('buyLink', '')
                        })
                
                return markets
        return {"error": "Failed to fetch data"}
    except Exception as e:
        return {"error": str(e)}


def get_vix_data():
    scrape_token = get_scrape_token()
    if not scrape_token:
        return {"error": "SCRAPE_DO_TOKEN not configured"}
    url = "https://api.investing.com/api/financialdata/44336/historical/chart/?interval=P1D&pointscount=110"
    encoded_url = urllib.parse.quote(url)
    scrape_url = f"http://api.scrape.do/?url={encoded_url}&token={scrape_token}"
    
    try:
        for retry in range(3):
            try:
                response = requests.get(scrape_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data']:
                        points = data['data']
                        if isinstance(points, dict) and 'points' in points:
                            points = points['points']
                        
                        # Format: [timestamp, open, high, low, close, volume, unknown]
                        df = pd.DataFrame(points, columns=["timestamp", "open", "high", "low", "close", "volume", "unknown"])
                        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df = df[['date', 'close']].tail(30)
                        df.columns = ['date', 'VIX']
                        return df
                time.sleep(0.5)
            except Exception as e:
                if retry < 2:
                    time.sleep(1)
                    continue
                return {"error": str(e)}
        return {"error": "Failed to fetch VIX data after 3 retries"}
    except Exception as e:
        return {"error": str(e)}


ETF_FULL_NAMES = {
    "BTCO": "Bitcoin Strategy ETF (Bitwise)",
    "EZBC": "Bitcoin ETF (Bitwise)",
    "ARKB": "21Shares Bitcoin ETF",
    "IBIT": "BlackRock iShares Bitcoin Trust",
    "BTCW": "Bitcoin Strategy ETF (MicroStrategy)",
    "BITB": "Bitcoin ETF (Bitwise)",
    "GBTC": "Grayscale Bitcoin Trust",
    "FBTC": "Fidelity Bitcoin ETF",
    "HODL": "Bitcoin ETF (Hashdex)",
    "BRRR": "Bitcoin ETF (Franklin Templeton)",
    "BITO": "ProShares Bitcoin Strategy ETF",
    "BTCY": "Bitcoin Strategy ETF (Direxion)"
}


def get_bitcoin_etf_flows():
    scrape_token = get_scrape_token()
    if not scrape_token:
        return {"error": "SCRAPE_DO_TOKEN not configured"}
    
    overview_url = "https://api.coinmarketcap.com/data-api/v3/etf/overview/netflow/chart?category=btc&range=30d&convertId=2781"
    detail_url = "https://api.coinmarketcap.com/data-api/v3/etf/detail/netflow?category=btc&range=30d&convertId=2781"
    
    def fetch_data(target_url):
        encoded_url = urllib.parse.quote(target_url)
        scrape_url = f"http://api.scrape.do/?url={encoded_url}&token={scrape_token}"
        try:
            response = requests.get(scrape_url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    overview_data = fetch_data(overview_url)
    detail_data = fetch_data(detail_url)
    
    result = {
        "overview": overview_data,
        "detail": detail_data,
        "etf_full_names": ETF_FULL_NAMES
    }
    
    return result


def get_contract_open_interest():
    oi_data = []
    
    try:
        response = requests.get("https://fapi.binance.com/fapi/v1/openInterest", params={"symbol": "BTCUSDT"})
        if response.status_code == 200:
            btc_oi = float(response.json()["openInterest"]) / 1000
        else:
            btc_oi = 0
        
        response = requests.get("https://fapi.binance.com/fapi/v1/openInterest", params={"symbol": "ETHUSDT"})
        if response.status_code == 200:
            eth_oi = float(response.json()["openInterest"]) / 1000
        else:
            eth_oi = 0
        
        oi_data.append({"exchange": "Binance", "btc_oi": btc_oi, "eth_oi": eth_oi})
    except Exception as e:
        oi_data.append({"exchange": "Binance", "btc_oi": 0, "eth_oi": 0})
    
    try:
        response = requests.get("https://www.okx.com/api/v5/public/open-interest", params={"instId": "BTC-USD-SWAP"})
        if response.status_code == 200 and response.json().get("code") == "0":
            btc_oi = float(response.json()["data"][0]["oi"]) / 1000
        else:
            btc_oi = 0
        
        response = requests.get("https://www.okx.com/api/v5/public/open-interest", params={"instId": "ETH-USD-SWAP"})
        if response.status_code == 200 and response.json().get("code") == "0":
            eth_oi = float(response.json()["data"][0]["oi"]) / 1000
        else:
            eth_oi = 0
        
        oi_data.append({"exchange": "OKX", "btc_oi": btc_oi, "eth_oi": eth_oi})
    except Exception as e:
        oi_data.append({"exchange": "OKX", "btc_oi": 0, "eth_oi": 0})
    
    try:
        response = requests.get("https://api.bybit.com/v5/market/open-interest", params={"category": "linear", "symbol": "BTCUSDT"})
        if response.status_code == 200 and response.json().get("retCode") == 0:
            btc_oi = float(response.json()["result"]["openInterest"]) / 1000
        else:
            btc_oi = 0
        
        response = requests.get("https://api.bybit.com/v5/market/open-interest", params={"category": "linear", "symbol": "ETHUSDT"})
        if response.status_code == 200 and response.json().get("retCode") == 0:
            eth_oi = float(response.json()["result"]["openInterest"]) / 1000
        else:
            eth_oi = 0
        
        oi_data.append({"exchange": "Bybit", "btc_oi": btc_oi, "eth_oi": eth_oi})
    except Exception as e:
        oi_data.append({"exchange": "Bybit", "btc_oi": 0, "eth_oi": 0})
    
    try:
        response = requests.post("https://api.hyperliquid.xyz/info", json={"type": "openInterest"})
        if response.status_code == 200:
            data = response.json()
            btc_oi = 0
            eth_oi = 0
            for item in data:
                if "BTC" in item.get("coin", ""):
                    btc_oi = float(item.get("openInterest", 0)) / 1000
                elif "ETH" in item.get("coin", ""):
                    eth_oi = float(item.get("openInterest", 0)) / 1000
        else:
            btc_oi = 0
            eth_oi = 0
        
        oi_data.append({"exchange": "Hyperliquid", "btc_oi": btc_oi, "eth_oi": eth_oi})
    except Exception as e:
        oi_data.append({"exchange": "Hyperliquid", "btc_oi": 0, "eth_oi": 0})
    
    return oi_data


def get_crypto_correlation_data():
    correlations = []
    scrape_token = get_scrape_token()
    if not scrape_token:
        return {"error": "SCRAPE_DO_TOKEN not configured"}
    
    # Helper function to fetch with retries
    def fetch_with_retry(url, max_retries=3):
        for i in range(max_retries):
            try:
                encoded_url = urllib.parse.quote(url)
                scrape_url = f"http://api.scrape.do/?url={encoded_url}&token={scrape_token}"
                response = requests.get(scrape_url, timeout=20)
                if response.status_code == 200:
                    return response.json()
                time.sleep(0.5)  # Small delay between retries
            except Exception as e:
                if i < max_retries - 1:
                    time.sleep(1)
        return None
    
    # Get BTC prices from CoinGecko
    btc_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=90&interval=daily"
    btc_data = fetch_with_retry(btc_url)
    btc_prices = [point[1] for point in btc_data["prices"]] if btc_data and "prices" in btc_data else []
    
    # Get crypto correlations
    crypto_assets = [
        {"name": "Ethereum", "coin": "ethereum"},
        {"name": "Solana", "coin": "solana"},
        {"name": "BNB", "coin": "binancecoin"}
    ]
    
    for asset in crypto_assets:
        url = f"https://api.coingecko.com/api/v3/coins/{asset['coin']}/market_chart?vs_currency=usd&days=90&interval=daily"
        asset_data = fetch_with_retry(url)
        
        if asset_data and "prices" in asset_data:
            asset_prices = [point[1] for point in asset_data["prices"]]
            
            if btc_prices and asset_prices and len(btc_prices) > 30 and len(asset_prices) > 30:
                min_len = min(len(btc_prices), len(asset_prices))
                btc_aligned = btc_prices[-min_len:]
                asset_aligned = asset_prices[-min_len:]
                
                corr = pd.Series(btc_aligned).corr(pd.Series(asset_aligned))
                correlations.append({"asset": asset["name"], "correlation": corr})
    
    # Get traditional assets from invest.com
    traditional_assets = [
        {"name": "Gold Futures", "id": "8830", "points": 110},
        {"name": "S&P 500", "id": "166", "points": 60},
        {"name": "Nasdaq 100", "id": "20", "points": 60},
        {"name": "Oil (WTI)", "id": "8849", "points": 110}
    ]
    
    for asset in traditional_assets:
        url = f"https://api.investing.com/api/financialdata/{asset['id']}/historical/chart/?interval=P1D&pointscount={asset['points']}"
        data = fetch_with_retry(url)
        
        if data and 'data' in data:
            # Handle both dict and list formats
            points = []
            if isinstance(data['data'], dict) and 'points' in data['data']:
                points = data['data']['points']
            elif isinstance(data['data'], list):
                points = data['data']
            
            if points:
                # Format: [timestamp, open, high, low, close, volume, ...]
                asset_prices = [point[4] for point in points if len(point) > 4]
                
                if btc_prices and asset_prices and len(btc_prices) > 30 and len(asset_prices) > 30:
                    min_len = min(len(btc_prices), len(asset_prices))
                    btc_aligned = btc_prices[-min_len:]
                    asset_aligned = asset_prices[-min_len:]
                    
                    corr = pd.Series(btc_aligned).corr(pd.Series(asset_aligned))
                    correlations.append({"asset": asset["name"], "correlation": corr})
    
    # Sort by absolute correlation
    correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    
    return correlations


def get_narratives():
    narratives = [
        {"topic": "Bitcoin ETF", "trend": "up", "description": "Institutional adoption continues"},
        {"topic": "DeFi 2.0", "trend": "up", "description": "New protocols gaining traction"},
        {"topic": "RWA Tokenization", "trend": "up", "description": "Real-world assets on-chain"},
        {"topic": "AI + Crypto", "trend": "up", "description": "AI agents in DeFi"},
        {"topic": "Layer 2 Scaling", "trend": "stable", "description": "Optimistic rollups mature"}
    ]
    return narratives