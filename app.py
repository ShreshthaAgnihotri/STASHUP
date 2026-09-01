# ============================================================
# FINMIND AI
# MAIN FLASK SERVER
# M1 + M2 + M3 + M4 + M5
# ============================================================

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import importlib
import traceback


# ============================================================
# FLASK SETUP
# ============================================================

app = Flask(__name__)


# ============================================================
# MODULE LOADING
# ============================================================

M1 = None
M2 = None
M3 = None
M4 = None


# ---------- M1 ----------

try:
    M1 = importlib.import_module("M1")
    print("✅ M1 loaded")

except Exception as e:
    print("❌ M1 error:", e)


# ---------- M2 ----------

try:
    M2 = importlib.import_module("m2")
    print("✅ M2 loaded")

except Exception as e:
    print("⚠️ M2 package not loaded:", e)


# ---------- M3 ----------

try:
    M3 = importlib.import_module("M3")
    print("✅ M3 loaded")

except Exception as e:
    print("❌ M3 error:", e)


# ---------- M4 ----------

try:
    M4 = importlib.import_module("M4")
    print("✅ M4 loaded")

except Exception as e:
    print("❌ M4 error:", e)


# ============================================================
# HELPER FUNCTION
# ============================================================

def find_function(module, possible_names):

    if module is None:
        return None

    for name in possible_names:

        function = getattr(module, name, None)

        if callable(function):
            return function

    return None


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({

        "status": "running",

        "modules": {

            "M1": M1 is not None,

            "M2": M2 is not None,

            "M3": M3 is not None,

            "M4": M4 is not None,

            "M5": True

        },

        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    })


# ============================================================
# M1 - MARKET DATA
# ============================================================

@app.route("/api/market/<symbol>")
def market_data(symbol):

    try:

        if M1 is None:

            return jsonify({

                "success": False,

                "error": "M1 module not loaded"

            }), 500


        function = find_function(

            M1,

            [

                "get_market_data",

                "fetch_market_data",

                "get_stock_data",

                "fetch_stock_data",

                "market_data"

            ]

        )


        if function is None:

            return jsonify({

                "success": False,

                "error":
                    "M1 function not found"

            }), 500


        result = function(
            symbol.upper()
        )


        return jsonify({

            "success": True,

            "module": "M1",

            "symbol": symbol.upper(),

            "data": result

        })


    except Exception as e:

        print(traceback.format_exc())

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# M2 - SIGNAL
# ============================================================

@app.route("/api/signal/<symbol>")
def signal(symbol):

    try:

        if M2 is None:

            return jsonify({

                "success": False,

                "error": "M2 module not loaded"

            }), 500


        function = find_function(

            M2,

            [

                "generate_signal",

                "get_signal",

                "analyze_stock",

                "calculate_signal",

                "run_signal_engine"

            ]

        )


        if function is None:

            return jsonify({

                "success": False,

                "error":
                    "M2 signal function not found"

            }), 500


        result = function(
            symbol.upper()
        )


        return jsonify({

            "success": True,

            "module": "M2",

            "symbol": symbol.upper(),

            "signal": result

        })


    except Exception as e:

        print(traceback.format_exc())

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# M3 - RAG
# ============================================================

@app.route(
    "/api/rag",
    methods=["POST"]
)
def rag():

    try:

        if M3 is None:

            return jsonify({

                "success": False,

                "error": "M3 module not loaded"

            }), 500


        data = request.get_json(
            silent=True
        ) or {}


        question = data.get(
            "question",
            ""
        ).strip()


        if not question:

            return jsonify({

                "success": False,

                "error":
                    "Question is required"

            }), 400


        function = find_function(

            M3,

            [

                "generate_rag_response",

                "rag_query",

                "query_rag",

                "ask_rag",

                "search_documents",

                "generate_response"

            ]

        )


        if function is None:

            return jsonify({

                "success": False,

                "error":
                    "M3 RAG function not found"

            }), 500


        result = function(question)


        return jsonify({

            "success": True,

            "module": "M3",

            "question": question,

            "data": result

        })


    except Exception as e:

        print(traceback.format_exc())

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# M4 - MULTI AGENT
# ============================================================

@app.route(
    "/api/agents",
    methods=["POST"]
)
def agents():

    try:

        if M4 is None:

            return jsonify({

                "success": False,

                "error": "M4 module not loaded"

            }), 500


        data = request.get_json(
            silent=True
        ) or {}


        symbol = data.get(
            "symbol",
            "RELIANCE"
        ).upper()


        risk_profile = data.get(

            "risk_profile",

            "MODERATE"

        ).upper()


        market = data.get(
            "market",
            {}
        )


        rag = data.get(
            "rag",
            {}
        )


        function = find_function(

            M4,

            [

                "run_multi_agent_analysis",

                "run_agents",

                "multi_agent_analysis",

                "analyze",

                "run_analysis",

                "synthesize"

            ]

        )


        if function is None:

            return jsonify({

                "success": False,

                "error":
                    "M4 agent function not found"

            }), 500


        # Try the most useful argument structure first

        try:

            result = function(

                market,

                rag,

                risk_profile

            )

        except TypeError:

            try:

                result = function(

                    symbol,

                    market,

                    rag,

                    risk_profile

                )

            except TypeError:

                result = function(
                    symbol
                )


        return jsonify({

            "success": True,

            "module": "M4",

            "symbol": symbol,

            "risk_profile":
                risk_profile,

            "intelligence": result

        })


    except Exception as e:

        print(traceback.format_exc())

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# COMPLETE PIPELINE
#
# M1 → M2 → M3 → M4 → M5
# ============================================================

