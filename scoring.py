def score_ROE(roe):
    if roe is None:
        return 0
    elif roe >= 0.15:
        return 20
    elif roe >= 0.10:
        return 10
    else:
        return 0

def score_net_margin(margin):
    if margin is None:
        return None
    elif margin >= 0.15:
        return 15
    elif margin >= 0.10:
        return 8
    else:
        return 0

def score_margin_consistency(consistency):
    if consistency is None:
        return None
    elif consistency <= 0.03:
        return 10
    elif consistency <= 0.06:
        return 5
    else:
        return 0

def score_liabilities_to_assets(ratio):
    if ratio is None:
        return None
    elif ratio <= 0.50:
        return 15
    elif ratio <= 0.70:
        return 8
    else:
        return 0

def score_positive_fcf(positive_years, available_years):
    if available_years != 5:
        return None
    return positive_years * 4

def score_growth(growth):
    if growth is None:
        return None
    elif growth >= 0.08:
        return 10
    elif growth >= 0.03:
        return 5
    else:
        return 0