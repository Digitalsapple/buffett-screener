import os
import requests
from datetime import date
from metrics import CAGR

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
    first_val = data["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"][0]["val"] #store the value of the first record in a variable
    print(f"Net Income: ${first_val:,}")

    annual_records = []

    for record in data["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]: #loop through records in USD and print the value of each record
        start = date.fromisoformat(record["start"]) #convert the start date from string to date format
        end = date.fromisoformat(record["end"])
        duration = (end - start).days
        if 330 <= duration <= 380:
            annual_records.append(record)

    unique_periods = {} #dictionary

    for record in annual_records:
        period = (record["start"], record["end"]) #tuple of start and end dates
        if period not in unique_periods:
            unique_periods[period] = record #add new key and value
        elif record["filed"] > unique_periods[period]["filed"]: #if it IS already in the dictionary
            unique_periods[period] = record #update the value if the filed date is more recent
    
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