import enum


class PaymentMethod(str, enum.Enum):
    """Allowed ways an expense can be paid."""

    cash = "cash"
    card = "card"
    upi = "upi"
    bank_transfer = "bank_transfer"


class Month(str, enum.Enum):
    """The 12 months of the year, used by budgets (no year: a budget repeats every year)."""

    january = "january"
    february = "february"
    march = "march"
    april = "april"
    may = "may"
    june = "june"
    july = "july"
    august = "august"
    september = "september"
    october = "october"
    november = "november"
    december = "december"
