import streamlit as st

def format_currency(value, currency="€"):
    """
    Format a number as currency.
    
    Args:
        value (float): The value to format
        currency (str, optional): Currency symbol. Defaults to "€".
        
    Returns:
        str: Formatted currency string
    """
    try:
        # Format the value with thousand separators and 2 decimal places
        if value is None:
            return f"{currency}0.00"
        
        value_float = float(value)
        
        # Format with thousand separator and 2 decimal places
        if value_float >= 0:
            return f"{currency}{value_float:,.2f}"
        else:
            # Handle negative values
            return f"-{currency}{abs(value_float):,.2f}"
    except:
        return f"{currency}0.00"

def format_percentage(value, include_sign=True):
    """
    Format a number as percentage.
    
    Args:
        value (float): The value to format
        include_sign (bool, optional): Whether to include +/- sign. Defaults to True.
        
    Returns:
        str: Formatted percentage string
    """
    try:
        value_float = float(value)
        
        # Format with 2 decimal places
        if include_sign:
            if value_float > 0:
                return f"+{value_float:.2f}%"
            elif value_float < 0:
                return f"{value_float:.2f}%"
            else:
                return f"0.00%"
        else:
            return f"{value_float:.2f}%"
    except:
        return "0.00%"

def render_performance_indicator(value):
    """
    Create a formatted string with color indicating positive/negative performance.
    
    Args:
        value (float): The performance value in percentage
        
    Returns:
        str: Formatted string with appropriate color (using Streamlit's markdown)
    """
    try:
        value_float = float(value)
        
        if value_float > 0:
            return f"+{value_float:.2f}%"  # Positivo
        elif value_float < 0:
            return f"{value_float:.2f}%"   # Negativo
        else:
            return f"0.00%"                # Neutro
    except:
        return f"N/A"
