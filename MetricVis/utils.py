
def format_absolute(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."),
        ["", "K", "M", "B", "T"][magnitude],
    )
    
def format_percentage(num):
    return "{:.1%}".format(num)

def clean_text(text):
    return text.replace("_", " ").title()

def ifnone( a, b):
    "`b` if `a` is None else `a`"
    return b if a is None else a
