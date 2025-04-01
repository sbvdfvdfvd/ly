import streamlit as st
import pandas as pd
import os
import traceback
from portfolio_analyzer import process_portfolio_data, calculate_asset_allocation
from visualization import (
    create_donut_chart, 
    create_geographic_distribution_chart,
    create_sector_breakdown_chart
)
from utils import format_currency, format_percentage, render_performance_indicator

# Set page configuration
st.set_page_config(
    page_title="Portfolio Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Main title
st.title("Portfolio Analysis Dashboard")
st.markdown("Upload your portfolio Excel file to analyze your investment allocation and performance.")

# File uploader
uploaded_file = st.file_uploader("Choose a portfolio Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Try to process the uploaded file
        raw_df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # First, check if this is a "Lista Titoli" format (transaction list)
        is_transaction_list = False
        header_row = None
        
        # Look for the row that contains 'Operazione' which indicates a transaction list format
        for i, row in raw_df.iterrows():
            if 'Operazione' in str(row.values):
                header_row = i
                is_transaction_list = True
                break
        
        if is_transaction_list and header_row is not None:
            st.info("Detected transaction list format. Processing transactions to calculate your portfolio...")
            
            # Use the identified header row to set column names, and start data from next row
            df = raw_df.copy()
            df.columns = df.iloc[header_row].values
            df = df.iloc[header_row+1:].reset_index(drop=True)
            
            # Drop rows where all values are NaN
            df = df.dropna(how='all')
            
            # Analyze the securities in the portfolio
            securities = df.groupby(['Titolo', 'Isin']).agg(
                total_quantity=('Quantita', 'sum'),
                avg_price=('Prezzo', 'mean'),
                total_value=('Controvalore', 'sum')
            ).reset_index()
            
            # Sort by total value
            securities = securities.sort_values('total_value', ascending=False)
            
            # Calculate total portfolio value
            total_portfolio_value = securities['total_value'].sum()
            
            # Attempt to categorize securities based on their names
            def categorize_security(name):
                name = str(name).lower()
                if any(term in name for term in ['cr 500', 'msci', 'equity', 'wd']):
                    return 'Azionario'
                elif any(term in name for term in ['gov', 'bond', 'ehycb']):
                    return 'Obbligazionario'
                elif any(term in name for term in ['gold', 'or', 'commodity']):
                    return 'Materie Prime'
                else:
                    return 'Altro'
            
            # Add category to securities
            securities['Categoria'] = securities['Titolo'].apply(categorize_security)
            
            # Calculate allocation percentage
            securities['Allocazione'] = (securities['total_value'] / total_portfolio_value * 100).round(2)
            
            # Estimate TER based on ETF type (just a placeholder, we don't have actual TER data)
            def estimate_ter(row):
                categoria = row['Categoria'].lower()
                if 'azionario' in categoria:
                    return 0.20  # Typical for stock ETFs
                elif 'obbligazionario' in categoria:
                    return 0.15  # Typical for bond ETFs
                elif 'materie prime' in categoria:
                    return 0.25  # Typical for commodity ETFs
                else:
                    return 0.22  # Default
            
            securities['TER'] = securities.apply(estimate_ter, axis=1)
            
            # Rename columns to match the expected format
            securities = securities.rename(columns={
                'Titolo': 'Nome',
                'total_value': 'Controvalore'
            })
            
            # Add placeholder return values (since we don't have actual return data)
            # In a real implementation, you would calculate this based on historical prices
            securities['Rendimento %'] = 0.0
            securities['Rendimento'] = 0.0
            
            # Use this prepared data
            df = securities
            
            # Process the data with our existing functions
            portfolio_data = {
                "data": df,
                "total_value": total_portfolio_value,
                "total_return_value": 0,  # We don't have this information
                "total_return_percentage": 0  # We don't have this information
            }
            
            # Calculate asset allocation
            asset_allocation = df.groupby('Categoria').agg(
                value=('Controvalore', 'sum')
            ).reset_index()
            asset_allocation['allocation'] = asset_allocation['value'] / asset_allocation['value'].sum() * 100
            asset_allocation = asset_allocation.rename(columns={'Categoria': 'asset_class'})
            
            # Make sure all major asset classes are represented (even with 0%)
            major_asset_classes = ['Azionario', 'Obbligazionario', 'Materie Prime', 'Liquidità']
            
            existing_classes = asset_allocation['asset_class'].tolist()
            for asset_class in major_asset_classes:
                if asset_class not in existing_classes:
                    asset_allocation = pd.concat([
                        asset_allocation,
                        pd.DataFrame({'asset_class': [asset_class], 'value': [0], 'allocation': [0]})
                    ], ignore_index=True)
            
            # Sort by allocation (descending)
            asset_allocation = asset_allocation.sort_values('allocation', ascending=False)
            
            # Dashboard layout
            col1, col2 = st.columns([3, 1])
            
            with col2:
                st.subheader("Panoramica Portafoglio")
                st.metric(
                    label="Valore Totale", 
                    value=format_currency(total_portfolio_value)
                )
                
            with col1:
                st.subheader("Allocazione Asset")
                donut_chart = create_donut_chart(asset_allocation)
                st.plotly_chart(donut_chart, use_container_width=True)
            
            # Filter options
            st.sidebar.header("Filtri")
            
            # Asset class filter
            categories = df["Categoria"].unique().tolist()
            asset_classes = ["Tutti"] + sorted(categories)
            selected_asset_class = st.sidebar.selectbox("Categoria Asset", asset_classes)
            
            # Filter the data
            filtered_df = df.copy()
            if selected_asset_class != "Tutti":
                filtered_df = filtered_df[filtered_df["Categoria"] == selected_asset_class]
            
            # Detailed holdings table
            st.subheader("Titoli in Portafoglio")
            
            # Format the dataframe for display
            display_df = filtered_df.copy()
            
            # Format financial columns
            display_df["Controvalore"] = display_df["Controvalore"].apply(format_currency)
            
            # Apply color formatting to return percentages
            display_df["Rendimento %"] = display_df["Rendimento %"].apply(
                lambda x: render_performance_indicator(x)
            )
            
            # Select and reorder columns for display
            display_columns = ['Nome', 'Categoria', 'TER', 'Allocazione', 'Controvalore']
            if 'Rendimento %' in display_df.columns:
                display_columns.append('Rendimento %')
            
            # Display the table
            st.dataframe(display_df[display_columns], use_container_width=True)
            
        else:
            # Check if the dataframe has the required columns for standard portfolio format
            required_columns = ["Nome", "Categoria", "TER", "Allocazione", "Controvalore", "Rendimento %", "Rendimento"]
            missing_columns = [col for col in required_columns if col not in raw_df.columns]
            
            if missing_columns:
                st.error(f"Il file Excel non contiene le colonne richieste: {', '.join(missing_columns)}")
                st.info("Assicurati che il tuo file Excel contenga le seguenti colonne: Nome, Categoria, TER, Allocazione, Controvalore, Rendimento %, Rendimento. Oppure carica un file con lista di transazioni.")
            else:
                # Process with standard format
                df = raw_df
                portfolio_data = process_portfolio_data(df)
                
                # Get total portfolio value and performance metrics
                total_value = portfolio_data["total_value"]
                total_return_value = portfolio_data["total_return_value"]
                total_return_percentage = portfolio_data["total_return_percentage"]
                
                # Dashboard layout
                col1, col2 = st.columns([3, 1])
                
                with col2:
                    st.subheader("Panoramica Portafoglio")
                    st.metric(
                        label="Valore Totale", 
                        value=format_currency(total_value), 
                        delta=f"{format_currency(total_return_value)} ({format_percentage(total_return_percentage)})"
                    )
                    
                with col1:
                    st.subheader("Allocazione Asset")
                    asset_allocation = calculate_asset_allocation(df)
                    donut_chart = create_donut_chart(asset_allocation)
                    st.plotly_chart(donut_chart, use_container_width=True)
                
                # Filter options
                st.sidebar.header("Filtri")
                
                # Asset class filter
                if "asset_class" in df.columns:
                    asset_classes = ["Tutti"] + sorted(df["asset_class"].unique().tolist())
                    selected_asset_class = st.sidebar.selectbox("Classe di Asset", asset_classes)
                else:
                    # Try to extract asset class from category
                    categories = df["Categoria"].unique().tolist()
                    asset_classes = ["Tutti"] + sorted(categories)
                    selected_asset_class = st.sidebar.selectbox("Categoria", asset_classes)
                
                # Country filter if available
                if "country" in df.columns:
                    countries = ["Tutti"] + sorted(df["country"].unique().tolist())
                    selected_country = st.sidebar.selectbox("Paese", countries)
                else:
                    selected_country = "Tutti"
                
                # Filter the data
                filtered_df = df.copy()
                if selected_asset_class != "Tutti":
                    if "asset_class" in df.columns:
                        filtered_df = filtered_df[filtered_df["asset_class"] == selected_asset_class]
                    else:
                        filtered_df = filtered_df[filtered_df["Categoria"] == selected_asset_class]
                
                if selected_country != "Tutti" and "country" in df.columns:
                    filtered_df = filtered_df[filtered_df["country"] == selected_country]
                
                # Detailed holdings table
                st.subheader("Titoli in Portafoglio")
                
                # Format the dataframe for display
                display_df = filtered_df.copy()
                
                # Format financial columns
                if "Controvalore" in display_df.columns:
                    display_df["Controvalore"] = display_df["Controvalore"].apply(format_currency)
                
                if "Rendimento" in display_df.columns:
                    display_df["Rendimento"] = display_df["Rendimento"].apply(format_currency)
                
                # Apply color formatting to return percentages
                if "Rendimento %" in display_df.columns:
                    # Save original values for sorting
                    display_df["_return_pct_original"] = display_df["Rendimento %"]
                    display_df["Rendimento %"] = display_df["Rendimento %"].apply(
                        lambda x: render_performance_indicator(x)
                    )
                
                # Remove any temporary columns used for sorting
                if "_return_pct_original" in display_df.columns:
                    display_df = display_df.drop("_return_pct_original", axis=1)
                
                # Display the table
                st.dataframe(display_df, use_container_width=True)
                
                # Geographic Distribution
                st.subheader("Distribuzione Geografica")
                
                # Check if we have geographic data
                if "country" in df.columns and "country_allocation" in df.columns:
                    geo_chart = create_geographic_distribution_chart(df)
                    st.plotly_chart(geo_chart, use_container_width=True)
                else:
                    st.info("I dati sulla distribuzione geografica non sono disponibili nel file caricato. Assicurati che il file contenga le colonne 'country' e 'country_allocation' per l'analisi geografica.")
                
                # Sector Breakdown (if data available)
                if "sector" in df.columns and "sector_allocation" in df.columns:
                    st.subheader("Suddivisione Settoriale")
                    sector_chart = create_sector_breakdown_chart(df)
                    st.plotly_chart(sector_chart, use_container_width=True)
            
    except Exception as e:
        st.error(f"Errore durante l'elaborazione del file: {str(e)}")
        st.error(traceback.format_exc())
else:
    # Sample instructions when no file is uploaded
    st.info("Carica un file Excel contenente i dati del tuo portafoglio.")
    
    st.markdown("""
    ### Formati di file supportati
    
    #### 1. Formato Standard di Portafoglio
    Il tuo file Excel dovrebbe contenere le seguenti colonne:
    - **Nome**: Nome del titolo
    - **Categoria**: Tipo di asset (es. Azioni, Obbligazioni, Liquidità)
    - **TER**: Total Expense Ratio
    - **Allocazione**: Percentuale di allocazione attuale
    - **Controvalore**: Valore monetario attuale
    - **Rendimento %**: Percentuale di rendimento
    - **Rendimento**: Valore assoluto del rendimento
    
    #### 2. Formato Elenco Transazioni
    In alternativa, puoi caricare un file con storico transazioni che contiene:
    - **Operazione**: Data dell'operazione
    - **Titolo**: Nome del titolo
    - **Isin**: Codice ISIN
    - **Quantita**: Numero di unità
    - **Prezzo**: Prezzo unitario
    - **Controvalore**: Valore totale
    
    Colonne opzionali per analisi avanzate:
    - **country**: Allocazione per paese
    - **country_allocation**: Percentuale di allocazione per paese
    - **sector**: Informazioni sul settore
    - **sector_allocation**: Percentuale di allocazione per settore
    """)

# Footer
st.markdown("---")
st.markdown("Portfolio Analysis Dashboard | Made with Streamlit")