from statistics import pstdev

def CAGR(first, last, intervals):
    if first <= 0 or last <= 0:
        return None
    return (last / first) ** (1 / intervals) - 1

def net_profit_margin(net_income, revenue):
    if revenue <= 0:
        return None
    return net_income / revenue

def calculate_std_dev(margins):
    if len(margins) != 5 or None in margins:
        return None
    return pstdev(margins)

def liability_to_asset_ratio(assets, liabilities):
    if assets <= 0:
        return None
    return liabilities / assets