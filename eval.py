import json
from datetime import datetime, timedelta
import yfinance as yf # type: ignore

current_year = datetime.now().year
ytd_start = f"{current_year}-01-01"
ytd_end = datetime.now() - timedelta(days=10)


def change(ticker, start_date=ytd_start, end_date=ytd_end):
    if ticker[-2:].upper() == 'XX':
        return 1.0, 1.0

    first = yf.download(
        ticker,
        start=start_date,
        end=(datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=10)),
        auto_adjust=False
    )["Open"].iloc[0]

    latest = yf.download(
        ticker,
        start=end_date,
        end=end_date + timedelta(days=10),
        auto_adjust=False
    )["Open"].iloc[0]

    first_price = float(first.iloc[0]) if hasattr(first, "iloc") else float(first)
    latest_price = float(latest.iloc[0]) if hasattr(latest, "iloc") else float(latest)

    return first_price, latest_price


def dividend_yield(ticker, start_date=ytd_start, end_date=ytd_end):
    if ticker[-2:].upper() == 'XX':
        return 0.0

    holding = yf.Ticker(ticker)
    dividends = holding.dividends

    # Handle timezone consistently
    dividends.index = dividends.index.tz_localize(None)

    mask = (
        (dividends.index >= start_date) &
        (dividends.index <= end_date)
    )

    return float(dividends.loc[mask].sum())


portfolio_start = 0.0
portfolio_end = 0.0
portfolio_dividends = 0.0

with open('portfolio.json', 'r') as file:
    portfolio = json.load(file)

for ticker, shares in portfolio.items():

    start_price, end_price = change(ticker)
    dividends_per_share = dividend_yield(ticker)

    start_value = start_price * shares
    end_value = end_price * shares
    dividend_income = dividends_per_share * shares

    portfolio_start += start_value
    portfolio_end += end_value
    portfolio_dividends += dividend_income

    total_return = (
        (end_price + dividends_per_share) / start_price - 1
    ) * 100

    print(
        f"{ticker}: "
        f"Start ${start_price:.2f}, "
        f"End ${end_price:.2f}, "
        f"Dividends ${dividends_per_share:.2f}, "
        f"Return {total_return:.2f}%"
    )

portfolio_return = (
    (portfolio_end + portfolio_dividends) / portfolio_start - 1
) * 100

print("\n--- PORTFOLIO SUMMARY ---")
print(f"Starting value: ${portfolio_start:,.2f}")
print(f"Ending value: ${portfolio_end:,.2f}")
print(f"Dividend income: ${portfolio_dividends:,.2f}")
print(f"Total return: {portfolio_return:.2f}%")