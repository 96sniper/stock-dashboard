import streamlit as st
import streamlit.components.v1 as components
import base64
import pandas as pd
import os
from pdf2image import convert_from_path
from datetime import date, timedelta
import glob

# Set to Wide Mode
st.set_page_config(layout="wide")

# Inject light gray theme with markdown
st.markdown("""
    <style>
    .stApp {
        background-color: #e6e6e6;  /* Light gray background */
        color: #000000;  /* Black text */
    }

    .block-container {
        padding: 1.5rem 2rem;
    }

    .stTabs [role="tablist"] {
        background-color: #d9d9d9;
    }

    .stTabs [role="tab"] {
        color: #333;
        font-weight: bold;
    }

    h1, h2, h3, h4 {
        color: #1a1a1a;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Stock Market Dashboard")

####################################################################################################################################################################

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(["Home Page", "Daily Tail Candles", "Daily Close Above/Below",
                                                          "Weekly Tail Candles", "Weekly Close Above/Below", 
                                                          "Monthly Tail Candles", "Monthly Close Above/Below",
                                                          "Upcoming Earnings", "MACD - Overbought/Oversold", 
                                                          "Mercury Retrograde Dates", "Notes"])

# Home Page
with tab1:

    # SPY Seasonality
    st.header("SPY Seasonality")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "spy_seasonality" and ending in .png
    pattern = os.path.join(base_dir, "spy_seasonality_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("SPY seasonality image not found.")

    # QQQ Seasonality
    st.subheader("QQQ Seasonality")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "qqq_seasonality" and ending in .png
    pattern = os.path.join(base_dir, "qqq_seasonality_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("QQQ seasonality image not found.")

    # IWM Seasonality
    st.subheader("IWM Seasonality")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "iwm_seasonality" and ending in .png
    pattern = os.path.join(base_dir, "iwm_seasonality_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("IWM seasonality image not found.")

# Daily Tails
with tab2:
    st.header("Daily Tail Candles")
    st.write("Daily Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "daily_tail_candle_count" and ending in .png
    pattern = os.path.join(base_dir, "daily_tail_candle_count_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Daily Tail Candle Count image not found.")

    # Display Bullish Tail Candles
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "daily_summary_data" and ending in .xlsx
    pattern = os.path.join(base_dir, "daily_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified file
        latest_file = max(matching_files, key=os.path.getmtime)
    
        try:
            df = pd.read_excel(latest_file)
            #st.dataframe(df, use_container_width=True)
        
            # Filter for Bullish Wick candles
            bullish_wicks = df[df["Candle Signal"] == "Bullish Wick"]  
            bullish_wick_count = len(bullish_wicks)

            st.subheader(f"Daily Bullish Wick Candles — Count: {bullish_wick_count}")

            if not bullish_wicks.empty:
                st.dataframe(bullish_wicks.reset_index(drop=True))
            else:
                st.info("No rows found where Candle Signal is 'Bullish Wick'.")
        except Exception as e:
            st.error(f"⚠️ Failed to load XLSX file: {e}")
    else:
        st.warning("Daily Summary Data file not found.")

    # Display Bearish Tail Candles
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "daily_summary_data" and ending in .xlsx
    pattern = os.path.join(base_dir, "daily_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified file
        latest_file = max(matching_files, key=os.path.getmtime)
    
        try:
            df = pd.read_excel(latest_file)
            #st.dataframe(df, use_container_width=True)
        
            # Filter for Bearish Wick candles
            bearish_wicks = df[df["Candle Signal"] == "Bearish Wick"]  
            bearish_wick_count = len(bearish_wicks)

            st.subheader(f"Daily Bearish Wick Candles — Count: {bearish_wick_count}")

            if not bearish_wicks.empty:
                st.dataframe(bearish_wicks.reset_index(drop=True))
            else:
                st.info("No rows found where Candle Signal is 'Bearish Wick'.")
        except Exception as e:
            st.error(f"⚠️ Failed to load XLSX file: {e}")
    else:
        st.warning("Daily Summary Data file not found.")

# Daily Closes
with tab3:
    st.header("Daily Close Above/Below")
    st.write("Daily Close Above Candles minus Daily Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "daily_close_above_below_count" and ending in .png
    pattern = os.path.join(base_dir, "daily_close_above_below_count_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Daily Close Above Below Count image not found.")

# Weekly Tails
with tab4:
    st.header("Weekly Tail Candles")
    st.write("Weekly Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "weekly_tail_candle_count" and ending in .png
    pattern = os.path.join(base_dir, "weekly_tail_candle_count_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Weekly Tail Candle Count image not found.")

    # Display Bullish Tail Candles
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "weekly_summary_data" and ending in .xlsx
    pattern = os.path.join(base_dir, "weekly_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified file
        latest_file = max(matching_files, key=os.path.getmtime)
    
        try:
            df = pd.read_excel(latest_file)
            #st.dataframe(df, use_container_width=True)
        
            # Filter for Bullish Wick candles
            bullish_wicks = df[df["Candle Signal"] == "Bullish Wick"]  
            bullish_wick_count = len(bullish_wicks)

            st.subheader(f"Weekly Bullish Wick Candles — Count: {bullish_wick_count}")

            if not bullish_wicks.empty:
                st.dataframe(bullish_wicks.reset_index(drop=True))
            else:
                st.info("No rows found where Candle Signal is 'Bullish Wick'.")
        except Exception as e:
            st.error(f"⚠️ Failed to load CSV file: {e}")
    else:
        st.warning("Weekly Summary Data file not found.")

    # Display Bearish Tail Candles
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "weekly_summary_data" and ending in .xlsx
    pattern = os.path.join(base_dir, "weekly_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified file
        latest_file = max(matching_files, key=os.path.getmtime)
    
        try:
            df = pd.read_excel(latest_file)
            #st.dataframe(df, use_container_width=True)
        
            # Filter for Bearish Wick candles
            bearish_wicks = df[df["Candle Signal"] == "Bearish Wick"]  
            bearish_wick_count = len(bearish_wicks)

            st.subheader(f"Weekly Bearish Wick Candles — Count: {bearish_wick_count}")

            if not bearish_wicks.empty:
                st.dataframe(bearish_wicks.reset_index(drop=True))
            else:
                st.info("No rows found where Candle Signal is 'Bearish Wick'.")
        except Exception as e:
            st.error(f"⚠️ Failed to load XLSX file: {e}")
    else:
        st.warning("Weekly Summary Data file not found.")

# Weekly Closes
with tab5:
    st.header("Weekly Close Above/Below")
    st.write("Weekly Close Above Candles minus Weekly Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "weekly_close_above_below_count" and ending in .png
    pattern = os.path.join(base_dir, "weekly_close_above_below_count_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Weekly Close Above Below Count image not found.")

# Monthly Tails
with tab6:
    st.header("Monthly Tail Candles")
    st.write("Monthly Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "monthly_tail_candle_count" and ending in .png
    pattern = os.path.join(base_dir, "monthly_tail_candle_count_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Monthly Tail Candle Count image not found.")

    # Display Bullish Tail Candles
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "monthly_summary_data" and ending in .xlsx
    pattern = os.path.join(base_dir, "monthly_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified file
        latest_file = max(matching_files, key=os.path.getmtime)
    
        try:
            df = pd.read_excel(latest_file)
            #st.dataframe(df, use_container_width=True)
        
            # Filter for Bullish Wick candles
            bullish_wicks = df[df["Candle Signal"] == "Bullish Wick"]  
            bullish_wick_count = len(bullish_wicks)

            st.subheader(f"Monthly Bullish Wick Candles — Count: {bullish_wick_count}")

            if not bullish_wicks.empty:
                st.dataframe(bullish_wicks.reset_index(drop=True))
            else:
                st.info("No rows found where Candle Signal is 'Bullish Wick'.")
        except Exception as e:
            st.error(f"⚠️ Failed to load XLSX file: {e}")
    else:
        st.warning("Monthly Summary Data file not found.")

    # Display Bearish Tail Candles
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "monthly_summary_data" and ending in .xlsx
    pattern = os.path.join(base_dir, "monthly_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified file
        latest_file = max(matching_files, key=os.path.getmtime)
    
        try:
            df = pd.read_excel(latest_file)
            #st.dataframe(df, use_container_width=True)
        
            # Filter for Bearish Wick candles
            bearish_wicks = df[df["Candle Signal"] == "Bearish Wick"]  
            bearish_wick_count = len(bearish_wicks)

            st.subheader(f"Monthly Bearish Wick Candles — Count: {bearish_wick_count}")

            if not bearish_wicks.empty:
                st.dataframe(bearish_wicks.reset_index(drop=True))
            else:
                st.info("No rows found where Candle Signal is 'Bearish Wick'.")
        except Exception as e:
            st.error(f"⚠️ Failed to load XLSX file: {e}")
    else:
        st.warning("Monthly Summary Data file not found.")


# Monthly Closes
with tab7:
    st.header("Monthly Close Above/Below")
    st.write("Monthly Close Above Candles minus Monthly Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "monthly_close_above_below_count" and ending in .png
    pattern = os.path.join(base_dir, "monthly_close_above_below_count_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Monthly Close Above Below Count image not found.")


# Upcoming Earnings
with tab8:
    st.header("Upcoming Earnings")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "earnings_calendar" and ending in .csv
    pattern = os.path.join(base_dir, "earnings_calendar_*.csv")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        
        try:
            df = pd.read_csv(latest_file)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Failed to load CSV file: {e}")
    else:
        st.warning("earnings calendar file not found.")

# MACD Overbought/Oversold
with tab9:
    st.header("MACD Overbought/Oversold")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "macd_values" and ending in .csv
    pattern = os.path.join(base_dir, "macd_values_*.csv")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        
        try:
            df = pd.read_csv(latest_file)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Failed to load CSV file: {e}")
    else:
        st.warning("macd values file not found.")

# Mercury Retrograde Dates
with tab10:
    st.header("Mercury Retrograde Dates")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "mercury_retrograde" and ending in .csv
    pattern = os.path.join(base_dir, "mercury_retrograde_*.csv")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        
        try:
            df = pd.read_csv(latest_file)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Failed to load CSV file: {e}")
    else:
        st.warning("Mercury Retrograde Dates file not found.")

#######################################################################################################################################################################


