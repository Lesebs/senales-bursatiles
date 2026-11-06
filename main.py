import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI(title="Señales bursátiles")

@app.get("/")
def home():
    return FileResponse("index.html")

@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    data = yf.Ticker(ticker).history(period="6mo")

    if len(data) < 50:
        raise HTTPException(status_code=404, detail="No hay datos suficientes")

    close = data["Close"]
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]

    return {
        "ticker": ticker.upper(),
        "precio": round(float(close.iloc[-1]), 2),
        "sma20": round(float(sma20), 2),
        "sma50": round(float(sma50), 2),
        "tendencia": "alcista" if sma20 > sma50 else "bajista",
    }