import re
import decimal

def hashtag_to_badge(value):
    hashtags = re.findall(r'#\w+', value)
    for tag in hashtags:
        clean_tag = re.search(r'#(\w+)', tag).group(1)  # Extract the word after the '#' symbol
        value = value.replace(tag, f'<a href="?tag={clean_tag}" class="badge badge-hashtag">{clean_tag}</a>')
    return value




def extract_fiat_value(s):
    currencies = ['USD', 'EUR', 'GBP', 'CAD', 'CHF', 'AUD', 'JPY']
    
    # CHF XXX
    pattern = r"({})\s?(\d+(?:\.\d+)?)"
    for currency in currencies:
        match = re.search(pattern.format(currency), s)
        if match:
            print(f"Currency: {match.group(1)}, Value: {match.group(2)}")
            return (decimal.Decimal(match.group(2)), match.group(1))

    # XXX CHF
    pattern = r"(\d+(?:\.\d+)?)\s?({})"

    for currency in currencies:
        match = re.search(pattern.format(currency), s)
        if match:
            value = decimal.Decimal(match.group(1))
            currency_symbol = currency
            # Find the currency symbol position in the string
            symbol_start = match.start(2)
            symbol_end = match.end(2)
            if symbol_start > 0:
                currency_symbol = s[symbol_start:symbol_end]
            print(f"Currency: {currency_symbol}, Value: {value}")
            return (value, currency_symbol)

    return (decimal.Decimal(-1), "")
