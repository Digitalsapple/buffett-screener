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

    data = get_data(320193)
    result = analyze_company(data, "2026-09-10")

    print("Returned company:", result["company"])
    print("Returned total:", result["total_score"])
    print(result["indicators"])