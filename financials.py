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

def get_balance_on_date(records, target_date):
    selected = None
    for record in records:
        if record["end"] != target_date:
            continue
        if selected is None:
            selected = record
        elif record["filed"] > selected["filed"]:
            selected = record
    return selected

def filter_dates(records, cutoff_date):
    eligible_records = []
    for record in records:
        if record["filed"] < cutoff_date: #checks if the filing date is PRIOR to the cutoff date
            eligible_records.append(record) #if so, then add to eligible records list
    return eligible_records