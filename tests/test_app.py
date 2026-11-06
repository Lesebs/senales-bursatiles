import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from datetime import date

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import main
from database import Base, engine

client = TestClient(main.app)


def serie(valores):
    fechas = pd.date_range(
        end="2026-11-05",
        periods=len(valores),
        tz="America/New_York",
    )
    return pd.Series(valores, index=fechas, dtype=float)


@pytest.fixture(autouse=True)
def base_limpia():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


def test_tendencia_alcista():
    resultado = main.calcular_senal("aapl", serie(list(range(1, 61))))

    assert resultado["ticker"] == "AAPL"
    assert resultado["sma20"] == 50.5
    assert resultado["sma50"] == 35.5
    assert resultado["tendencia"] == "alcista"


def test_tendencia_bajista():
    resultado = main.calcular_senal("aapl", serie(list(range(60, 0, -1))))

    assert resultado["tendencia"] == "bajista"


def test_ignora_ultimo_precio_vacio():
    valores = list(range(1, 61)) + [float("nan")]
    resultado = main.calcular_senal("aapl", serie(valores))

    assert resultado["precio"] == 60
    assert resultado["fecha"] == date(2026, 11, 4)


def test_rechaza_pocos_datos():
    with pytest.raises(ValueError):
        main.calcular_senal("aapl", serie(list(range(1, 11))))


def test_no_duplica_la_misma_fecha(monkeypatch):
    class TickerFalso:
        def __init__(self, ticker):
            pass

        def history(self, period):
            return pd.DataFrame({"Close": serie(list(range(1, 61)))})

    monkeypatch.setattr(main.yf, "Ticker", TickerFalso)

    assert client.get("/signal/AAPL").status_code == 200
    assert client.get("/signal/AAPL").status_code == 200

    historial = client.get("/history/AAPL").json()
    assert len(historial) == 1
    assert historial[0]["fecha"] == "2026-11-05"


def test_ticker_sin_datos(monkeypatch):
    class TickerVacio:
        def __init__(self, ticker):
            pass

        def history(self, period):
            return pd.DataFrame()

    monkeypatch.setattr(main.yf, "Ticker", TickerVacio)

    assert client.get("/signal/NOEXISTE").status_code == 404