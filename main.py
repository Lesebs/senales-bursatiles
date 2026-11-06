import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select

from database import Base, SessionLocal, Signal, engine

Base.metadata.create_all(engine)

app = FastAPI(title="Señales bursátiles")


@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    data = yf.Ticker(ticker).history(period="6mo")
    close = data["Close"].dropna() if "Close" in data.columns else None

    if close is None or len(close) < 50:
        raise HTTPException(status_code=404, detail="No hay datos suficientes")

    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]

    resultado = {
        "ticker": ticker.upper(),
        "precio": round(float(close.iloc[-1]), 2),
        "sma20": round(float(sma20), 2),
        "sma50": round(float(sma50), 2),
        "tendencia": "alcista" if sma20 > sma50 else "bajista",
    }

    with SessionLocal() as session:
        session.add(Signal(**resultado))
        session.commit()

    return resultado


@app.get("/history/{ticker}")
def get_history(ticker: str):
    consulta = (
        select(Signal)
        .where(Signal.ticker == ticker.upper())
        .order_by(Signal.creada_en.desc())
        .limit(20)
    )

    with SessionLocal() as session:
        filas = session.scalars(consulta).all()

        return [
            {
                "ticker": fila.ticker,
                "precio": fila.precio,
                "sma20": fila.sma20,
                "sma50": fila.sma50,
                "tendencia": fila.tendencia,
                "creada_en": fila.creada_en,
            }
            for fila in filas
        ]