"""Explicit product exclusions for the seven-day leader research universe."""
EXCLUDED_WEAPONS = frozenset({'Nova','XM1014','MAG-7','Sawed-Off','Negev','M249','R8 Revolver'})


def allowed_products(names):
    # Match weapon prefix, not skin/agent names containing the same word.
    prefix = names.astype(str).str.split(' | ', n=1, regex=False).str[0]
    prefix = prefix.str.replace(r'^(?:StatTrak™ |Souvenir )', '', regex=True)
    return ~prefix.isin(EXCLUDED_WEAPONS)
