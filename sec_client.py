import os
import requests
from datetime import date
from companies import companies

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

    cutoff_date = "2026-09-10"

    results = []
    failed = []

    for name, cik in companies.items():
        print("\nAnalyzing", name)

        try:
            data = get_data(cik)
            result = analyze_company(data, cutoff_date)

            if result["total_score"] is not None:
                results.append(result)
            else:
                failed.append({
                    "company": name,
                    "reason": "Incomplete financial indicators"
                })

        except Exception as error:
            failed.append({
                "company": name,
                "reason": str(error)
            })

            print(name, "FAILED:", error)
    
    results.sort(
        key=lambda company: company["total_score"],
        reverse=True
    )

    print("\nFINAL RANKING")

    for rank, company in enumerate(results, start=1):
        print(
            rank,
            company["company"],
            company["total_score"],
            "/ 100"
        )
    
    print("\nSUMMARY")
    print("Companies attempted:", len(companies))
    print("Successfully scored:", len(results))
    print("Failed/skipped:", len(failed))

    print("\nFAILED COMPANIES")

    for company in failed:
        print(
            company["company"],
            "-",
            company["reason"]
        )