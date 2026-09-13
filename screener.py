from metrics import CAGR, net_profit_margin, calculate_std_dev, liability_to_asset_ratio, return_on_equity, free_cash_flow
from financials import get_annual_records, get_unique_periods, get_balance_on_date, filter_dates, get_revenue_periods, get_capex_periods, get_operating_cash_periods, get_equity_records
from scoring import score_ROE, score_net_margin, score_margin_consistency, score_liabilities_to_assets, score_positive_fcf, score_growth
from datetime import date

def analyze_company(data, cutoff_date):
    roe_points = None
    margin_points = None
    consistency_points = None
    ratio_points = None
    fcf_points = None
    revenue_growth_points = None
    earnings_growth_points = None

    roe = None
    ratio = None

    income_records = data["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]
    eligible_income = filter_dates(income_records, cutoff_date)
    annual_records = get_annual_records(eligible_income) #get the annual records from the data
    unique_periods = get_unique_periods(annual_records) #get the unique periods from the annual records
    
    sorted_periods = sorted(unique_periods)
    latest_five = sorted_periods[-5:] #get the last five periods

    #ANNUALIZED EARNINGS GROWTH
    first_income = unique_periods[latest_five[0]]["val"]
    last_income = unique_periods[latest_five[-1]]["val"]
    growth = CAGR(first_income, last_income, len(latest_five) - 1) #calculate the CAGR using the first and last income and the number of intervals

    if growth is None:
        print("Annualized earnings growth: unavailable")
    else:
        earnings_growth_points = score_growth(growth)
    
    #ANNUALIZED_REVENUE_GROWTH
    unique_revenue = get_revenue_periods(data, cutoff_date)

    for period in latest_five:
        if period in unique_revenue:
            record = unique_revenue[period]
        else:
            print("Missing revenue for:", period)
    
    first_revenue = unique_revenue[latest_five[0]]["val"]
    last_revenue = unique_revenue[latest_five[-1]]["val"]
    revenue_growth = CAGR(first_revenue, last_revenue, len(latest_five) - 1)
    if revenue_growth is None:
        print("Annualized revenue growth: unavailable")
    else:
        revenue_growth_points = score_growth(revenue_growth)

    #NET PROFIT MARGIN
    latest_period = latest_five[-1]
    income = unique_periods[latest_period]["val"]
    revenue = unique_revenue[latest_period]["val"]
    margin = net_profit_margin(income, revenue)
    if margin is None:
        print("Net profit margin: unavailable")
    else:
        margin_points = score_net_margin(margin)
    
    #NET PROFIT MARGIN CONSISTENCY
    margins = []
    for period in latest_five:
        income = unique_periods[period]["val"]
        revenue = unique_revenue[period]["val"]
        margin = net_profit_margin(income, revenue)
        margins.append(margin)
        if margin is None:
            print(f"{period[1]}, Margin unavailable")
    
    consistency = calculate_std_dev(margins)
    if consistency is None:
        print("Margin consistency: unavailable")
    else:
        consistency_points = score_margin_consistency(consistency)

    # ASSET LIABILITY RATIO
    asset_records = data["facts"]["us-gaap"]["Assets"]["units"]["USD"]


    eligible_assets = filter_dates(asset_records, cutoff_date)
    eligible_equity = get_equity_records(data, cutoff_date)
    latest_end = latest_five[-1][1]

    latest_asset_record = get_balance_on_date(eligible_assets, latest_end)
    latest_equity_record = get_balance_on_date(eligible_equity, latest_end)

    latest_liability_record = None

    # Use reported liabilities if available
    if "Liabilities" in data["facts"]["us-gaap"]:
        liability_records = data["facts"]["us-gaap"]["Liabilities"]["units"]["USD"]
        eligible_liabilities = filter_dates(liability_records, cutoff_date)
        latest_liability_record = get_balance_on_date(eligible_liabilities,latest_end)
    if latest_asset_record is None:
        print("Assets unavailable")
    else:
        assets = latest_asset_record["val"]
        if latest_liability_record is not None:
            liabilities = latest_liability_record["val"]
        elif latest_equity_record is not None:
            liabilities = assets - latest_equity_record["val"]
        else:
            liabilities = None
        if liabilities is None:
            print("Liabilities unavailable")
        else:
            ratio = liability_to_asset_ratio(assets,liabilities)
            if ratio is None:
                print("Liability to asset ratio: unavailable")
            else:
                ratio_points = score_liabilities_to_assets(ratio)
    
    #RETURN ON EQUITY (ROE)
    openingDATE = latest_five[-2][1]  # second last's record's end date
    closingDATE = latest_five[-1][1]  # last period's end date

    eligible_equity = get_equity_records(data, cutoff_date)
    openingEQ = get_balance_on_date(eligible_equity, openingDATE)
    closingEQ = get_balance_on_date(eligible_equity, closingDATE)

    if openingEQ is None or closingEQ is None:
        print("Equity unavailable")
    else:
        latest_income = unique_periods[latest_five[-1]]['val']
        roe = return_on_equity(latest_income, openingEQ["val"], closingEQ["val"])
        if roe is None:
            print("Return on equity: unavailable")
        else:
            roe_points = score_ROE(roe)


    #Free Cash Flow
    unique_operating_cash = get_operating_cash_periods(data, cutoff_date)
    unique_capex = get_capex_periods(data, cutoff_date)

    #calculate free cash flow
    positive_fcf_years = 0
    available_fcf_years = 0

    #NEW CODE TO SOLVE THE NVIDIA EDGE CASE
    #TODO: investigate historical NVIDIA CAPEX tags for backtesting
    for period in latest_five:
        end_date = period[1]
        operating_record = None
        capex_record = None

        for cash_period, record in unique_operating_cash.items():
            if cash_period[1] == end_date:
                operating_record = record
                break
        for capex_period, record in unique_capex.items():
            if capex_period[1] == end_date:
                capex_record = record
                break
        if operating_record is None or capex_record is None: # DEBUG CASH FLOW ERROR
            print(end_date, "Missing cash-flow data")
            if operating_record is None:
                print("  -> Missing operating cash flow")
            if capex_record is None:
                print("  -> Missing CAPEX")
        else:
            operating_cash = operating_record["val"]
            capex = capex_record["val"]
            fcf = free_cash_flow(operating_cash, capex)
            available_fcf_years += 1
            if fcf > 0:
                positive_fcf_years += 1
    #ends here
    fcf_points = score_positive_fcf(positive_fcf_years, available_fcf_years)
    if fcf_points is None:
        print("Free-cash-flow indicator unavailable: need 5 complete years")


    
    scores = {
        "Return on equity": roe_points,
        "Net profit margin": margin_points,
        "Margin consistency": consistency_points,
        "Liabilities to assets": ratio_points,
        "Positive free cash flow": fcf_points,
        "Revenue growth": revenue_growth_points,
        "Earnings growth": earnings_growth_points
    }
    for name, points in scores.items():
        print(name, ":", points)
    
    total_score = None
    if None in scores.values():
        print("Total score unavailable, one or more indicators are missing")
    else:
        total_score = sum(scores.values())
        print("Total score:", total_score, "/ 100")
    
    indicators = {
        "Return on equity": roe,
        "Net profit margin": net_profit_margin(unique_periods[latest_five[-1]]["val"], unique_revenue[latest_five[-1]]["val"]),
        "Margin consistency": consistency,
        "Liabilities to assets": ratio,
        "Positive free cash flow": (positive_fcf_years if available_fcf_years == 5 else None),
        "Revenue growth": revenue_growth,
        "Earnings growth": growth,
    }

    return {
        "company": data["entityName"],
        "cik": data["cik"],
        "cutoff_date": cutoff_date,
        "indicators": indicators,
        "scores": scores,
        "total_score": total_score,
    }