@app.route(
    "/api/analyze/<symbol>"
)
def complete_analysis(symbol):

    try:

        symbol = symbol.upper()


        risk_profile = request.args.get(

            "risk_profile",

            "MODERATE"

        ).upper()


        # ====================================================
        # M1
        # ====================================================

        m1_result = {}

        if M1 is not None:

            function = find_function(

                M1,

                [

                    "get_market_data",

                    "fetch_market_data",

                    "get_stock_data",

                    "fetch_stock_data",

                    "market_data"

                ]

            )

            if function:

                try:

                    m1_result = function(symbol)

                except Exception as e:

                    m1_result = {

                        "error": str(e)

                    }


        # ====================================================
        # M2
        # ====================================================

        m2_result = {}

        if M2 is not None:

            function = find_function(

                M2,

                [

                    "generate_signal",

                    "get_signal",

                    "analyze_stock",

                    "calculate_signal",

                    "run_signal_engine"

                ]

            )

            if function:

                try:

                    m2_result = function(symbol)

                except Exception as e:

                    m2_result = {

                        "error": str(e)

                    }


        # ====================================================
        # M3
        # ====================================================

        m3_result = {}

        if M3 is not None:

            function = find_function(

                M3,

                [

                    "generate_rag_response",

                    "rag_query",

                    "query_rag",

                    "ask_rag",

                    "generate_response"

                ]

            )

            if function:

                try:

                    question = (

                        f"What are the important "
                        f"financial developments and "
                        f"risks for {symbol}?"

                    )

                    m3_result = function(question)

                except Exception as e:

                    m3_result = {

                        "error": str(e),

                        "grounded": False

                    }


        # ====================================================
        # M4
        # ====================================================

        m4_result = {}

        if M4 is not None:

            function = find_function(

                M4,

                [

                    "run_multi_agent_analysis",

                    "run_agents",

                    "multi_agent_analysis",

                    "analyze",

                    "run_analysis",

                    "synthesize"

                ]

            )

            if function:

                try:

                    try:

                        m4_result = function(

                            m1_result,

                            m3_result,

                            risk_profile

                        )

                    except TypeError:

                        m4_result = function(
                            symbol
                        )

                except Exception as e:

                    m4_result = {

                        "error": str(e)

                    }


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        return jsonify({

            "success": True,

            "symbol": symbol,

            "risk_profile":
                risk_profile,

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),


            "market_data": m1_result,

            "signals": m2_result,

            "rag": m3_result,

            "multi_agent": m4_result,


            "pipeline": [

                "M1 - Market Data",

                "M2 - Signal Classification",

                "M3 - RAG / Financial Documents",

                "M4 - Multi-Agent Reasoning",

                "M5 - User Interface"

            ]

        })


    except Exception as e:

        print(traceback.format_exc())

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# WATCHLIST
# ============================================================

@app.route("/api/watchlist")
def watchlist():

    stocks = [

        "RELIANCE",
        "TCS",
        "INFY",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "ITC",
        "LT",
        "AXISBANK",
        "BHARTIARTL",
        "KOTAKBANK",
        "HINDUNILVR",
        "MARUTI",
        "SUNPHARMA",
        "TITAN",
        "BAJFINANCE",
        "ASIANPAINT",
        "WIPRO",
        "TECHM",
        "ADANIENT",
        "NTPC",
        "POWERGRID",
        "TATASTEEL",
        "ONGC",
        "COALINDIA"

    ]


    return jsonify({

        "success": True,

        "stocks": stocks

    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({

        "success": False,

        "error":
            "Endpoint not found"

    }), 404


@app.errorhandler(500)
def internal_error(error):

    return jsonify({

        "success": False,

        "error":
            "Internal server error"

    }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("              FINMIND AI")
    print("       MULTI-AGENT INVESTMENT SYSTEM")
    print("=" * 60)

    print()

    print(
        "M1 Market Data   :",
        "✅ LOADED"
        if M1
        else
        "❌ NOT LOADED"
    )

    print(
        "M2 Signal Engine :",
        "✅ LOADED"
        if M2
        else
        "⚠️ CHECK M2"
    )

    print(
        "M3 RAG           :",
        "✅ LOADED"
        if M3
        else
        "❌ NOT LOADED"
    )

    print(
        "M4 Multi-Agent   :",
        "✅ LOADED"
        if M4
        else
        "❌ NOT LOADED"
    )

    print(
        "M5 Frontend      :",
        "✅ READY"
    )

    print()

    print(
        "🌐 Website:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    print("=" * 60)

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )