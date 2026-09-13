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
        "Microsoft": 789019,
        "Alphabet": 1652044,
        "Meta": 1326801,
        "Mastercard": 1141391,
        "Lam Research": 707549,
        "Arista Networks": 1596532,
        "Intuitive Surgical": 1035267,
        "Adobe": 796343,
        "KLA": 319201,
        "Amphenol": 820313,
        "NVIDIA": 1045810,
        "Applied Materials": 6951,
        "Newmont": 1164727,
        "Howmet Aerospace": 4281,
        "Eaton": 1551182,
        "Vertex Pharmaceuticals": 875320,
        "Parker-Hannifin": 76334,
        "Netflix": 1065280,
        "Coca-Cola": 21344,
        "Thermo Fisher Scientific": 97745,
        "Micron": 723125,
        "ServiceNow": 1373715,
        "Accenture": 1467373,
        "Amazon": 1018724,
        "Salesforce": 1108524,
        "Fortinet": 1262039,
        "Costco": 909832,
        "Cisco": 858877,
        "Merck": 310158,
        "Disney": 1744489,
        "Vertiv": 1674101,
        "Apple": 320193,
        "Analog Devices": 6281,
        "IBM": 51143,
        "Amgen": 318154,
        "Walmart": 104169,
        "Johnson & Johnson": 200406,
        "Procter & Gamble": 80424,
        "Gilead Sciences": 882095,
        "General Dynamics": 40533,
        "Oracle": 1341439,
        "AMD": 2488,
        "RTX": 101829,
        "Union Pacific": 100885,
        "Texas Instruments": 97476,
        "T-Mobile": 1283699,
        "Deere": 315189,
        "AT&T": 732717,
        "PepsiCo": 77476,
        "Abbott": 1800,
        "Tesla": 1318605,
        "Chevron": 93410,
        "Caterpillar": 18230,
        "Home Depot": 354950,
        "Lockheed Martin": 936468,
        "Marathon Petroleum": 1510295,
        "Danaher": 313616,
        "Bristol Myers Squibb": 14272,
        "CVS Health": 64803,
        "Ford": 37996,
        "Pfizer": 78003,

        "Intuit": 896878,
        "Garmin": 1121788,
        "HEICO": 46619,
        "Fastenal": 815556,
        "Cintas": 723254,
        "Monolithic Power Systems": 1280452,
        "IDEXX Laboratories": 874716,
        "Republic Services": 1060391,
        "Comfort Systems USA": 1035983,
        "Chipotle": 1058090,
        "Motorola Solutions": 68505,
        "Autodesk": 769397,
        "Paychex": 723531,
        "Wabtec": 943452,
        "Ecolab": 31462,
        "Agilent Technologies": 1090872,
        "Comcast": 1166691,
        "Waste Management": 823768,
        "W.W. Grainger": 277135,
        "Devon Energy": 1090012,
        "ONEOK": 1039684,
        "Johnson Controls": 833444,
        "Waste Connections": 1318220,
        "Teradyne": 97210,
        "PayPal": 1633917,
        "Sherwin-Williams": 89800,
        "Williams Companies": 107263,
        "Synopsys": 883241,
        "SLB": 87347,
        "Ross Stores": 745732,
        "Delta Air Lines": 27904,
        "Rockwell Automation": 1024478,
        "Moody's": 1059556,
        "Edwards Lifesciences": 1099800,
        "Colgate-Palmolive": 21665,
        "Kinder Morgan": 1506307,
        "Targa Resources": 1389170,
        "Regeneron": 872589,
        "Cencora": 1140859,
        "Sysco": 96021,
    }

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