import os
import requests
from datetime import date

def get_data(cik):
    contact = os.environ.get("EMAIL_CONTACT") #contact info is read from the environment variable EMAIL_CONTACT and stored in var "contact"
    if not contact:
        raise ValueError("Please enter your real email into EMAIL_CONTACT.") #prompt user to enter email if "contact" does not exist
    
    true_cik = str(cik).zfill(10) #convert number to a text and then add leading zeros
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{true_cik}.json" #create the url
    response = requests.get(url, headers={"User-Agent": "buffett-screener " + contact}, timeout=30) #send a GET request to the url with the contact info in the header
    response.raise_for_status() #checks for errors, and if there are, it stops the function
    return response.json() #return the response in JSON format

if __name__ == "__main__": ##this is the main function that runs when code is executed
    from screener import analyze_company

    companies = {
        "Apple": 320193,
        "Microsoft": 789019,
        "NVIDIA": 1045810,
        "AMD": 2488,
        "Amazon": 1018724,
        "Coca-Cola": 21344,
        "JPMorgan": 19617,
        "Walmart": 104169,
        "Netflix": 1065280,
        "Tesla": 1318605,
        "Ford": 37996,
        "Costco": 909832,
        "Adobe": 796343,
        "Analog Devices": 6281,
        "AT&T": 732717,
    }

    cutoff_date = "2026-09-10"
    results = []

    for name, cik in companies.items():
        print("\nAnalyzing", name)
        data = get_data(cik)
        result = analyze_company(data, cutoff_date)

        if result["total_score"] is not None:
            results.append(result)
        else:
            print(result["company"], "skipped: incomplete or unsupported financial data")

    results.sort(key=lambda company: company["total_score"], reverse=True)
    print("\nFINAL RANKING")

    for rank, company in enumerate(results, start=1):
        print(
            rank,
            company["company"],
            company["total_score"],
            "/ 100"
        )