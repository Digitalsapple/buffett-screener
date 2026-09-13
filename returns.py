import yfinance as yf
import pandas as pd
from companies import companies, tickers
from backtest import get_top_tickers

def get_stock_return(ticker, cutoff_date):
    cutoff = pd.Timestamp(cutoff_date)
    search_start = cutoff + pd.Timedelta(days=1) # Buy on the first trading day AFTER the ranking date
    target_sell_date = cutoff + pd.DateOffset(years=1) #Sell after one year
    search_end = target_sell_date + pd.Timedelta(days=10)   # extra days in case the target date falls on a weekend or market holiday

    stock = yf.Ticker(ticker)
    data = stock.history(start=search_start,end=search_end,auto_adjust=True)

    if data.empty:
        return None

    data.index = data.index.tz_localize(None) #DEBUG: REMOVE TIMEZONES

    buy_data = data[data.index > cutoff] #first trading day

    if buy_data.empty:
        return None

    buy_row = buy_data.iloc[0]
    buy_date = buy_data.index[0]
    buy_price = buy_row["Close"]

    sell_data = data[data.index >= target_sell_date]

    if sell_data.empty:
        return None

    sell_row = sell_data.iloc[0]
    sell_date = sell_data.index[0]
    sell_price = sell_row["Close"]

    stock_return = (sell_price / buy_price) - 1

    return {
        "ticker": ticker,
        "buy_date": buy_date,
        "buy_price": buy_price,
        "sell_date": sell_date,
        "sell_price": sell_price,
        "return": stock_return
    }


def backtest_portfolio(tickers, cutoff_date):
    stock_results = []

    for ticker in tickers:
        result = get_stock_return(ticker,cutoff_date)
        if result is not None:
            stock_results.append(result)
        else:
            print("Could not calculate return for", ticker)

    if not stock_results:
        return None

    # Portfolio Weight: each stock gets 10% when all 10 are available
    portfolio_return = sum(
        result["return"]
        for result in stock_results
    ) / len(stock_results)

    spy_result = get_stock_return("SPY",cutoff_date) #benchmark

    if spy_result is None:
        spy_return = None
        difference = None
    else:
        spy_return = spy_result["return"]
        difference = portfolio_return - spy_return

    return {
        "cutoff_date": cutoff_date,
        "stocks": stock_results,
        "portfolio_return": portfolio_return,
        "spy_return": spy_return,
        "difference": difference
    }


if __name__ == "__main__":
    all_results = []

    cutoff_dates = [
        "2022-09-10",
        "2023-09-10",
        "2024-09-10"
    ]

    for cutoff_date in cutoff_dates:
        top_tickers, top_companies, failed = get_top_tickers(cutoff_date)
        print("\n" + "=" * 60)
        print("BACKTEST:", cutoff_date)
        print("=" * 60)
        result = backtest_portfolio(top_tickers,cutoff_date)

        if result is None:
            print("Backtest failed.")
            continue

        all_results.append(result)

        print("\nINDIVIDUAL STOCK RETURNS\n")

        for stock in result["stocks"]:
            print(stock["ticker"],"|",stock["buy_date"].date(),"→",stock["sell_date"].date(),"|",f'{stock["return"]:.2%}')
        print("\nRESULT")
        print("Screener portfolio:",f'{result["portfolio_return"]:.2%}')
        if result["spy_return"] is not None:
            print("S&P 500 (SPY):",f'{result["spy_return"]:.2%}')
            print("Difference:",f'{result["difference"] * 100:.2f}',"percentage points")

    print("\n" + "=" * 60)
    print("OVERALL BACKTEST SUMMARY")
    print("=" * 60)

    if all_results:
        average_portfolio_return = sum(
            result["portfolio_return"]
            for result in all_results
        ) / len(all_results)

        valid_spy_results = [
            result
            for result in all_results
            if result["spy_return"] is not None
        ]

        average_spy_return = sum(
            result["spy_return"]
            for result in valid_spy_results
        ) / len(valid_spy_results)

        average_difference = (average_portfolio_return - average_spy_return)
        outperform_count = sum(
            1
            for result in valid_spy_results
            if result["portfolio_return"] > result["spy_return"]
        )

        print("Average screener return:",f"{average_portfolio_return:.2%}")
        print("Average S&P 500 return:",f"{average_spy_return:.2%}")
        print("Average difference:",f"{average_difference * 100:.2f}","percentage points")        
        print("Periods outperforming S&P 500:",outperform_count,"/",len(valid_spy_results))