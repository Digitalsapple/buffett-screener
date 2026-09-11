import os
import requests
from datetime import date
from metrics import CAGR, net_profit_margin, calculate_std_dev, liability_to_asset_ratio, return_on_equity, free_cash_flow
from financials import get_annual_records, get_unique_periods, get_balance_on_date
from scoring import score_ROE, score_net_margin, score_margin_consistency, score_liabilities_to_assets, score_positive_fcf, score_growth

def get_data(cik):
    contact = os.environ.get("EMAIL_CONTACT") #contact info is read from the environment variable EMAIL_CONTACT and stored in var "contact"
    if not contact:
        raise ValueError("Please enter your real email into EMAIL_CONTACT.") #prompt user to enter email if "contact" does not exist
    
    true_cik = str(cik).zfill(10) #convert number to a text and then add leading zeros
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{true_cik}.json" #create the url
    response = requests.get(url, headers={"User-Agent": "buffett-screener " + contact}, timeout=30) #send a GET request to the url with the contact info in the header
    response.raise_for_status() #checks for errors, and if there are, it stops the function
    return response.json() #return the response in JSON format

if __name__ == "__main__": #this is the main function that runs when code is executed 
    data = get_data(320193)

    annual_records = get_annual_records(data["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]) #get the annual records from the data
    unique_periods = get_unique_periods(annual_records) #get the unique periods from the annual records
    
    sorted_periods = sorted(unique_periods)
    latest_five = sorted_periods[-5:] #get the last five periods

    for period in latest_five:
        record = unique_periods[period]
        print(record["start"], record["end"], f"${record['val']:,}") #print the net income for the last five periods

    #ANNUALIZED EARNINGS GROWTH
    first_income = unique_periods[latest_five[0]]["val"]
    last_income = unique_periods[latest_five[-1]]["val"]
    growth = CAGR(first_income, last_income, len(latest_five) - 1) #calculate the CAGR using the first and last income and the number of intervals

    if growth is None:
        print("Annualized earnings growth: unavailable")
    else:
        print(f"Annualized earnings growth: {growth:.2%}")
        earnings_growth_points = score_growth(growth)
        print("Earnings growth points:", earnings_growth_points, "/ 10")
    
    #ANNUALIZED_REVENUE_GROWTH
    revenue_records = data["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
    annual_revenue = get_annual_records(revenue_records)
    unique_revenue = get_unique_periods(annual_revenue)
    print("Unique annual revenue periods:", len(unique_revenue))

    for period in latest_five:
        if period in unique_revenue:
            record = unique_revenue[period]
            print(record["start"], record["end"], f"${record["val"]:,}")
        else:
            print("Missing revenue for:", period)
    
    first_revenue = unique_revenue[latest_five[0]]["val"]
    last_revenue = unique_revenue[latest_five[-1]]["val"]
    revenue_growth = CAGR(first_revenue, last_revenue, len(latest_five) - 1)
    if revenue_growth is None:
        print("Annualized revenue growth: unavailable")
    else:
        print(f"Annualized revenue growth: {revenue_growth:.2%}")
        revenue_growth_points = score_growth(revenue_growth)
        print("Revenue growth points:", revenue_growth_points, "/ 10")

    #NET PROFIT MARGIN
    latest_period = latest_five[-1]
    income = unique_periods[latest_period]["val"]
    revenue = unique_revenue[latest_period]["val"]
    margin = net_profit_margin(income, revenue)
    if margin is None:
        print("Net profit margin: unavailable")
    else:
        print(f"Net profit margin: {margin:.2%}")
        margin_points = score_net_margin(margin)
        print(f"Net margin points: {margin_points} / 15")
    
    #NET PROFIT MARGIN CONSISTENCY
    margins = []
    for period in latest_five:
        income = unique_periods[period]["val"]
        revenue = unique_revenue[period]["val"]
        margin = net_profit_margin(income, revenue)
        margins.append(margin)
        if margin is None:
            print(f"{period[1]}, Margin unavailable")
        else:
            print(f"{period[1]} Margin: {margin:.2%}")
    
    consistency = calculate_std_dev(margins)
    if consistency is None:
        print("Margin consistency: unavailable")
    else:
        print(f"Margin consistency (std dev): {consistency * 100:.2f} percentage points")
        consistency_points = score_margin_consistency(consistency)
        print("Margin consistency points:", consistency_points, "/ 10")

    # ASSET LIABILITY RATIO
    asset_records = data["facts"]["us-gaap"]["Assets"]["units"]["USD"]
    liability_records = data["facts"]["us-gaap"]["Liabilities"]["units"]["USD"]
    latest_end = latest_five[-1][1] #[-1] takes the latest (start, end) tuple, and then [1] takes the end date from the tuple
    
    latest_asset_record = get_balance_on_date(asset_records, latest_end)
    latest_liability_record = get_balance_on_date(liability_records, latest_end)
    if latest_asset_record is None or latest_liability_record is None:
        print("Latest asset or liability record unavailable")
    else:
        print("Balance date:", latest_end)
        print(f"Assets: ${latest_asset_record['val']:,}")
        print(f"Liabilities: ${latest_liability_record['val']:,}")

        ratio = liability_to_asset_ratio(latest_asset_record["val"], latest_liability_record["val"])
        if ratio is None:
            print("Liability to asset ratio: unavailable")
        else:
            print(f"Liability to asset ratio: {ratio:.2%}")
            ratio_points = score_liabilities_to_assets(ratio)
            print("Liabilities to assets points:", ratio_points, "/ 15")
    
    #RETURN ON EQUITY (ROE)
    equity_records = data["facts"]["us-gaap"]["StockholdersEquity"]["units"]["USD"]
    print(equity_records[-1])
    openingDATE = latest_five[-2][1]  # second last's record's end date
    closingDATE = latest_five[-1][1]  # last period's end date

    openingEQ = get_balance_on_date(equity_records, openingDATE)
    closingEQ = get_balance_on_date(equity_records, closingDATE)

    if openingEQ is None or closingEQ is None:
        print("Equity unavailable")
    else:
        print(f"Opening Equity: {openingDATE} ${openingEQ['val']:,}")
        print(f"Closing Equity: {closingDATE} ${closingEQ['val']:,}")
        latest_income = unique_periods[latest_five[-1]]['val']
        roe = return_on_equity(latest_income, openingEQ["val"], closingEQ["val"])
        if roe is None:
            print("Return on equity: unavailable")
        else:
            print(f"Return on equity: {roe:.2%}")
            roe_points = score_ROE(roe)
            print("ROE points:", roe_points, "/ 20")


    #Free Cash Flow
    operating_cash_records = data["facts"]["us-gaap"]["NetCashProvidedByUsedInOperatingActivities"]["units"]["USD"]
    capital_expenditure_records = data["facts"]["us-gaap"]["PaymentsToAcquirePropertyPlantAndEquipment"]["units"]["USD"]
    unique_operating_cash = get_unique_periods(get_annual_records(operating_cash_records))
    unique_capex = get_unique_periods(get_annual_records(capital_expenditure_records))

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
            print(period[1], f"Free cash flow: ${fcf:,}")
    fcf_points = score_positive_fcf(positive_fcf_years, available_fcf_years)
    if fcf_points is None:
        print("Free-cash-flow indicator unavailable: need 5 complete years")
    else:
        print("Years with positive free cash flow:", positive_fcf_years, "/ 5")
        print("Free cash flow points:", fcf_points, "/ 20")