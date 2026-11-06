import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select

from database import Base, SessionLocal, Signal, engine

Base.metadata.create_all(engine)

app = FastAPI(title="Señales bursátiles")


def calcular_senal(ticker, close):
    close = close.dropna()

    if len(close) < 50:
        raise ValueError("No hay datos suficientes")

    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]

    return {
        "ticker": ticker.upper(),
        "fecha": close.index[-1].date(),
        "precio": round(float(close.iloc[-1]), 2),
        "sma20": round(float(sma20), 2),
        "sma50": round(float(sma50), 2),
        "tendencia": "alcista" if sma20 > sma50 else "bajista",
    }


def guardar_senal(resultado):
    consulta = select(Signal).where(
        Signal.ticker == resultado["ticker"],
        Signal.fecha == resultado["fecha"],
    )

    with SessionLocal() as session:
        senal = session.scalar(consulta)

        if senal is None:
            session.add(Signal(**resultado))
        else:
            senal.precio = resultado["precio"]
            senal.sma20 = resultado["sma20"]
            senal.sma50 = resultado["sma50"]
            senal.tendencia = resultado["tendencia"]

        session.commit()


@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    data = yf.Ticker(ticker).history(period="6mo")

    if "Close" not in data.columns:
        raise HTTPException(status_code=404, detail="No hay datos suficientes")

    try:
        resultado = calcular_senal(ticker, data["Close"])
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from None

    guardar_senal(resultado)
    return resultado


@app.get("/history/{ticker}")
def get_history(ticker: str):
    consulta = (
        select(Signal)
        .where(Signal.ticker == ticker.upper())
        .order_by(Signal.fecha.desc())
        .limit(20)
    )

    with SessionLocal() as session:
        filas = session.scalars(consulta).all()

        return [
            {
                "ticker": fila.ticker,
                "fecha": fila.fecha,
                "precio": fila.precio,
                "sma20": fila.sma20,
                "sma50": fila.sma50,
                "tendencia": fila.tendencia,
            }
            for fila in filas
        ]