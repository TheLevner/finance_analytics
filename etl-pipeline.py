import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql://finance_user:PSWD@localhost:5433/finance_analytics"
engine = create_engine(DB_URL)

STOCKS = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "TSM", "META", "AVGO", "SPCX", "LLY"]

def load_assets():
    ticker_to_id = {}

    with engine.begin() as conn:
        for ticker in STOCKS:
            select_query = text("SELECT id FROM assets WHEER ticker = :ticker")
            exist_row = conn.execute(select_query, {"ticker":ticker}).fetchone()

            if exist_row:
                ticker_to_id[ticker] = exist_row[0]
                continue

            print(f"Получение данныех нового актива {ticker}")
            info = yf.Ticker(ticker).info
            company_name = info.get("shortName") or info.get("longName")
            sector = info.get("sector")

            insert_query = text("""
                INSERT INTO assets (ticker, company_name, sector)
                VALUES (:ticker, :name, :sector)
                RETURNING id;
            """)
            result = conn.execute(insert_query , {"ticker": ticker, "name": company_name, "sector": sector})
            ticker_to_id[ticker] = result.fetchone()[0]
    return ticker_to_id