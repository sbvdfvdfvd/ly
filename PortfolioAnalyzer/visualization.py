import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_donut_chart(asset_allocation_df):
    """
    Create a donut chart visualization for asset allocation.
    
    Args:
        asset_allocation_df (pd.DataFrame): DataFrame with asset allocation data
        
    Returns:
        plotly.graph_objects.Figure: Donut chart figure
    """
    # Color mapping for asset classes (both English and Italian)
    color_map = {
        'Stocks': '#4285F4',
        'Bonds': '#34A853',
        'Money Market': '#FBBC05',
        'Commodities': '#EA4335',
        'Real Estate': '#8F44AA',
        'Alternatives': '#0097A7',
        'Cash': '#757575',
        'Other': '#9E9E9E',
        'Azionario': '#4285F4',
        'Obbligazionario': '#34A853',
        'Mercato Monetario': '#FBBC05',
        'Materie Prime': '#EA4335',
        'Immobiliare': '#8F44AA',
        'Alternativi': '#0097A7',
        'Liquidità': '#757575',
        'Altro': '#9E9E9E'
    }
    
    # Assign colors to asset classes
    colors = [color_map.get(asset, '#9E9E9E') for asset in asset_allocation_df['asset_class']]
    
    # Create the donut chart
    fig = go.Figure(data=[go.Pie(
        labels=asset_allocation_df['asset_class'],
        values=asset_allocation_df['allocation'],
        hole=0.6,
        marker_colors=colors,
        textinfo='label+percent',
        hoverinfo='label+percent+value',
        hovertemplate='%{label}<br>Allocation: %{percent}<br>Value: %{value:.2f}%<extra></extra>'
    )])
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        annotations=[dict(
            text='Asset<br>Allocation',
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )]
    )
    
    return fig

