def CAGR(first, last, intervals):
    if first <= 0 or last <= 0:
        return None
    return (last / first) ** (1 / intervals) - 1

def net_profit_margin(net_income, revenue):
    if revenue <= 0:
        return None
    return net_income / revenue