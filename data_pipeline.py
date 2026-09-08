import pandas as pd
import yfinance as yf
from sqlalchemy import text
from db_connection import get_engine

def get_prices(tickers, start_date = "2019-01-01", end_date = None):
    raw = yf.download(tickers, start = start_date, end = end_date)["Close"]
    long_df = raw.reset_index().melt(
        id_vars="Date", var_name="ticker", value_name="close_price"
    )
    long_df = long_df.rename(columns={"Date": "price_date"})
    long_df = long_df.dropna(subset=["close_price"])

    return long_df


def insert_prices(engine, prices_df):
    insert_query = text(""" 
        INSERT IGNORE INTO prices (ticker, price_date, close_price)
        VALUES (:ticker, :price_date, :close_price)
    """)
    
    records = prices_df.to_dict(orient = "records")

    with engine.begin() as conn:
        conn.execute(insert_query, records)
    
    print(f"Inserted (or skipped existing) {len(records)} price rows.")


def insert_portfolio(engine, portfolio_name, weights: dict):
    if not abs(sum(weights.values()) - 1.0) < 1e-6:
        raise ValueError(f"Weights must sum to 1.0, got {sum(weights.values())}")

    insert_query = text(""" 
        INSERT IGNORE INTO portfolios (portfolio_name, ticker, weight)
        VALUES (:portfolio_name, :ticker, :weight)
    """)

    records = [
        {"portfolio_name": portfolio_name, "ticker": ticker, "weight": weight}
        for ticker, weight in weights.items()
    ]

    with engine.begin() as conn:
        conn.execute(insert_query, records)
    
    print(f"Inserted porfolio {portfolio_name} with {len(records)} holdings")

if __name__ == "__main__":
    engine = get_engine()

    portfolio_name = "FirstPortfolio"
    weights = {
        "AAPL": 0.4,
        "MSFT": 0.3,
        "JPM": 0.3,
    }

    print("Fetching price data...")
    prices_df = get_prices(tickers=list(weights.keys()), start_date="2019-01-01")

    print("Inserting prices into database...")
    insert_prices(engine, prices_df)

    print("Inserting portfolio definition...")
    insert_portfolio(engine, portfolio_name, weights)

    print("Data pipeline complete")




