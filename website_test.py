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

# Inject light gray theme and compact table style with markdown
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

    /* Compact table style for all tables */
    div[data-testid="stDataFrame"] table {
        font-size: 0.85em !important;
    }
    div[data-testid="stDataFrame"] th, 
    div[data-testid="stDataFrame"] td {
        padding: 2px 4px !important;
        word-break: break-word;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Stock Market Dashboard")

# Password protection for viewership
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == "Hockey1996$":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        if "password" in st.session_state and not st.session_state["password_correct"]:
            st.error("Password incorrect")
        st.stop()

check_password()


def find_matching_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized_map = {
        str(col).strip().lower().replace(" ", "").replace("_", ""): col
        for col in df.columns
    }
    for candidate in candidates:
        key = candidate.strip().lower().replace(" ", "").replace("_", "")
        if key in normalized_map:
            return normalized_map[key]
    return None

####################################################################################################################################################################

# Tabs
tab0, tab1, tab_spy_vix, tab_spy_day_of_week, tab_ytd, tab_fed_funds_spy, tab_mercury, tab2, tab3, tab8, tab9, tab10, tab11 = st.tabs([
                                                          "Mindset", "Seasonality", "SPY/VIX Analysis", "SPY Day of Week", "YTD Analysis", "Fed Funds Rate - SPY", "Mercury Retrograde Analysis", "Tail Candles (D-W-M)", "Close Above/Below (D-W-M)",
                                                          "Upcoming Earnings", "20/50ma Crossover", 
                                                          "NAAIM Data", "Notes"])

###############################################################################################################################################################

# Mindset
with tab0:
    st.header("Psychology")
    st.write("Psychology is the most important aspect of trading")
    st.write(" ")
    st.write("Mind like a quarterback.")
    st.write("Tom Brady either throws the ball in a safe place for the receiver to catch or he throws it away. No home runs. He is happy with a short gain consistently.")
    st.write(" ")
    st.write("Remember that this trading account is my entire future. Smart trades at the right time will compound into a fortune. Dumb trades at the wrong time will compound into a disaster.")
    st.write("Most days I will be best off by just watching charts and doing nothing.")
    st.write(" ")
    st.write("Being in a trade is one of the toughest places to be in because rational thinking goes away.")
    st.write("What ive noticed is by being very-very patient, I am able to identify the best possible trade entries and get out quickly. Not being in a position gave me that ability to read markets correctly.")
    st.write(" ")
    st.write("Try to not hold over the weekend - Dont trade Friday unless there is a quick day trade.")
    st.write("My mind will be too focussed on news and Bitcoin over the weekend if I enter a position on friday.")
    st.write("Not to mention the 3 days you lose out on theta.")
    st.write(" ")
    st.write("The hardest thing is not trading at all. Most of the time staying away is the best decision.")
    st.write(" ")
    st.write("Its not about finding the perfect trade that will double your money. Its about finding opportunities where reward outweighs the risk and taking a shot.")
###############################################################################################################################################################

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

    # VIX Seasonality (moved from its own tab)
    st.subheader("VIX Seasonality")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    pattern = os.path.join(base_dir, "VIX_seasonality_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("VIX seasonality image not found.")

###############################################################################################################################################################

# Tail Candles (Daily/Weekly/Monthly)
with tab2:
    st.header("Tail Candles (D-W-M)")
    st.write("Daily Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "daily_tail_candle_count" and ending in .png
    pattern = os.path.join(base_dir, "daily_tail_candle_count_*.png")
    matching_files = [
        path for path in glob.glob(pattern)
        if "daily_tail_candle_count_separate_" not in os.path.basename(path)
    ]

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Daily Tail Candle Count image not found.")

    st.subheader("Daily Tail Candle Counts (Separate)")
    separate_pattern = os.path.join(base_dir, "daily_tail_candle_count_separate_*.png")
    separate_matches = glob.glob(separate_pattern)

    if separate_matches:
        latest_separate_file = max(separate_matches, key=os.path.getmtime)
        st.image(latest_separate_file, width=1500)
    else:
        st.warning("Daily Tail Candle Count (Separate) image not found.")

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

    st.divider()
    st.subheader("Weekly Tail Candles")
    st.write("Weekly Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    pattern = os.path.join(base_dir, "weekly_tail_candle_count_*.png")
    matching_files = [
        path for path in glob.glob(pattern)
        if "weekly_tail_candle_count_separate_" not in os.path.basename(path)
    ]

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Weekly Tail Candle Count image not found.")

    st.subheader("Weekly Tail Candle Counts (Separate)")
    separate_pattern = os.path.join(base_dir, "weekly_tail_candle_count_separate_*.png")
    separate_matches = glob.glob(separate_pattern)

    if separate_matches:
        latest_separate_file = max(separate_matches, key=os.path.getmtime)
        st.image(latest_separate_file, width=1500)
    else:
        st.warning("Weekly Tail Candle Count (Separate) image not found.")

    pattern = os.path.join(base_dir, "weekly_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)

        try:
            df = pd.read_excel(latest_file)

            bullish_wicks = df[df["Candle Signal"] == "Bullish Wick"]
            bullish_wick_count = len(bullish_wicks)

            st.subheader(f"Weekly Bullish Wick Candles — Count: {bullish_wick_count}")

            if not bullish_wicks.empty:
                st.dataframe(bullish_wicks.reset_index(drop=True))
            else:
                st.info("No rows found where Candle Signal is 'Bullish Wick'.")
        except Exception as e:
            st.error(f"⚠️ Failed to load XLSX file: {e}")
    else:
        st.warning("Weekly Summary Data file not found.")

    pattern = os.path.join(base_dir, "weekly_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)

        try:
            df = pd.read_excel(latest_file)

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

    st.divider()
    st.subheader("Monthly Tail Candles")
    st.write("Monthly Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    pattern = os.path.join(base_dir, "monthly_tail_candle_count_*.png")
    matching_files = [
        path for path in glob.glob(pattern)
        if "monthly_tail_candle_count_separate_" not in os.path.basename(path)
    ]

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Monthly Tail Candle Count image not found.")

    st.subheader("Monthly Tail Candle Counts (Separate)")
    separate_pattern = os.path.join(base_dir, "monthly_tail_candle_count_separate_*.png")
    separate_matches = glob.glob(separate_pattern)

    if separate_matches:
        latest_separate_file = max(separate_matches, key=os.path.getmtime)
        st.image(latest_separate_file, width=1500)
    else:
        st.warning("Monthly Tail Candle Count (Separate) image not found.")

    pattern = os.path.join(base_dir, "monthly_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)

        try:
            df = pd.read_excel(latest_file)

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

    pattern = os.path.join(base_dir, "monthly_summary_data_*.xlsx")
    matching_files = glob.glob(pattern)

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)

        try:
            df = pd.read_excel(latest_file)

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

###############################################################################################################################################################

# Close Above/Below (Daily/Weekly/Monthly)
with tab3:
    st.header("Close Above/Below (D-W-M)")
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

    st.divider()
    st.subheader("Weekly Close Above/Below")
    st.write("Weekly Close Above Candles minus Weekly Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    pattern = os.path.join(base_dir, "weekly_close_above_below_count_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Weekly Close Above Below Count image not found.")

    st.divider()
    st.subheader("Monthly Close Above/Below")
    st.write("Monthly Close Above Candles minus Monthly Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    pattern = os.path.join(base_dir, "monthly_close_above_below_count_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("Monthly Close Above Below Count image not found.")

###############################################################################################################################################################

# Upcoming Earnings
with tab8:
    st.header("Upcoming Earnings")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Display latest earnings calendar graph
    graph_pattern = os.path.join(base_dir, "earnings_calendar_*_graph.png")
    graph_files = glob.glob(graph_pattern)

    if graph_files:
        latest_graph = max(graph_files, key=os.path.getmtime)
        st.image(latest_graph, use_container_width=True)
    else:
        st.warning("earnings calendar graph image not found.")

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

###############################################################################################################################################################

# 20/50ma Crossover
with tab9:
    st.header("20/50ma Crossover")
    st.write("SPY daily candlestick pages with MA 20/50 crossover zones and summary stats.")
    st.write("Green Zones show where the 20MA flips above the 50MA. Red Zones show where the 20MA flips below the 50MA.")
    st.write("This chart shows that when a 20/50ma crossover, the odds of price action to a certain direction increases.")
    st.write("This should help me in my short term trading by knowing what price should do.")
    st.write("The price action following a 20/50ma crossover is not guaranteed but the odds increase for a certain direction.")
    st.write("The zones were calculated by looking for the maximum price gain or decline within the zone. This simply gives an idea to what direction price should be heading short term.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "spy_daily_data" and ending in "_graph.png"
    pattern = os.path.join(base_dir, "spy_daily_data_*_page_*_graph.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Pick the latest date-run by using the newest modified file, then matching its date prefix
        latest_file = max(matching_files, key=os.path.getmtime)
        latest_name = os.path.basename(latest_file)
        latest_prefix = latest_name.split("_page_")[0]

        latest_run_pages = [
            file_path for file_path in matching_files
            if os.path.basename(file_path).startswith(latest_prefix + "_page_")
        ]

        def extract_page_number(path: str) -> int:
            name = os.path.basename(path)
            try:
                return int(name.split("_page_")[1].split("_graph.png")[0])
            except Exception:
                return 999999

        latest_run_pages = sorted(latest_run_pages, key=extract_page_number, reverse=True)
        st.image(latest_run_pages, use_container_width=True)
    else:
        st.warning("20/50ma crossover graph images not found.")

###############################################################################################################################################################

# NAAIM Data
with tab10:
    st.header("NAAIM Data")
    st.write("Above 90 seems to be an area where you should start to see a stock market pullback/selloff. Below 40 seems to be an area where you should start to see a stock market rally.")
    
    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Search for files starting with "naaim_plot" and ending in .png
    pattern = os.path.join(base_dir, "naaim_plot_*.png")
    matching_files = glob.glob(pattern)

    if matching_files:
        # Grab the most recently modified one
        latest_file = max(matching_files, key=os.path.getmtime)
        st.image(latest_file, width=1500)
    else:
        st.warning("NAAIM Plot image not found.")

    st.subheader("NAAIM + SPY Overlay")

    combined_pattern = os.path.join(base_dir, "naaim_spy_combined_*_graph.png")
    combined_files = glob.glob(combined_pattern)

    if combined_files:
        latest_combined = max(combined_files, key=os.path.getmtime)
        st.image(latest_combined, width=1500)
    else:
        st.warning("NAAIM + SPY combined graph image not found.")

# Notes
with tab11:
    st.write("Trading Psychology:")
    st.write("FOMO:")
    st.write("Afraid of watching the market move in a direction without me.")
    st.write("Causes me to take stupid trades at the worst time because I’m afraid to watch the market keep moving while I’m on the sidelines.")
    st.write("What I need to realize is that if I’m putting the time into reading charts consistently, then I will find unlimited trades.")
    st.write("It is better for me to sit on the sidelines and wait for the charts to show a high reward/risk ratio setup than to force something just because I want action.") 
    st.write("When I am patient for my trades, I will make plenty of money.")
    st.write("Remember that my goal is to make 20% per week and compound that over time. This is ambitious but is totally doable if I am patient and am watching chart consistently.")
    st.write("Be GRATEFULL. Dont get all emotional and upset for missing a trade or taking a small loss. There is a new trade always. I am very lucky to be in the position I am in.")
    st.write("Just be patient and keep reading charts. The success will come.")
    st.write("Check intraday price changes. How do the top % gainers look and how do the bottom % losers look? That will determine market direction.")
    st.write("Seeing the losers show bottoming tails is bullish. Seeing the winners show topping tails is bearish. Are the losers at support?")

#######################################################################################################################################################################

# SPY/VIX Analysis
with tab_spy_vix:
    st.header("SPY/VIX Analysis")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    (
        svix_tab1, svix_tab2, svix_tab3, svix_tab4, svix_tab5, svix_tab6
    ) = st.tabs([
        "VIX Daily Returns & % Positive Rate",
        "SPY Daily Returns & % Positive Rate",
        "SPY Last 10 Weeks",
        "VIX Avg Price & STD Dev Bands",
        "SPY Candles with UVXY+SPY Positive Dates",
        "SPY Candles with VIX+SPY Positive Dates",
    ])

    with svix_tab1:
        vix_weekday_matches = glob.glob(os.path.join(base_dir, "vix_weekday_*_graph.png"))
        if vix_weekday_matches:
            latest_vix_weekday = max(vix_weekday_matches, key=os.path.getmtime)
            st.image(latest_vix_weekday, use_container_width=True)
        else:
            st.warning("VIX Weekday Returns & Hit Rate image not found.")

    with svix_tab2:
        spy_weekday_matches = glob.glob(os.path.join(base_dir, "spy_weekday_*_graph.png"))
        if spy_weekday_matches:
            latest_spy_weekday = max(spy_weekday_matches, key=os.path.getmtime)
            st.image(latest_spy_weekday, use_container_width=True)
        else:
            st.warning("SPY Daily Returns & % Positive Rate image not found.")

    with svix_tab3:
        spy_10wk_matches = glob.glob(os.path.join(base_dir, "spy_last_10_weeks_*_graph.png"))
        if spy_10wk_matches:
            latest_spy_10wk = max(spy_10wk_matches, key=os.path.getmtime)
            st.image(latest_spy_10wk, use_container_width=True)
        else:
            st.warning("SPY Last 10 Weeks image not found.")

    with svix_tab4:
        matches = glob.glob(os.path.join(base_dir, "vix_analysis_*_graph.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=1200)
        else:
            st.warning("VIX Avg Price & STD Dev Bands image not found.")

    with svix_tab5:
        matches = glob.glob(os.path.join(base_dir, "spy_uvxy_positive_*_graph.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=1200)
        else:
            st.warning("SPY Candles with UVXY+SPY Positive Dates image not found.")

    with svix_tab6:
        matches = glob.glob(os.path.join(base_dir, "spy_vix_positive_*_graph.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=1200)
        else:
            st.warning("SPY Candles with VIX+SPY Positive Dates image not found.")

#######################################################################################################################################################################

# SPY Day of Week
with tab_spy_day_of_week:
    st.header("SPY Day of Week")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    st.subheader("Daily SPY Gain Chart")
    gain_chart_path = os.path.join(base_dir, "Daily_SPY_Gain_Chart.png")
    if os.path.exists(gain_chart_path):
        st.image(gain_chart_path, use_container_width=True)
    else:
        st.warning("Daily SPY Gain Chart image not found.")

    st.subheader("SPY Daily Positive Count Ghart")
    positive_count_path = os.path.join(base_dir, "SPY_Daily_Positive_Count_Ghart.png")
    if os.path.exists(positive_count_path):
        st.image(positive_count_path, use_container_width=True)
    else:
        st.warning("SPY Daily Positive Count Ghart image not found.")

#######################################################################################################################################################################

# YTD Analysis
with tab_ytd:
    st.header("YTD Analysis")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")
    sector_matches = glob.glob(os.path.join(base_dir, "ytd_analysis_*.xlsx"))
    all_stocks_matches = glob.glob(os.path.join(base_dir, "all_stocks_ytd_analysis_*.xlsx"))

    st.markdown(
        """
        <style>
        div[data-testid="stDataFrame"] div[role="columnheader"] {
            text-align: center !important;
            justify-content: center !important;
            font-size: 0.82rem !important;
        }
        div[data-testid="stDataFrame"] div[role="gridcell"] {
            text-align: center !important;
            justify-content: center !important;
            font-size: 0.82rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    row_height = 24
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Sector ETFs")
        if sector_matches:
            latest_sector_file = max(sector_matches, key=os.path.getmtime)
            try:
                sector_df = pd.read_excel(latest_sector_file)
                sector_table_height = min(900, max(360, row_height * (len(sector_df) + 1) + 12))
                st.dataframe(
                    sector_df,
                    use_container_width=True,
                    height=sector_table_height,
                    hide_index=True,
                    row_height=row_height,
                )
            except Exception as e:
                st.error(f"⚠️ Failed to load sector ETF XLSX file: {e}")
        else:
            st.warning("Sector ETF YTD analysis file not found.")

    with right_col:
        st.subheader("All Stocks")
        if all_stocks_matches:
            latest_all_stocks_file = max(all_stocks_matches, key=os.path.getmtime)
            try:
                all_stocks_df = pd.read_excel(latest_all_stocks_file)

                sector_col = find_matching_column(all_stocks_df, ["Sector"])
                industry_col = find_matching_column(all_stocks_df, ["Industry"])
                filtered_df = all_stocks_df.copy()

                if sector_col or industry_col:
                    filter_container = getattr(st, "popover", None)
                    if callable(filter_container):
                        filter_context = filter_container("🔎 Filter Table")
                    else:
                        filter_context = st.expander("🔎 Filter Table", expanded=False)

                    with filter_context:
                        selected_sectors = []
                        selected_industries = []
                        filter_col1, filter_col2 = st.columns(2)

                        if sector_col:
                            sector_options = sorted(
                                value for value in all_stocks_df[sector_col].dropna().astype(str).unique() if value.strip()
                            )
                            selected_sectors = filter_col1.multiselect(
                                "Sector",
                                sector_options,
                                key="ytd_all_stocks_sector_filter",
                            )
                            if selected_sectors:
                                filtered_df = filtered_df[filtered_df[sector_col].astype(str).isin(selected_sectors)]
                        else:
                            filter_col1.caption("No `Sector` column found")

                        if industry_col:
                            industry_source_df = filtered_df if sector_col and selected_sectors else all_stocks_df
                            industry_options = sorted(
                                value for value in industry_source_df[industry_col].dropna().astype(str).unique() if value.strip()
                            )
                            selected_industries = filter_col2.multiselect(
                                "Industry",
                                industry_options,
                                key="ytd_all_stocks_industry_filter",
                            )
                            if selected_industries:
                                filtered_df = filtered_df[filtered_df[industry_col].astype(str).isin(selected_industries)]
                        else:
                            filter_col2.caption("No `Industry` column found")

                    st.caption(f"Showing {len(filtered_df):,} of {len(all_stocks_df):,} rows")
                else:
                    st.caption("No `Sector` or `Industry` columns were found in this file.")

                all_stocks_table_height = min(900, max(360, row_height * (len(filtered_df) + 1) + 12))
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    height=all_stocks_table_height,
                    hide_index=True,
                    row_height=row_height,
                )
            except Exception as e:
                st.error(f"⚠️ Failed to load all-stocks XLSX file: {e}")
        else:
            st.warning("All stocks YTD analysis file not found.")

#######################################################################################################################################################################

# Fed Funds Rate - SPY
with tab_fed_funds_spy:
    st.header("Fed Funds Rate - SPY")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")
    fed_page_matches = glob.glob(os.path.join(base_dir, "fed_rates_spy_page_*_graph.png"))

    if fed_page_matches:
        def extract_fed_page_number(path: str) -> int:
            name = os.path.basename(path)
            try:
                return int(name.split("_page_")[1].split("_")[0])
            except Exception:
                return -1

        ordered_pages = sorted(fed_page_matches, key=extract_fed_page_number, reverse=True)
        st.image(ordered_pages, use_container_width=True)
    else:
        st.warning("Fed Funds Rate - SPY graph images not found.")

#######################################################################################################################################################################

# Mercury Retrograde Analysis
with tab_mercury:
    st.header("Mercury Retrograde Analysis")

    base_dir = os.path.join(os.path.dirname(__file__), "uploads")

    # Summary page first
    summary_matches = glob.glob(os.path.join(base_dir, "mercury_retrograde_summary_*_graph.png"))
    if summary_matches:
        latest_summary = max(summary_matches, key=os.path.getmtime)
        st.subheader("Summary Stats")
        summary_col, _ = st.columns(2)
        with summary_col:
            st.image(latest_summary, use_container_width=True)
    else:
        st.warning("Mercury retrograde summary image not found.")

    # Then show SPY pages in reverse order (e.g., 7 -> 1)
    page_matches = glob.glob(os.path.join(base_dir, "mercury_retrograde_spy_page_*_graph.png"))
    if page_matches:
        def extract_page_number(path: str) -> int:
            name = os.path.basename(path)
            try:
                return int(name.split("_page_")[1].split("_")[0])
            except Exception:
                return -1

        ordered_pages = sorted(page_matches, key=extract_page_number, reverse=True)
        st.subheader("SPY Candlestick Pages (Newest Page Number First)")
        st.image(ordered_pages, use_container_width=True)
    else:
        st.warning("Mercury retrograde SPY page images not found.")

    
             


#######################################################################################################################################################################




