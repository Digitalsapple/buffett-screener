from sec_client import get_data
from screener import analyze_company
from companies import companies, tickers

def rank_companies(companies, cutoff_date):
    results = []
    failed = []

    for name, cik in companies.items():
        try:
            data = get_data(cik)
            result = analyze_company(data,cutoff_date)
            if result["total_score"] is not None:
                result["name"] = name
                results.append(result)
            else:
                failed.append({"company": name,"reason": "Incomplete indicators"})
        except Exception as error:
            failed.append({"company": name,"reason": str(error)})
    results.sort(key=lambda company: (-company["total_score"],company["company"])) #tie-breaking debug added)
    return results, failed

def get_top_tickers(cutoff_date, top_n=10):
    results, failed = rank_companies(companies,cutoff_date)
    top_companies = results[:top_n]
    top_tickers = []
    for company in top_companies:
        name = company["name"]
        ticker = tickers[name]
        top_tickers.append(ticker)
    return top_tickers, top_companies, failed