import pandas as pd
import numpy as np

def process_portfolio_data(df):
    """
    Process portfolio data from the uploaded Excel file.
    
    Args:
        df (pd.DataFrame): The dataframe containing portfolio data
        
    Returns:
        dict: Dictionary containing processed portfolio metrics
    """
    # Normalize column names for processing
    df_processed = df.copy()
    
    # Map standard column names
    column_mapping = {
        'Controvalore': 'value',
        'Rendimento': 'return_value',
        'Rendimento %': 'return_percentage',
        'Nome': 'name',
        'Categoria': 'category',
        'TER': 'ter',
        'Allocazione': 'allocation'
    }
    
    # Rename columns if they exist
    for old_col, new_col in column_mapping.items():
        if old_col in df_processed.columns:
            df_processed[new_col] = df_processed[old_col]
    
    # Calculate total portfolio value
    if 'value' in df_processed.columns:
        total_value = df_processed['value'].sum()
    elif 'Controvalore' in df_processed.columns:
        total_value = df_processed['Controvalore'].sum()
    else:
        total_value = 0
    
    # Calculate total return value
    if 'return_value' in df_processed.columns:
        total_return_value = df_processed['return_value'].sum()
    elif 'Rendimento' in df_processed.columns:
        total_return_value = df_processed['Rendimento'].sum()
    else:
        total_return_value = 0
    
    # Calculate total return percentage
    if total_value > 0:
        total_return_percentage = (total_return_value / (total_value - total_return_value)) * 100
    else:
        total_return_percentage = 0
    
    # Categorize by asset class if not already present
    if 'asset_class' not in df_processed.columns:
        df_processed['asset_class'] = categorize_by_asset_class(df_processed)
    
    return {
        'data': df_processed,
        'total_value': total_value,
        'total_return_value': total_return_value,
        'total_return_percentage': total_return_percentage
    }

def categorize_by_asset_class(df):
    """
    Categorize holdings into major asset classes based on category.
    
    Args:
        df (pd.DataFrame): The dataframe containing portfolio data
        
    Returns:
        pd.Series: Series with asset class for each holding
    """
    # Extract category column
    if 'category' in df.columns:
        category_col = 'category'
    elif 'Categoria' in df.columns:
        category_col = 'Categoria'
    else:
        # If no category column exists, return 'Unknown'
        return pd.Series(['Unknown'] * len(df))
    
    # Function to map categories to asset classes
    def map_category_to_asset_class(category):
        category = str(category).lower()
        
        if any(term in category for term in ['azioni', 'azion', 'stock', 'equity', 'share']):
            return 'Stocks'
        elif any(term in category for term in ['obblig', 'bond', 'fixed income', 'treasury']):
            return 'Bonds'
        elif any(term in category for term in ['monetario', 'money market', 'liquidity', 'cash']):
            return 'Money Market'
        elif any(term in category for term in ['commodit', 'materie prime', 'gold', 'silver', 'oil']):
            return 'Commodities'
        elif any(term in category for term in ['immobil', 'real estate', 'reit']):
            return 'Real Estate'
        elif any(term in category for term in ['alternativ', 'hedge', 'private equity']):
            return 'Alternatives'
        else:
            return 'Other'
    
    return df[category_col].apply(map_category_to_asset_class)

def calculate_asset_allocation(df):
    """
    Calculate the asset allocation percentages by asset class.
    
    Args:
        df (pd.DataFrame): The dataframe containing portfolio data
        
    Returns:
        pd.DataFrame: Dataframe with asset class allocations
    """
    # Process the data
    processed_data = process_portfolio_data(df)
    df_processed = processed_data['data']
    
    # Use the value column to calculate allocation
    if 'value' in df_processed.columns:
        value_col = 'value'
    elif 'Controvalore' in df_processed.columns:
        value_col = 'Controvalore'
    else:
        # If no value column exists, we can't calculate allocation
        return pd.DataFrame({
            'asset_class': ['No Data'],
            'allocation': [100]
        })
    
    # Determine asset class column
    if 'asset_class' in df_processed.columns:
        asset_class_col = 'asset_class'
    else:
        # Create asset class from category
        df_processed['asset_class'] = categorize_by_asset_class(df_processed)
        asset_class_col = 'asset_class'
    
    # Calculate allocation by asset class
    asset_allocation = df_processed.groupby(asset_class_col)[value_col].sum().reset_index()
    asset_allocation.columns = ['asset_class', 'value']
    asset_allocation['allocation'] = asset_allocation['value'] / asset_allocation['value'].sum() * 100
    
    # Make sure all major asset classes are represented (even with 0%)
    major_asset_classes = ['Stocks', 'Bonds', 'Money Market', 'Commodities', 'Cash']
    
    existing_classes = asset_allocation['asset_class'].tolist()
    for asset_class in major_asset_classes:
        if asset_class not in existing_classes:
            asset_allocation = pd.concat([
                asset_allocation,
                pd.DataFrame({'asset_class': [asset_class], 'value': [0], 'allocation': [0]})
            ], ignore_index=True)
    
    # Sort by allocation (descending)
    asset_allocation = asset_allocation.sort_values('allocation', ascending=False)
    
    return asset_allocation
