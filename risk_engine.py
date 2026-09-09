import numpy as np
import pandas as pd
from sqlalchemy import text, bindparam
from db_connection import get_engine

def load_portfolio(engine, portfolio_name):
    query = text("""
        SELECT ticker, weight
        FROM portfolios
        WHERE portfolio_name = :portfolio_name
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"portfolio_name": portfolio_name})
        rows = result.fetchall()

    if not rows:
        raise ValueError(f"No portfolio found named '{portfolio_name}'")
    
    return {row.ticker:float(row.weight) for row in rows}


def load_prices(engine, tickers):
    query = text("""
        SELECT ticker, price_date, close_price
        FROM prices
        WHERE ticker IN :tickers
        ORDER BY price_date
    """).bindparams(bindparam("tickers", expanding = True))
                 
    with engine.connect() as conn:
        df = pd.read_sql(
            query, conn, params={"tickers": list(tickers)}
        )
    
    if df.empty:
        raise ValueError(f"No price data found for tickers: {tickers}")
    
    wide = df.pivot(index="price_date", columns = "ticker", values = "close_price")
    wide = wide.sort_index()
    wide = wide.astype(float)
    return wide


def compute_returns(prices):
    return np.log(prices/prices.shift(1)).dropna()

def portfolio_returns(returns, weights: dict):
    assets = returns.columns 
    w = np.array([weights[a] for a in assets])
    port_ret = returns[assets].values @ w

    return pd.Series(port_ret, index= returns.index, name = "Portfolio")


def historical_var(returns, confidence=0.95, portfolio_value = 1.0):
    alpha = 1 -confidence
    var_return = -np.percentile(returns, alpha*100)

    return var_return * portfolio_value

def expected_shortfall(returns, confidence = 0.95, portfolio_value = 1.0):
    alpha = 1 - confidence
    var_return = np.percentile(returns, alpha * 100)
    tail_losses = returns[returns <= var_return]
    es_return = -tail_losses.mean()

    return es_return * portfolio_value

def monte_carlo_var(returns, confidence = 0.95, portfolio_value = 1.0, n_simulaitons = 10000, seed = 42):
    rng = np.random.default_rng(seed)
    mu = returns.mean()
    sigma = returns.std()

    simulated_returns = rng.normal(mu, sigma, n_simulaitons)

    alpha = 1 - confidence
    var_return = -np.percentile(simulated_returns, alpha * 100)

    return var_return * portfolio_value

def save_risk_result(engine, portfolio_name, run_date, confidence, method, var_value, es_value):
    insert_query = text("""
        INSERT INTO risk_results
            (portfolio_name, run_date, confidence_level, method, var_value, expected_shortfall)
        VALUES (:portfolio_name, :run_date, :confidence_level, :method, :var_value, :expected_shortfall)
    """)

    with engine.begin() as conn:
        conn.execute(insert_query, {
            "portfolio_name": portfolio_name,
            "run_date": run_date,
            "confidence_level": confidence,
            "method": method,
            "var_value": round(float(var_value), 2),
            "expected_shortfall": round(float(es_value), 2),
        })

if __name__ == "__main__":
    engine = get_engine()

    portfolio_name = "FirstPortfolio"
    portfolio_value = 1000000
    confidence = [0.95, 0.99]

    print(f"Loading portfolio '{portfolio_name}'...")

    weights = load_portfolio(engine, portfolio_name)

    print(f"    Holdings: {weights} ")

    print("Loading history prices...")

    prices = load_prices(engine, list(weights.keys()))

    print (f"   Loaded {len(prices)} days of prices for {list(prices.columns)}")

    returns = compute_returns(prices)
    port_ret = portfolio_returns(returns, weights)

    run_date = prices.index.max()

    print(f"\nCalculating risk of metrics as of {run_date}...\n")

    for confidence in confidence:
        hist_var = historical_var(port_ret, confidence, portfolio_value)
        hist_es = expected_shortfall(port_ret, confidence, portfolio_value)
        mc_var = monte_carlo_var(port_ret, confidence, portfolio_value)

        print(f"--- {confidence:.0%} confidence ---" )
        print(f"    Historical VaR: £{hist_var:,.2f}")
        print(f"    Expected Shortfall: £{hist_es:,.2f}")
        print(f"    Monte Carlo VaR: £{mc_var:,.2f}")

        save_risk_result(engine, portfolio_name, run_date, confidence, "historical", hist_var, hist_es)
        save_risk_result(engine, portfolio_name, run_date, confidence, "monte_carlo", mc_var, hist_es)

    print("\nRisk engine run complete - results saved to risk_results table.")