def create_geographic_distribution_chart(df):
    """
    Create a chart showing the geographic distribution of the portfolio.
    
    Args:
        df (pd.DataFrame): The dataframe containing portfolio data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart of geographic distribution
    """
    # Check if we have geographic data
    if 'country' not in df.columns or 'country_allocation' not in df.columns:
        # Try to extract from other columns or use placeholder
        if 'Paese' in df.columns and 'Allocazione Paese' in df.columns:
            geo_data = df.groupby('Paese')['Allocazione Paese'].sum().reset_index()
            geo_data.columns = ['country', 'allocation']
        else:
            # Create a placeholder chart
            return go.Figure(
                data=[go.Bar(x=['No Data'], y=[0])],
                layout=dict(
                    title="Geographic Distribution (No Data Available)",
                    xaxis_title="Country",
                    yaxis_title="Allocation (%)"
                )
            )
    else:
        # Use the country and country_allocation columns
        geo_data = df.groupby('country')['country_allocation'].sum().reset_index()
        geo_data.columns = ['country', 'allocation']
    
    # Sort by allocation (descending)
    geo_data = geo_data.sort_values('allocation', ascending=False)
    
    # Take top 10 countries
    top_countries = geo_data.head(10).copy()
    
    # Create a horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=top_countries['country'],
            x=top_countries['allocation'],
            orientation='h',
            marker_color='#4285F4',
            hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
        )
    ])
    
    # Update layout
    fig.update_layout(
        title="Top Countries by Allocation",
        xaxis_title="Allocation (%)",
        yaxis=dict(
            title="Country",
            categoryorder='total ascending'
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_sector_breakdown_chart(df):
    """
    Create a chart showing the sector breakdown of the portfolio.
    
    Args:
        df (pd.DataFrame): The dataframe containing portfolio data
        
    Returns:
        plotly.graph_objects.Figure: Horizontal bar chart of sector breakdown
    """
    # Check if we have sector data
    if 'sector' not in df.columns or 'sector_allocation' not in df.columns:
        # Try to extract from other columns or use placeholder
        if 'Settore' in df.columns and 'Allocazione Settore' in df.columns:
            sector_data = df.groupby('Settore')['Allocazione Settore'].sum().reset_index()
            sector_data.columns = ['sector', 'allocation']
        else:
            # Create a placeholder chart
            return go.Figure(
                data=[go.Bar(x=['No Data'], y=[0])],
                layout=dict(
                    title="Sector Breakdown (No Data Available)",
                    xaxis_title="Sector",
                    yaxis_title="Allocation (%)"
                )
            )
    else:
        # Use the sector and sector_allocation columns
        sector_data = df.groupby('sector')['sector_allocation'].sum().reset_index()
        sector_data.columns = ['sector', 'allocation']
    
    # Sort by allocation (descending)
    sector_data = sector_data.sort_values('allocation', ascending=False)
    
    # Take top 10 sectors
    top_sectors = sector_data.head(10).copy()
    
    # Create a horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=top_sectors['sector'],
            x=top_sectors['allocation'],
            orientation='h',
            marker_color='#34A853',
            hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
        )
    ])
    
    # Update layout
    fig.update_layout(
        title="Top Sectors by Allocation",
        xaxis_title="Allocation (%)",
        yaxis=dict(
            title="Sector",
            categoryorder='total ascending'
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig
    
def create_performance_chart(df, transaction_df=None):
    """
    Create a chart showing the performance trend over time for portfolio holdings.
    
    Args:
        df (pd.DataFrame): The dataframe containing portfolio data
        transaction_df (pd.DataFrame, optional): The dataframe containing transaction history 
            with dates. This is used to determine the time range.
        
    Returns:
        plotly.graph_objects.Figure: Line chart of performance trend
    """
    # Initialize chart
    fig = go.Figure()
    
    # Check if we have the necessary data to create a performance chart
    if 'Rendimento %' not in df.columns and 'return_percentage' not in df.columns:
        # Create a placeholder chart with explanatory text
        fig.add_annotation(
            text="Dati di rendimento insufficienti per creare il grafico dell'andamento",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title="Andamento dei Rendimenti (Dati Insufficienti)",
            xaxis_title="Data",
            yaxis_title="Rendimento (%)"
        )
        return fig
    
    # Determine the column name for return percentage
    return_col = 'Rendimento %' if 'Rendimento %' in df.columns else 'return_percentage'
    
    # Define value column 
    value_col = 'Controvalore' if 'Controvalore' in df.columns else 'value'
    
    # Determine the appropriate timeframe based on the data
    earliest_date = None
    latest_date = None

    # First check if we have transaction data with the original dates
    if transaction_df is not None and 'Operazione' in transaction_df.columns:
        try:
            # Convert dates from the transaction dataframe
            date_series = pd.to_datetime(transaction_df['Operazione'], format='%d/%m/%Y', errors='coerce')
            valid_dates = date_series.dropna()
            
            if not valid_dates.empty:
                earliest_date = valid_dates.min()
                latest_date = valid_dates.max()
                
                print(f"FROM TRANSACTION DF - Earliest date found: {earliest_date.strftime('%d/%m/%Y')}")
                print(f"FROM TRANSACTION DF - Latest date found: {latest_date.strftime('%d/%m/%Y')}")
        except Exception as e:
            print(f"Error parsing dates from transaction_df: {str(e)}")
            
    # Fallback to checking the main dataframe if no valid dates found yet
    if earliest_date is None and 'Operazione' in df.columns:
        try:
            # Convert all date strings to datetime objects, coercing errors
            date_series = pd.to_datetime(df['Operazione'], format='%d/%m/%Y', errors='coerce')
            
            # Filter out NaT (Not a Time) values
            valid_dates = date_series.dropna()
            
            if not valid_dates.empty:
                earliest_date = valid_dates.min()
                latest_date = valid_dates.max()
                
                print(f"FROM MAIN DF - Earliest date found: {earliest_date.strftime('%d/%m/%Y')}")
                print(f"FROM MAIN DF - Latest date found: {latest_date.strftime('%d/%m/%Y')}")
        except Exception as e:
            print(f"Error parsing dates from main df: {str(e)}")
    
    # If we have valid dates from either source, use them
    if earliest_date is not None and latest_date is not None:
        # Force start date to be December 1, 2023 if mentioned in the original data
        december_2023 = pd.to_datetime('01/12/2023', format='%d/%m/%Y')
        
        # Check if earliest date is close to Dec 2023 (within a few days)
        if abs((earliest_date - december_2023).days) <= 5:
            # Use exactly December 1, 2023
            start_date = december_2023
            print(f"Using exact date Dec 1, 2023 based on the approximate match")
        else:
            # Make sure we have at least 3 months of data
            if (latest_date - earliest_date).days < 90:
                start_date = earliest_date - timedelta(days=30)  # Add buffer
            else:
                start_date = earliest_date
        
        # Always show up to present date
        end_date = datetime.now()
    else:
        # Default: show 1 year of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
    
    # Create date range with monthly frequency
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Color palette for different securities
    colors = ['#4285F4', '#34A853', '#FBBC05', '#EA4335', '#8F44AA']
    
    # Calculate portfolio performance (weighted average of all securities)
    # If we're looking at a filtered view, we need to recalculate the portfolio total
    total_portfolio_value = df[value_col].sum()
    
    # Calculate weighted return for the displayed portfolio/selection
    if total_portfolio_value > 0:
        portfolio_return = (df[value_col] * df[return_col]).sum() / total_portfolio_value
    else:
        portfolio_return = 0
        
    # Add portfolio performance line (thicker line)
    np.random.seed(42)  # Use fixed seed for consistent results
    portfolio_volatility = 0.6  # Moderate volatility
    portfolio_random_walk = np.random.normal(0, portfolio_volatility, len(dates) - 1)
    portfolio_monthly_returns = np.concatenate([np.array([0]), portfolio_random_walk])
    
    # Add a bias toward the final portfolio return value
    bias = np.linspace(0, portfolio_return, len(dates)) - portfolio_monthly_returns.cumsum()
    adjusted_portfolio_returns = portfolio_monthly_returns + bias * 0.5
    
    # Calculate the cumulative portfolio performance in euros
    # Use the total portfolio value as starting point
    portfolio_performance_base = 100 * (1 + adjusted_portfolio_returns / 100).cumprod()
    
    # Scale to actual euro values (start with the total portfolio value)
    portfolio_performance_euro = total_portfolio_value * portfolio_performance_base / 100
    
    # Add the portfolio performance line
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_performance_euro,
        mode='lines',
        name='Portafoglio Completo',
        line=dict(color='#E91E63', width=3),
        hovertemplate='%{x}<br>%{y:.2f}€<extra>Portafoglio Completo</extra>'
    ))
    
    # Get top 3 holdings by value (instead of 5, since we're adding portfolio)
    top_holdings = df.sort_values(by=value_col, ascending=False).head(3)
    
    # Add a line for each top holding
    for i, (_, security) in enumerate(top_holdings.iterrows()):
        # Get the current return value
        current_return_pct = float(security[return_col])
        
        # Generate a simulated performance curve
        volatility_factor = 0.5 + (abs(current_return_pct) / 10) 
        np.random.seed(hash(str(i)) % 10000)  # Use index as seed for consistent results
        random_walk = np.random.normal(0, volatility_factor, len(dates) - 1)
        monthly_returns = np.concatenate([np.array([0]), random_walk])
        
        # Add a slight bias toward the final return value
        target_return = current_return_pct
        bias = np.linspace(0, target_return, len(dates)) - monthly_returns.cumsum()
        adjusted_returns = monthly_returns + bias * 0.3
        
        # Calculate the cumulative performance as base 100
        cumulative_performance_base = 100 * (1 + adjusted_returns / 100).cumprod()
        
        # Get the actual value of this security
        security_value = float(security[value_col])
        
        # Convert to euro values
        security_performance_euro = security_value * cumulative_performance_base / 100
        
        # Format name for display
        name_col = 'Nome' if 'Nome' in df.columns else 'Titolo' if 'Titolo' in df.columns else 'name'
        name = security[name_col]
        
        # Add the line to the chart
        fig.add_trace(go.Scatter(
            x=dates,
            y=security_performance_euro,
            mode='lines',
            name=name,
            line=dict(color=colors[i % len(colors)], width=1.5),
            hovertemplate='%{x}<br>%{y:.2f}€<extra>' + name + '</extra>'
        ))
    
    # Add a market reference line (benchmark)
    np.random.seed(99)  # Use fixed seed for consistency
    market_volatility = 0.4
    market_random_walk = np.random.normal(0, market_volatility, len(dates) - 1)
    market_monthly_returns = np.concatenate([np.array([0]), market_random_walk])
    market_performance_base = 100 * (1 + market_monthly_returns / 100).cumprod()
    
    # Scale the benchmark to a meaningful euro value (e.g., 30% of portfolio)
    benchmark_start_value = total_portfolio_value * 0.3  # A smaller value to avoid cluttering
    market_performance_euro = benchmark_start_value * market_performance_base / 100
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=market_performance_euro,
        mode='lines',
        name='Benchmark',
        line=dict(color='#757575', dash='dash'),
        hovertemplate='%{x}<br>%{y:.2f}€<extra>Benchmark</extra>'
    ))
    
    # Calculate timeframe description for title
    # Get differences in days and months
    days_diff = (end_date - start_date).days
    months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    # Create appropriate timeframe description
    if days_diff <= 31:
        timeframe = "Ultimo mese"
    elif days_diff <= 93:
        timeframe = f"Ultimi {months_diff} mesi"
    elif days_diff <= 370:
        timeframe = "Ultimo anno"
    else:
        years = days_diff // 365
        months = (days_diff % 365) // 30
        if months > 0:
            timeframe = f"Ultimi {years} anni e {months} mesi"
        else:
            timeframe = f"Ultimi {years} anni"
    
    # Update layout
    fig.update_layout(
        title=f"Andamento dei Rendimenti ({timeframe})",
        xaxis_title="Data",
        yaxis_title="Valore (€)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=40, b=80)
    )
    
    # Add a note about data simulation
    fig.add_annotation(
        text="Nota: Questo grafico è basato su dati stimati per scopi di visualizzazione",
        xref="paper", yref="paper",
        x=0.5, y=-0.25,
        showarrow=False,
        font=dict(size=10, color="gray")
    )
    
    return fig