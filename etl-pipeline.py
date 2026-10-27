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
            select_query = text("SELECT id FROM assets WHERE ticker = :ticker")
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

def load_quotes(ticker_to_id):
    with engine.begin() as conn:
        for ticker, asset_id in ticker_to_id.items():
            print(f"скачиваются кодировки {ticker}")

            df = yf.download(ticker, period="3mo", progress=False)

            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]

            records = []
            for _, row in df.iterrows():
                records.append({
                    "asset_id": asset_id,
                    "date": row['date'],
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row['volume'])
                })
            quotes_query = text("""
                INSERT INTO quotes (asset_id, date, open, high, low, close, volume)
                VALUES (:asset_id, :date, :open, :high, :low, :close, :volume)
                ON CONFLICT (asset_id, date) DO NOTHING;
            """)
            conn.execute(quotes_query, records)
            print(f"котировки {ticker} загружены")

if __name__ == "__main__":
    print("Начало ETL-процесса")
    mapping = load_assets()
    load_quotes(mapping)
    print("ETL-процесс успешно завершен")