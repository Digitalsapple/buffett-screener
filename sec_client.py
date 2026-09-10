import os
import requests
from datetime import date
from metrics import CAGR, net_profit_margin
from financials import get_annual_records, get_unique_periods

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

    first_income = unique_periods[latest_five[0]]["val"]
    last_income = unique_periods[latest_five[-1]]["val"]
    growth = CAGR(first_income, last_income, len(latest_five) - 1) #calculate the CAGR using the first and last income and the number of intervals

    if growth is None:
        print("Annualized earnings growth: unavailable")
    else:
        print(f"Annualized earnings growth: {growth:.2%}")
    
    
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

    
    latest_period = latest_five[-1]
    income = unique_periods[latest_period]["val"]
    revenue = unique_revenue[latest_period]["val"]
    margin = net_profit_margin(income, revenue)
    if margin is None:
        print("Net profit margin: unavailable")
    else:
        print(f"Net profit margin: {margin:.2%}")