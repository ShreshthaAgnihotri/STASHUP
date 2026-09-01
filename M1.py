from flask import Flask, jsonify
import random
from datetime import datetime

app = Flask(__name__)


# =========================================================
# M1 - MARKET DATA
# =========================================================

STOCKS = {

    "RELIANCE": {
        "name": "Reliance Industries",
        "price": 1452.35,
        "volume": 1420000
    },

    "TCS": {
        "name": "Tata Consultancy Services",
        "price": 4215.50,
        "volume": 850000
    },

    "INFY": {
        "name": "Infosys",
        "price": 1885.20,
        "volume": 1120000
    },

    "HDFCBANK": {
        "name": "HDFC Bank",
        "price": 1742.80,
        "volume": 980000
    },

    "ICICIBANK": {
        "name": "ICICI Bank",
        "price": 1298.40,
        "volume": 1050000
    },

    "SBIN": {
        "name": "State Bank of India",
        "price": 812.60,
        "volume": 1650000
    },

    "BHARTIARTL": {
        "name": "Bharti Airtel",
        "price": 1845.30,
        "volume": 920000
    },

    "ITC": {
        "name": "ITC Limited",
        "price": 428.75,
        "volume": 1350000
    },

    "LT": {
        "name": "Larsen & Toubro",
        "price": 3678.20,
        "volume": 620000
    },

    "AXISBANK": {
        "name": "Axis Bank",
        "price": 1185.40,
        "volume": 780000
    },

    "KOTAKBANK": {
        "name": "Kotak Mahindra Bank",
        "price": 2015.60,
        "volume": 540000
    },

    "HINDUNILVR": {
        "name": "Hindustan Unilever",
        "price": 2695.80,
        "volume": 410000
    },

    "MARUTI": {
        "name": "Maruti Suzuki",
        "price": 12450.00,
        "volume": 280000
    },

    "TATAMOTORS": {
        "name": "Tata Motors",
        "price": 1025.70,
        "volume": 1450000
    },

    "SUNPHARMA": {
        "name": "Sun Pharmaceutical",
        "price": 1785.25,
        "volume": 690000
    },

    "ADANIENT": {
        "name": "Adani Enterprises",
        "price": 2485.60,
        "volume": 520000
    },

    "ADANIPORTS": {
        "name": "Adani Ports",
        "price": 1398.45,
        "volume": 610000
    },

    "ASIANPAINT": {
        "name": "Asian Paints",
        "price": 3125.30,
        "volume": 350000
    },

    "WIPRO": {
        "name": "Wipro",
        "price": 565.40,
        "volume": 1250000
    },

    "HCLTECH": {
        "name": "HCL Technologies",
        "price": 1645.80,
        "volume": 720000
    },

    "TECHM": {
        "name": "Tech Mahindra",
        "price": 1788.50,
        "volume": 480000
    },

    "BAJFINANCE": {
        "name": "Bajaj Finance",
        "price": 8950.25,
        "volume": 390000
    },

    "ULTRACEMCO": {
        "name": "UltraTech Cement",
        "price": 12450.70,
        "volume": 210000
    },

    "TITAN": {
        "name": "Titan Company",
        "price": 3655.90,
        "volume": 330000
    },

    "NTPC": {
        "name": "NTPC Limited",
        "price": 385.65,
        "volume": 1180000
    },

    "POWERGRID": {
        "name": "Power Grid Corporation",
        "price": 345.80,
        "volume": 970000
    },

    "ONGC": {
        "name": "Oil and Natural Gas Corporation",
        "price": 312.45,
        "volume": 1350000
    },

    "COALINDIA": {
        "name": "Coal India",
        "price": 485.30,
        "volume": 880000
    },

    "JSWSTEEL": {
        "name": "JSW Steel",
        "price": 1125.60,
        "volume": 760000
    },

    "TATASTEEL": {
        "name": "Tata Steel",
        "price": 185.75,
        "volume": 2100000
    }
}


# =========================================================
# RSI CALCULATION
# =========================================================

def calculate_rsi(price_change):

    if price_change > 1:
        rsi = random.uniform(60, 75)

    elif price_change < -1:
        rsi = random.uniform(25, 40)

    else:
        rsi = random.uniform(45, 60)

    return round(rsi, 2)


# =========================================================
# SIGNAL GENERATION
# =========================================================

def generate_signal(price_change, volume_change, rsi):

    score = 0

    # PRICE MOMENTUM
    if price_change > 0.5:
        score += 1

    elif price_change < -0.5:
        score -= 1


    # VOLUME
    if volume_change > 10:
        score += 1

    elif volume_change < -10:
        score -= 1


    # RSI
    if 50 <= rsi <= 70:
        score += 1

    elif rsi > 70:
        score -= 1

    elif rsi < 30:
        score -= 1


    # FINAL SIGNAL
    if score >= 2:
        signal = "BULLISH"

    elif score <= -2:
        signal = "BEARISH"

    else:
        signal = "NEUTRAL"


    # CONFIDENCE
    confidence = min(
        95,
        60 + abs(score) * 10 + random.randint(0, 10)
    )

    return signal, confidence


