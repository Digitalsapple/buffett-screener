import os
import requests

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
    print("Company:", data["entityName"]) #retrive the company name from the JSON response and print it
    print(data.keys()) #print the keys of the JSON response
    print(data["facts"].keys()) #look into the FACTS key
    financials = data["facts"]["us-gaap"] #look into the US-GAAP key
    print(list(financials.keys())[:10]) #print the first 10 keys of the US-GAAP key

    net_income = financials["NetIncomeLoss"] #look into the NetIncomeLoss key
    print(net_income.keys()) #print the keys of the NetIncomeLoss key

    net_income_values = net_income["units"]["USD"] #look into the USD key
    print(net_income_values[0])

    first_record = net_income_values[0] #store the first record of the USD key in a variable
    print(f"Net Income: ${first_record['val']:,}")