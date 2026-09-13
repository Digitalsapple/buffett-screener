from metrics import CAGR, net_profit_margin, calculate_std_dev, liability_to_asset_ratio, return_on_equity, free_cash_flow
from financials import get_annual_records, get_unique_periods, get_balance_on_date, filter_dates
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
    revenue_records = data["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
    eligible_revenue = filter_dates(revenue_records, cutoff_date)
    annual_revenue = get_annual_records(eligible_revenue)
    unique_revenue = get_unique_periods(annual_revenue)

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
    liability_records = data["facts"]["us-gaap"]["Liabilities"]["units"]["USD"]
    latest_end = latest_five[-1][1] #[-1] takes the latest (start, end) tuple, and then [1] takes the end date from the tuple
    
    eligible_assets = filter_dates(asset_records, cutoff_date)
    eligible_liabilities = filter_dates(liability_records, cutoff_date)
    latest_asset_record = get_balance_on_date(eligible_assets, latest_end)
    latest_liability_record = get_balance_on_date(eligible_liabilities, latest_end)

    if latest_asset_record is None or latest_liability_record is None:
        print("Latest asset or liability record unavailable")
    else:
        ratio = liability_to_asset_ratio(latest_asset_record["val"], latest_liability_record["val"])
        if ratio is None:
            print("Liability to asset ratio: unavailable")
        else:
            ratio_points = score_liabilities_to_assets(ratio)
    
    #RETURN ON EQUITY (ROE)
    equity_records = data["facts"]["us-gaap"]["StockholdersEquity"]["units"]["USD"]
    openingDATE = latest_five[-2][1]  # second last's record's end date
    closingDATE = latest_five[-1][1]  # last period's end date

    eligible_equity = filter_dates(equity_records, cutoff_date)
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
    operating_cash_records = data["facts"]["us-gaap"]["NetCashProvidedByUsedInOperatingActivities"]["units"]["USD"]
    capital_expenditure_records = data["facts"]["us-gaap"]["PaymentsToAcquirePropertyPlantAndEquipment"]["units"]["USD"]
    
    eligible_operating_cash = filter_dates(operating_cash_records, cutoff_date)
    eligible_capex = filter_dates(capital_expenditure_records, cutoff_date)
    unique_operating_cash = get_unique_periods(get_annual_records(eligible_operating_cash))
    unique_capex = get_unique_periods(get_annual_records(eligible_capex))

    #calculate free cash flow
    positive_fcf_years = 0
    available_fcf_years = 0

    for period in latest_five:
        if period not in unique_operating_cash or period not in unique_capex:
            print(period[1], "Missing cash-flow data")
        else:
            operating_cash = unique_operating_cash[period]["val"]
            capex = unique_capex[period]["val"]
            fcf = free_cash_flow(operating_cash, capex)
            available_fcf_years += 1
            if fcf > 0:
                positive_fcf_years += 1
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