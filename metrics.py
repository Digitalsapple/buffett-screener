def CAGR(first, last, intervals):
    if first <= 0 or last <= 0:
        return None
    return (last / first) ** (1 / intervals) - 1