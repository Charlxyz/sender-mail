from flask import Flask, jsonify, request
from binance.client import Client
import pandas as pd
import threading, time, smtplib, requests
from email.mime.text import MIMEText


app = Flask(__name__)
client = Client()

# -----------------------------
#   CONFIG EMAIL
# -----------------------------
EMAIL_SENDER = "sendermail199920@gmail.com"
EMAIL_PASSWORD = "jqdt lieu vtbj dldu"
EMAIL_RECEIVER = "charly59000@orange.fr"

def send_email(subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
    except Exception as e:
        print("Erreur Email:", e)

# -----------------------------
#   FONCTIONS D'ANALYSE
# -----------------------------

def compute_ema(closes, span):
    s = pd.Series(closes)
    ema = s.ewm(span=span, adjust=False).mean()
    return ema.iloc[-1], ema.iloc[-2]

def compute_rsi(closes, period=14):
    s = pd.Series(closes)
    delta = s.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

def analyze_market(symbol="BTCUSDT", interval="1m", ema_short=20, ema_long=50, rsi_period=14):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=200)
    closes = [float(k[4]) for k in klines]

    ema_s_curr, ema_s_prev = compute_ema(closes, ema_short)
    ema_l_curr, ema_l_prev = compute_ema(closes, ema_long)
    rsi = compute_rsi(closes, rsi_period)

    result = {
        "symbol": symbol,
        "interval": interval,
        "close": closes[-1],
        "ema_short": ema_s_curr,
        "ema_long": ema_l_curr,
        "rsi": rsi,
        "signal_ema": None,
        "signal_rsi": None
    }

    # -----------------------------
    #   SIGNAL EMA
    # -----------------------------
    if ema_s_prev < ema_l_prev and ema_s_curr > ema_l_curr:
        result["signal_ema"] = "BUY"
        message = f"📈 Signal EMA BUY sur {symbol} ({interval})"
        send_email("Signal EMA BUY", message)

    elif ema_s_prev > ema_l_prev and ema_s_curr < ema_l_curr:
        result["signal_ema"] = "SELL"
        message = f"📉 Signal EMA SELL sur {symbol} ({interval})"
        send_email("Signal EMA SELL", message)

    # -----------------------------
    #   SIGNAL RSI
    # -----------------------------
    if rsi > 70:
        result["signal_rsi"] = "OVERBOUGHT"
        message = f"⚠️ RSI Overbought sur {symbol} ({interval}) — RSI = {rsi:.2f}"
        send_email("RSI Overbought", message)

    elif rsi < 30:
        result["signal_rsi"] = "OVERSOLD"
        message = f"⚠️ RSI Oversold sur {symbol} ({interval}) — RSI = {rsi:.2f}"
        send_email("RSI Oversold", message)

    return result

# -----------------------------
#   API FLASK
# -----------------------------

@app.route("/analyze", methods=["GET"])
def api_analyze():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1m")

    data = analyze_market(symbol=symbol, interval=interval)
    return jsonify(data)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"})

def auto_ping():
    while True:
        try:
            requests.get("/ping")
        except Exception as e:
            print("Erreur auto-ping:", e)
        time.sleep(300)  # 300 secondes = 5 minutes

# -----------------------------
#   LANCEMENT
# -----------------------------

if __name__ == "__main__":
    threading.Thread(target=auto_ping, daemon=True).start()
    app.run(debug=True)

# EXEMPLE DE REQUÊTE
# http://127.0.0.1:5000/analyze
# http://127.0.0.1:5000/analyze?symbol=BTCUSD&interval=5m