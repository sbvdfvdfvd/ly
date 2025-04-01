import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

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