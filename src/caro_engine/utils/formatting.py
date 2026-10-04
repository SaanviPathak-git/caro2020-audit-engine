"""
Formatting utilities for Indian currency, numbers, and audit presentation.
"""

def format_inr(value: float, decimals: int = 2) -> str:
    """
    Format a number in Indian numbering system: e.g. 12,34,567.89
    """
    if value is None:
        return "₹0.00"
    
    is_neg = value < 0
    val_abs = abs(value)
    
    formatted_float = f"{val_abs:.{decimals}f}"
    parts = formatted_float.split(".")
    integer_part = parts[0]
    decimal_part = f".{parts[1]}" if len(parts) > 1 else ""
    
    if len(integer_part) <= 3:
        res = integer_part
    else:
        last3 = integer_part[-3:]
        rest = integer_part[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        res = ",".join(groups) + "," + last3
        
    return f"{'-' if is_neg else ''}₹{res}{decimal_part}"

def format_crores(value: float, decimals: int = 2) -> str:
    """Format value in INR Crores"""
    return f"{format_inr(value, decimals)} Cr"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format float as percentage"""
    if value is None:
        return "0.00%"
    return f"{value:.{decimals}f}%"