# =========================================================
# GET MARKET DATA FOR ONE STOCK
# =========================================================

def get_market_data(symbol):

    symbol = symbol.upper()

    if symbol not in STOCKS:
        return None


    stock = STOCKS[symbol]

    old_price = stock["price"]
    old_volume = stock["volume"]


    # -----------------------------------------------------
    # SIMULATED PRICE MOVEMENT
    # -----------------------------------------------------

    price_change = random.uniform(-1.5, 1.5)

    new_price = old_price * (
        1 + price_change / 100
    )


    # -----------------------------------------------------
    # SIMULATED VOLUME
    # -----------------------------------------------------

    volume_change = random.uniform(-20, 30)

    new_volume = int(
        old_volume * (
            1 + volume_change / 100
        )
    )


    # -----------------------------------------------------
    # UPDATE STOCK
    # -----------------------------------------------------

    stock["price"] = round(
        new_price,
        2
    )

    stock["volume"] = new_volume


    # -----------------------------------------------------
    # RSI
    # -----------------------------------------------------

    rsi = calculate_rsi(
        price_change
    )


    # -----------------------------------------------------
    # SIGNAL
    # -----------------------------------------------------

    signal, confidence = generate_signal(
        price_change,
        volume_change,
        rsi
    )


    # -----------------------------------------------------
    # SENTIMENT
    # -----------------------------------------------------

    if signal == "BULLISH":

        sentiment = "POSITIVE"

    elif signal == "BEARISH":

        sentiment = "NEGATIVE"

    else:

        sentiment = "NEUTRAL"


    # -----------------------------------------------------
    # MOMENTUM
    # -----------------------------------------------------

    if abs(price_change) > 1:

        momentum = "STRONG"

    else:

        momentum = "MODERATE"


    # -----------------------------------------------------
    # RETURN DATA
    # -----------------------------------------------------

    return {

        "symbol": symbol,

        "company": stock["name"],

        "price": stock["price"],

        "previous_price": round(
            old_price,
            2
        ),

        "price_change_percent": round(
            price_change,
            2
        ),

        "volume": new_volume,

        "volume_change_percent": round(
            volume_change,
            2
        ),

        "rsi": rsi,

        "momentum": momentum,

        "signal": signal,

        "confidence": confidence,

        "sentiment": sentiment,

        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    }


# =========================================================
# GET ALL STOCK DATA
# =========================================================

def get_all_market_data():

    market_data = []

    for symbol in STOCKS:

        data = get_market_data(symbol)

        if data:

            market_data.append(data)

    return market_data


# =========================================================
# API 1
# GET ONE STOCK
# =========================================================

@app.route("/api/market/<symbol>")
def market_data_api(symbol):

    data = get_market_data(symbol)

    if data is None:

        return jsonify({
            "error": "Stock not found",
            "available_stocks": list(STOCKS.keys())
        }), 404


    return jsonify(data)


# =========================================================
# API 2
# GET ALL STOCKS
# =========================================================

@app.route("/api/market")
def all_market_data_api():

    return jsonify({
        "status": "success",
        "count": len(STOCKS),
        "stocks": get_all_market_data()
    })


# =========================================================
# API 3
# SEARCH STOCK
# =========================================================

@app.route("/api/search/<query>")
def search_stock(query):

    query = query.upper()

    results = []

    for symbol, stock in STOCKS.items():

        if (
            query in symbol
            or query in stock["name"].upper()
        ):

            results.append({
                "symbol": symbol,
                "name": stock["name"]
            })


    return jsonify({
        "query": query,
        "results": results
    })


# =========================================================
# API 4
# LIST ALL STOCK SYMBOLS
# =========================================================

@app.route("/api/stocks")
def stock_list():

    stocks = []

    for symbol, stock in STOCKS.items():

        stocks.append({
            "symbol": symbol,
            "name": stock["name"]
        })


    return jsonify({
        "count": len(stocks),
        "stocks": stocks
    })


# =========================================================
# HOME / TEST
# =========================================================

@app.route("/")
def home():

    return jsonify({

        "project": "FinSight AI",

        "module": "M1 - Market Data",

        "status": "running",

        "total_stocks": len(STOCKS),

        "endpoints": {

            "all_market_data":
                "/api/market",

            "single_stock":
                "/api/market/RELIANCE",

            "search":
                "/api/search/reliance",

            "stock_list":
                "/api/stocks"

        }

    })


# =========================================================
# START FLASK SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )