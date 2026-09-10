from datetime import date

def get_annual_records(records):
    annual_records = []

    for record in records:
        start = date.fromisoformat(record["start"])
        end = date.fromisoformat(record["end"])
        duration = (end - start).days
        if 330 <= duration <= 380:
            annual_records.append(record)
    
    return annual_records

def get_unique_periods(records):
    unique_periods = {} #dictionary

    for record in records:
        period = (record["start"], record["end"]) #tuple of start and end dates
        if period not in unique_periods:
            unique_periods[period] = record #add new key and value
        elif record["filed"] > unique_periods[period]["filed"]: #if it IS already in the dictionary
            unique_periods[period] = record #update the value if the filed date is more recent
    return unique_periods