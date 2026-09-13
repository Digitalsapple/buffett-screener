from sec_client import get_data
from screener import analyze_company
from companies import companies, tickers

def rank_companies(companies, cutoff_date):
    results = []
    failed = []

    for name, cik in companies.items():
        print("Analyzing:", name)
        try:
            data = get_data(cik)
            result = analyze_company(data,cutoff_date)
            if result["total_score"] is not None:
                results.append(result)
            else:
                failed.append({"company": name,"reason": "Incomplete indicators"})
        except Exception as error:
            failed.append({"company": name,"reason": str(error)})
    results.sort(key=lambda company: (-company["total_score"],company["company"]) #tie-breaking debug added
)
    return results, failed

if __name__ == "__main__":

    cutoff_dates = [
        "2022-09-10",
        "2023-09-10",
        "2024-09-10",
    ]

    for cutoff_date in cutoff_dates:
        results, failed = rank_companies(companies,cutoff_date)
        print("\n" + "=" * 50)
        print(cutoff_date, "HISTORICAL RANKING")
        print("=" * 50)
        for rank, company in enumerate(results[:10],start=1):
            print(rank,company["company"],company["total_score"],"/ 100")
        print("\nCompanies successfully scored:", len(results))
        print("Companies skipped:", len(failed))