import yfinance as yf
import pandas as pd
from companies import companies, tickers, cutoff_dates
from backtest import get_top_tickers
from pathlib import Path

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

    if len(stock_results) != len(tickers):
        print("Incomplete portfolio: missing return data")
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
    ranking_rows = []
    holding_rows = []
    summary_rows = []
    excluded_rows = []

    for cutoff_date in cutoff_dates:
        top_tickers, top_companies, failed, ranked_companies = get_top_tickers(cutoff_date)
        #CSV FILE ADDITION
        for rank, company in enumerate(ranked_companies, start=1):
            row = {
                "cutoff_date": cutoff_date,
                "rank": rank,
                "ticker": tickers[company["name"]],
                "company": company["company"],
                "cik": company["cik"],
                "total_score": company["total_score"],
                "selected_top_10": rank <= 10,
            }

            for name, value in company["indicators"].items():
                row["indicator_" + name] = value

            for name, points in company["scores"].items():
                row["points_" + name] = points

            ranking_rows.append(row)

        for failure in failed:
            excluded_rows.append({
                "cutoff_date": cutoff_date,
                "company": failure["company"],
                "reason": failure["reason"],
            })
        #ENDS HERE

        print("\n" + "=" * 60)
        print("BACKTEST:", cutoff_date)
        print("=" * 60)
        result = backtest_portfolio(top_tickers,cutoff_date)

        if result is None:
            print("Backtest failed.")
            continue

        all_results.append(result)
        for stock in result["stocks"]:
            holding_rows.append({
                "cutoff_date": cutoff_date,
                "ticker": stock["ticker"],
                "initial_weight_pct": 100 / len(top_tickers),
                "buy_date": stock["buy_date"].date().isoformat(),
                "sell_date": stock["sell_date"].date().isoformat(),
                "adjusted_buy_price": stock["buy_price"],
                "adjusted_sell_price": stock["sell_price"],
                "return_pct": stock["return"] * 100,
            })

        summary_rows.append({
            "cutoff_date": cutoff_date,
            "selected_stock_count": len(top_tickers),
            "returned_stock_count": len(result["stocks"]),
            "complete_portfolio": len(result["stocks"]) == len(top_tickers),
            "portfolio_return_pct": result["portfolio_return"] * 100,
            "spy_return_pct": (
                result["spy_return"] * 100
                if result["spy_return"] is not None else None
            ),
            "difference_percentage_points": (
                result["difference"] * 100
                if result["difference"] is not None else None
            ),
        })

        print("\nINDIVIDUAL STOCK RETURNS\n")

        for stock in result["stocks"]:
            print(stock["ticker"],"|",stock["buy_date"].date(),"→",stock["sell_date"].date(),"|",f'{stock["return"]:.2%}')
        print("\nRESULT")
        print("Screener portfolio:",f'{result["portfolio_return"]:.2%}')
        if result["spy_return"] is not None:
            print("S&P 500 (SPY):",f'{result["spy_return"]:.2%}')
            print("Difference:",f'{result["difference"] * 100:.2f}',"percentage points")

    #CSV
    output_folder = Path(__file__).resolve().parent / "output"
    output_folder.mkdir(exist_ok=True)

    pd.DataFrame(ranking_rows).to_csv(
        output_folder / "rankings.csv",
        index=False,
    )

    pd.DataFrame(holding_rows).to_csv(
        output_folder / "holdings.csv",
        index=False,
    )

    pd.DataFrame(summary_rows).to_csv(
        output_folder / "backtest_summary.csv",
        index=False,
    )

    pd.DataFrame(
        excluded_rows,
        columns=["cutoff_date", "company", "reason"],
    ).to_csv(
        output_folder / "excluded_companies.csv",
        index=False,
    )

    print("CSV files saved to:", output_folder)


    print("\n" + "=" * 60)
    print("OVERALL BACKTEST SUMMARY")
    print("=" * 60)

    #replace if all results
    valid_spy_results = [
        result
        for result in all_results
        if result["spy_return"] is not None
    ]

    if valid_spy_results:
        period_count = len(valid_spy_results)

        average_portfolio_return = sum(
            result["portfolio_return"]
            for result in valid_spy_results
        ) / period_count

        average_spy_return = sum(
            result["spy_return"]
            for result in valid_spy_results
        ) / period_count

        average_difference = (
            average_portfolio_return - average_spy_return
        )

        outperform_count = sum(
            1
            for result in valid_spy_results
            if result["portfolio_return"] > result["spy_return"]
        )

        overall_rows = [
            {
                "metric": "Periods with portfolio and benchmark results",
                "value": period_count,
                "unit": "periods",
            },
            {
                "metric": "Average screener return",
                "value": average_portfolio_return * 100,
                "unit": "percent",
            },
            {
                "metric": "Average SPY return",
                "value": average_spy_return * 100,
                "unit": "percent",
            },
            {
                "metric": "Average difference",
                "value": average_difference * 100,
                "unit": "percentage points",
            },
            {
                "metric": "Periods outperforming SPY",
                "value": outperform_count,
                "unit": "periods",
            },
        ]

        print("Average screener return:", f"{average_portfolio_return:.2%}")
        print("Average SPY return:", f"{average_spy_return:.2%}")
        print(
            "Average difference:",
            f"{average_difference * 100:.2f}",
            "percentage points",
        )
        print("Periods outperforming SPY:", outperform_count, "/", period_count)

    else:
        overall_rows = [
            {
                "metric": "Periods with portfolio and benchmark results",
                "value": 0,
                "unit": "periods",
            }
        ]
        print("No comparable periods available.")

    pd.DataFrame(overall_rows).to_csv(
        output_folder / "overall_summary.csv",
        index=False,
    )