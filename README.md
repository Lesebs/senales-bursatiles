\# Señales bursátiles



Aplicación web que consulta precios históricos de acciones, calcula medias móviles y guarda una señal diaria por ticker en PostgreSQL.



> Proyecto educativo. No es una recomendación de inversión.



\## Arquitectura



```text

Navegador → FastAPI → Yahoo Finance

&#x20;              ↓

&#x20;          PostgreSQL

```



\## Tecnologías



\- Python y FastAPI

\- PostgreSQL y SQLAlchemy

\- Docker y Docker Compose

\- Pytest



\## Cómo funciona



\- Compara la media móvil de 20 días con la de 50 días.

\- Si la de 20 es mayor, la tendencia es alcista. Si no, es bajista.

\- Ignora precios vacíos.

\- Guarda una sola señal por ticker y fecha.



\## Ejecutar el proyecto



Requisito: Docker Desktop abierto.



```powershell

copy .env.example .env

docker compose up -d --build

```



Abre `http://127.0.0.1:8000`.



\## Ejecutar las pruebas



```powershell

python -m venv .venv

.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt -r requirements-dev.txt

python -m pytest

```



\## Endpoints



\- `GET /signal/{ticker}`: calcula y guarda la señal.

\- `GET /history/{ticker}`: muestra hasta 20 señales guardadas.

\- `GET /docs`: abre la documentación interactiva.



\## Limitaciones



\- Yahoo Finance se consulta con `yfinance`, una librería no oficial.

\- Las medias móviles solo describen la tendencia pasada.

