from datetime import date

def get_annual_records(records):
    from datetime import date

    annual_records = []
    for record in records:
        if "start" not in record or "end" not in record:
            continue
        start_date = date.fromisoformat(record["start"])
        end_date = date.fromisoformat(record["end"])
        duration = (end_date - start_date).days
        if (
            record.get("form") in ["10-K", "10-K/A"]
            and record.get("fp") == "FY"
            and 300 <= duration <= 380
        ):
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


#DEBUGGING AND TESTING
def get_revenue_periods(data, cutoff_date):
    revenue_tags = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"]
    combined_revenue = {}
    for tag in revenue_tags:
        if tag not in data["facts"]["us-gaap"]:
            continue
        records = data["facts"]["us-gaap"][tag]["units"].get("USD", [])
        eligible_records = filter_dates(records, cutoff_date)
        annual_records = get_annual_records(eligible_records)
        unique_periods = get_unique_periods(annual_records)
        combined_revenue.update(unique_periods)
    return combined_revenue

def get_capex_periods(data, cutoff_date):
    capex_tags = [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets"
    ]

    combined_capex = {}

    for tag in capex_tags:
        if tag not in data["facts"]["us-gaap"]:
            continue

        records = data["facts"]["us-gaap"][tag]["units"].get("USD", [])

        eligible_records = filter_dates(records, cutoff_date)
        annual_records = get_annual_records(eligible_records)
        unique_periods = get_unique_periods(annual_records)

        for period, record in unique_periods.items():
            if period not in combined_capex:
                combined_capex[period] = record

    return combined_capex

def get_operating_cash_periods(data, cutoff_date):
    operating_cash_tags = ["NetCashProvidedByUsedInOperatingActivities","NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"]
    combined_cash = {}

    for tag in operating_cash_tags:
        if tag not in data["facts"]["us-gaap"]:
            continue
        records = data["facts"]["us-gaap"][tag]["units"].get("USD", [])
        eligible_records = filter_dates(records, cutoff_date)
        annual_records = get_annual_records(eligible_records)
        unique_periods = get_unique_periods(annual_records)
        for period, record in unique_periods.items():
            # IF SAME PERIOD, THEN TAKE THE PRIMARY TAG
            if period not in combined_cash:
                combined_cash[period] = record
    return combined_cash

def get_equity_records(data, cutoff_date):
    facts = data["facts"]["us-gaap"]
    # WHAT IS IDEAL: equity attributable to the company's stockholders
    if "StockholdersEquity" in facts:
        records = facts["StockholdersEquity"]["units"].get("USD", [])
        return filter_dates(records, cutoff_date)

    # If that doesn't work, this is the fallback: total equity includes noncontrolling interest
    total_tag = "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
    if total_tag not in facts:
        return []
    total_records = filter_dates(facts[total_tag]["units"].get("USD", []),cutoff_date)
    # If minority interest exists, subtract it
    if "MinorityInterest" not in facts:
        return []
    minority_records = filter_dates(facts["MinorityInterest"]["units"].get("USD", []),cutoff_date)
    derived_equity = []
    for total_record in total_records:
        end_date = total_record["end"]
        minority_record = get_balance_on_date(minority_records,end_date)
        if minority_record is not None:
            new_record = total_record.copy()
            new_record["val"] = (total_record["val"]- minority_record["val"])
            derived_equity.append(new_record)
    return derived_equity