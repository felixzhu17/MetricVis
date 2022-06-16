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


def ifnone(a, b):
    "`b` if `a` is None else `a`"
    return b if a is None else a


def get_month_before(row, df, col):
    try:
        return df.query(f"""month == {row['month']} and year == {row['year'] - 1}""")[
            col
        ].item()
    except ValueError as e:
        raise ValueError(
            f"Monthly data not available for {row['month']: .0f}-{row['year'] - 1: .0f}"
        )


def get_week_before(row, df, col):
    try:
        return df.query(f"""week == {row['week']} and year == {row['year'] - 1}""")[
            col
        ].item()
    except ValueError as e:
        raise ValueError(
            f"Weekly data not available for {row['week']: .0f}-{row['year'] - 1: .0f}"
        )
