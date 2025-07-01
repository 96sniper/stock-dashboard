import streamlit as st
import streamlit.components.v1 as components
import base64
import pandas as pd
import os
from pdf2image import convert_from_path
from datetime import date, timedelta

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["Home Page", "Daily Tail Candles", "Daily Close Above/Below",
                                                          "Weekly Tail Candles", "Weekly Close Above/Below", 
                                                          "Monthly Tail Candles", "Monthly Close Above/Below",
                                                          "Upcoming Earnings", "Hourly Candles"])

# Home Page
with tab1:

    # SPY Seasonality
    st.header("SPY Seasonality")

    image_path = os.path.join(os.path.dirname(__file__), "spy_seasonality.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("SPY seasonality image not found.")

    # QQQ Seasonality
    st.subheader("QQQ Seasonality")

    image_path = os.path.join(os.path.dirname(__file__), "qqq_seasonality.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("QQQ seasonality image not found.")

    # IWM Seasonality
    st.subheader("IWM Seasonality")

    image_path = os.path.join(os.path.dirname(__file__), "iwm_seasonality.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("IWM seasonality image not found.")

# Daily Tails
with tab2:
    st.header("Daily Tail Candles")
    st.write("Daily Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    
    #pdf_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\daily_tail_candle_count.pdf"
    image_path = os.path.join(os.path.dirname(__file__), "daily_tail_candle_count.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("Daily Tail Candle Count image not found.")

    # Display Bullish Tail Candles
    #excel_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\daily_summary_data.xlsx"
    excel_path = os.path.join(os.path.dirname(__file__), "daily_summary_data.xlsx")
    try:
        df = pd.read_excel(excel_path)
        bullish_wicks = df[df["Candle Signal"] == "Bullish Wick"]  
        bullish_wick_count = len(bullish_wicks)
        
        st.subheader(f"Daily Bullish Wick Candles — Count: {bullish_wick_count}")

        if not bullish_wicks.empty:
            st.dataframe(bullish_wicks.reset_index(drop=True))
        else:
            st.info("No rows found where Candle Signal is 'Bullish Wick'.")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")

    # Display Bearish Tail Candles
    #excel_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\daily_summary_data.xlsx"
    excel_path = os.path.join(os.path.dirname(__file__), "daily_summary_data.xlsx")
    try:
        df = pd.read_excel(excel_path)
        bearish_wicks = df[df["Candle Signal"] == "Bearish Wick"]
        bearish_wick_count = len(bearish_wicks)

        st.subheader(f"Daily Bearish Wick Candles — Count: {bearish_wick_count}")
        
        if not bearish_wicks.empty:
            st.dataframe(bearish_wicks.reset_index(drop=True))
        else:
            st.info("No rows found where Candle Signal is 'Bearish Wick'.")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")

# Daily Closes
with tab3:
    st.header("Daily Close Above/Below")
    st.write("Daily Close Above Candles minus Daily Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")
    
    #pdf_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\daily_close_above_below_count.pdf"
    image_path = os.path.join(os.path.dirname(__file__), "daily_close_above_below_count.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("Daily Close Above Below Count image not found.")

# Weekly Tails
with tab4:
    st.header("Weekly Tail Candles")
    st.write("Weekly Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    
    #pdf_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\weekly_tail_candle_count.pdf"
    image_path = os.path.join(os.path.dirname(__file__), "weekly_tail_candle_count.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("Weekly Tail Candle Count image not found.")

    # Display Bullish Tail Candles
    #excel_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\weekly_summary_data.xlsx"
    excel_path = os.path.join(os.path.dirname(__file__), "weekly_summary_data.xlsx")
    try:
        df = pd.read_excel(excel_path)
        bullish_wicks = df[df["Candle Signal"] == "Bullish Wick"]  
        bullish_wick_count = len(bullish_wicks)
        
        st.subheader(f"Weekly Bullish Wick Candles — Count: {bullish_wick_count}")

        if not bullish_wicks.empty:
            st.dataframe(bullish_wicks.reset_index(drop=True))
        else:
            st.info("No rows found where Candle Signal is 'Bullish Wick'.")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")

    # Display Bearish Tail Candles
    #excel_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\weekly_summary_data.xlsx"
    excel_path = os.path.join(os.path.dirname(__file__), "weekly_summary_data.xlsx")
    try:
        df = pd.read_excel(excel_path)
        bearish_wicks = df[df["Candle Signal"] == "Bearish Wick"]
        bearish_wick_count = len(bearish_wicks)

        st.subheader(f"Weekly Bearish Wick Candles — Count: {bearish_wick_count}")
        
        if not bearish_wicks.empty:
            st.dataframe(bearish_wicks.reset_index(drop=True))
        else:
            st.info("No rows found where Candle Signal is 'Bearish Wick'.")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")

# Weekly Closes
with tab5:
    st.header("Weekly Close Above/Below")
    st.write("Weekly Close Above Candles minus Weekly Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")
    
    #pdf_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\weekly_close_above_below_count.pdf"
    image_path = os.path.join(os.path.dirname(__file__), "weekly_close_above_below_count.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("Weekly Close Above Below Count image not found.")

# Monthly Tails
with tab6:
    st.header("Monthly Tail Candles")
    st.write("Monthly Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    
    #pdf_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\monthly_tail_candle_count.pdf"
    image_path = os.path.join(os.path.dirname(__file__), "monthly_tail_candle_count.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("Monthly Tail Candle Count image not found.")

    # Display Bullish Tail Candles
    #excel_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\monthly_summary_data.xlsx"
    excel_path = os.path.join(os.path.dirname(__file__), "monthly_summary_data.xlsx")
    try:
        df = pd.read_excel(excel_path)
        bullish_wicks = df[df["Candle Signal"] == "Bullish Wick"]  
        bullish_wick_count = len(bullish_wicks)
        
        st.subheader(f"Monthly Bullish Wick Candles — Count: {bullish_wick_count}")

        if not bullish_wicks.empty:
            st.dataframe(bullish_wicks.reset_index(drop=True))
        else:
            st.info("No rows found where Candle Signal is 'Bullish Wick'.")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")

    # Display Bearish Tail Candles
    #excel_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\monthly_summary_data.xlsx"
    excel_path = os.path.join(os.path.dirname(__file__), "monthly_summary_data.xlsx")
    try:
        df = pd.read_excel(excel_path)
        bearish_wicks = df[df["Candle Signal"] == "Bearish Wick"]
        bearish_wick_count = len(bearish_wicks)

        st.subheader(f"Monthly Bearish Wick Candles — Count: {bearish_wick_count}")
        
        if not bearish_wicks.empty:
            st.dataframe(bearish_wicks.reset_index(drop=True))
        else:
            st.info("No rows found where Candle Signal is 'Bearish Wick'.")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")

# Monthly Closes
with tab7:
    st.header("Monthly Close Above/Below")
    st.write("Monthly Close Above Candles minus Monthly Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")
    
    #pdf_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\monthly_close_above_below_count.pdf"
    image_path = os.path.join(os.path.dirname(__file__), "monthly_close_above_below_count.png")

    if os.path.exists(image_path):
        st.image(image_path, width=1500)
    else:
        st.warning("Monthly Close Above Below Count image not found.")

# Upcoming Earnings
with tab8:
    st.header("Upcoming Earnings")
    #file_path = r"C:\Users\jrrub\OneDrive\Desktop\Stock Script Analysis Charts\earnings_calendar.csv"
    file_path = os.path.join(os.path.dirname(__file__), "earnings_calendar.csv")
    df = pd.read_csv(file_path)
    st.dataframe(df, use_container_width=True)

#######################################################################################################################################################################

# Hourly Candles

with tab9:

    # 8:30 Bullish
    st.header("8:30 1hr Bullish Tail Candles")
    file_path = os.path.join(os.path.dirname(__file__), "8_30am_hourly_summary_data.csv")

    try:
        df = pd.read_csv(file_path, parse_dates=["Date"])

        # Check if the first row's Date matches today's date in mm/dd/yyyy format
        first_date = df.loc[0, 'Date'].date()
        today_date = date.today() - timedelta(days=1)
       
        if first_date == today_date:
            bullish_df = df[df['Candle Signal'] == 'Bullish Wick']
            if not bullish_df.empty:
                st.subheader("Bullish Wick Candles — Hourly")
                st.dataframe(bullish_df.reset_index(drop=True), use_container_width=True)
            else:
                st.info("No 'Bullish Wick' signals found for today.")
        else:
            st.warning("There is no data for today yet.")
    except Exception as e:
        st.error(f"Failed to process file: {e}")

    # 8:30 Bearish
    st.header("8:30 1hr Bearish Tail Candles")
    file_path = os.path.join(os.path.dirname(__file__), "8_30am_hourly_summary_data.csv")

    try:
        df = pd.read_csv(file_path, parse_dates=["Date"])

        # Check if the first row's Date matches today's date in mm/dd/yyyy format
        first_date = df.loc[0, 'Date'].date()
        today_date = date.today() - timedelta(days=1)
       
        if first_date == today_date:
            bearish_df = df[df['Candle Signal'] == 'Bearish Wick']
            if not bearish_df.empty:
                st.subheader("Bearish Wick Candles — Hourly")
                st.dataframe(bearish_df.reset_index(drop=True), use_container_width=True)
            else:
                st.info("No 'Bearish Wick' signals found for today.")
        else:
            st.warning("There is no data for today yet.")
    except Exception as e:
        st.error(f"Failed to process file: {e}")

     # 9:30 Bullish
    st.header("9:30 1hr Bullish Tail Candles")
    file_path = os.path.join(os.path.dirname(__file__), "9_30am_hourly_summary_data.csv")

    try:
        df = pd.read_csv(file_path, parse_dates=["Date"])

        # Check if the first row's Date matches today's date in mm/dd/yyyy format
        first_date = df.loc[0, 'Date'].date()
        today_date = date.today() - timedelta(days=1)
       
        if first_date == today_date:
            bullish_df = df[df['Candle Signal'] == 'Bullish Wick']
            if not bullish_df.empty:
                st.subheader("Bullish Wick Candles — Hourly")
                st.dataframe(bullish_df.reset_index(drop=True), use_container_width=True)
            else:
                st.info("No 'Bullish Wick' signals found for today.")
        else:
            st.warning("There is no data for today yet.")
    except Exception as e:
        st.error(f"Failed to process file: {e}")

    # 9:30 Bearish
    st.header("9:30 1hr Bearish Tail Candles")
    file_path = os.path.join(os.path.dirname(__file__), "9_30am_hourly_summary_data.csv")

    try:
        df = pd.read_csv(file_path, parse_dates=["Date"])

        # Check if the first row's Date matches today's date in mm/dd/yyyy format
        first_date = df.loc[0, 'Date'].date()
        today_date = date.today() - timedelta(days=1)
       
        if first_date == today_date:
            bearish_df = df[df['Candle Signal'] == 'Bearish Wick']
            if not bearish_df.empty:
                st.subheader("Bearish Wick Candles — Hourly")
                st.dataframe(bearish_df.reset_index(drop=True), use_container_width=True)
            else:
                st.info("No 'Bearish Wick' signals found for today.")
        else:
            st.warning("There is no data for today yet.")
    except Exception as e:
        st.error(f"Failed to process file: {e}")

