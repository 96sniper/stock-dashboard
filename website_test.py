import streamlit as st
import streamlit.components.v1 as components
import base64
import pandas as pd
import os
from datetime import date, timedelta
import glob
import re

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


def _directory_asset_score(path: str) -> int:
    return (
        len(glob.glob(os.path.join(path, "*.png")))
        + len(glob.glob(os.path.join(path, "*.xlsx")))
    )


def resolve_data_dir() -> str:
    script_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(script_dir)
    candidates = [
        os.path.join(script_dir, "uploads"),
        os.path.join(script_dir, "uplaods"),
        os.path.join(script_dir, "stock-dashboard", "uploads"),
        os.path.join(parent_dir, "uploads"),
        os.path.join(parent_dir, "stock-dashboard", "uploads"),
    ]
    existing = [path for path in candidates if os.path.isdir(path)]
    if existing:
        return max(existing, key=_directory_asset_score)
    return script_dir


def is_valid_png(file_path: str) -> bool:
    try:
        if os.path.getsize(file_path) <= 8:
            return False
        with open(file_path, "rb") as image_file:
            return image_file.read(8) == b"\x89PNG\r\n\x1a\n"
    except OSError:
        return False


def latest_valid_png(pattern: str, exclude_substring: str | None = None) -> str | None:
    matches = glob.glob(pattern)
    if exclude_substring:
        matches = [path for path in matches if exclude_substring not in os.path.basename(path)]
    valid_matches = [path for path in matches if is_valid_png(path)]
    if valid_matches:
        return max(valid_matches, key=os.path.getmtime)
    return None


def render_bull_pct_donut(df: pd.DataFrame) -> None:
    def polar_to_cartesian(center_x: float, center_y: float, radius: float, angle_in_degrees: float) -> tuple[float, float]:
        angle_in_radians = (angle_in_degrees - 90.0) * 3.141592653589793 / 180.0
        return (
            center_x + radius * float(__import__("math").cos(angle_in_radians)),
            center_y + radius * float(__import__("math").sin(angle_in_radians)),
        )

    def describe_arc(center_x: float, center_y: float, radius: float, start_angle: float, end_angle: float) -> str:
        start_x, start_y = polar_to_cartesian(center_x, center_y, radius, end_angle)
        end_x, end_y = polar_to_cartesian(center_x, center_y, radius, start_angle)
        large_arc_flag = "1" if end_angle - start_angle > 180 else "0"
        return (
            f"M {center_x} {center_y} "
            f"L {start_x:.2f} {start_y:.2f} "
            f"A {radius} {radius} 0 {large_arc_flag} 0 {end_x:.2f} {end_y:.2f} "
            "Z"
        )

    bull_pct_column = None
    for column in df.columns:
        normalized = str(column).strip().upper().replace(" ", "_")
        if normalized == "BULL_PCT":
            bull_pct_column = column
            break

    if bull_pct_column is None:
        return

    numeric_values = pd.to_numeric(df[bull_pct_column], errors="coerce").dropna().round(2)
    if numeric_values.empty:
        return

    target_values = [0.0, 33.33, 66.67, 100.0]
    counts = [
        int(((numeric_values == 0.0) | (numeric_values == 0)).sum()) if target_values[0] == 0.0 else 0,
        int(((numeric_values >= 32.99) & (numeric_values <= 33.67)).sum()) if target_values[1] == 33.33 else 0,
        int(((numeric_values >= 66.0) & (numeric_values <= 67.34)).sum()) if target_values[2] == 66.67 else 0,
        int(((numeric_values == 100.0) | (numeric_values == 100)).sum()) if target_values[3] == 100.0 else 0,
    ]
    if sum(counts) == 0:
        return

    colors = ["#F04444", "#FFFFFF", "#FFFFFF", "#2ECC71"]
    labels = ["0", "33.33", "66.67", "100"]

    total = sum(counts)
    center_x = 90.0
    center_y = 90.0
    radius = 72.0
    stroke_width = 28.0
    current_angle = 0.0
    svg_paths = []

    for count, color in zip(counts, colors):
        if count <= 0:
            continue
        sweep_angle = 360.0 * (count / total)
        start_angle = current_angle
        end_angle = current_angle + sweep_angle
        
        # Handle full 360° arc by splitting into two 180° arcs
        if sweep_angle >= 359.99:
            path1 = describe_arc(center_x, center_y, radius, start_angle, start_angle + 180.0)
            path2 = describe_arc(center_x, center_y, radius, start_angle + 180.0, start_angle + 360.0)
            svg_paths.append(f'<path d="{path1}" fill="{color}" stroke="#666666" stroke-width="1.5" />')
            svg_paths.append(f'<path d="{path2}" fill="{color}" stroke="#666666" stroke-width="1.5" />')
        else:
            path = describe_arc(center_x, center_y, radius, start_angle, end_angle)
            svg_paths.append(
                f'<path d="{path}" fill="{color}" stroke="#666666" stroke-width="1.5" />'
            )
        current_angle = end_angle

    legend_text = " | ".join(f"{label}: {count}" for label, count in zip(labels, counts))
    svg = f'''
    <div style="display:flex; justify-content:center; margin:0.35rem 0 0.75rem 0;">
      <svg width="220" height="220" viewBox="0 0 180 180" role="img" aria-label="BULL_PCT donut chart">
        <circle cx="90" cy="90" r="{radius}" fill="#FFFFFF" stroke="#D0D0D0" stroke-width="1" />
        {''.join(svg_paths)}
        <circle cx="90" cy="90" r="{radius - stroke_width}" fill="#FFFFFF" stroke="#D0D0D0" stroke-width="1" />
        <text x="90" y="86" text-anchor="middle" font-size="12" font-weight="700" fill="#111111">BULL_PCT</text>
        <text x="90" y="104" text-anchor="middle" font-size="10" fill="#444444">{total} rows</text>
      </svg>
    </div>
    <div style="text-align:center; font-size:0.8rem; color:#444444; margin-top:-0.35rem; margin-bottom:0.75rem;">
      {legend_text}
    </div>
    '''

    components.html(svg, height=320, scrolling=False)


def render_trend_pie_charts(df: pd.DataFrame) -> None:
    """Render pie charts for DAILY, WEEKLY, and MONTHLY BULL vs BEAR counts."""
    def polar_to_cartesian(center_x: float, center_y: float, radius: float, angle_in_degrees: float) -> tuple[float, float]:
        angle_in_radians = (angle_in_degrees - 90.0) * 3.141592653589793 / 180.0
        return (
            center_x + radius * float(__import__("math").cos(angle_in_radians)),
            center_y + radius * float(__import__("math").sin(angle_in_radians)),
        )

    def describe_arc(center_x: float, center_y: float, radius: float, start_angle: float, end_angle: float) -> str:
        start_x, start_y = polar_to_cartesian(center_x, center_y, radius, end_angle)
        end_x, end_y = polar_to_cartesian(center_x, center_y, radius, start_angle)
        large_arc_flag = "1" if end_angle - start_angle > 180 else "0"
        return (
            f"M {center_x} {center_y} "
            f"L {start_x:.2f} {start_y:.2f} "
            f"A {radius} {radius} 0 {large_arc_flag} 0 {end_x:.2f} {end_y:.2f} "
            "Z"
        )

    def create_pie_svg(bull_count: int, bear_count: int, title: str) -> str:
        total = bull_count + bear_count
        if total == 0:
            return f'<div style="text-align:center;"><p>{title}: No data</p></div>'

        bull_percentage = (bull_count / total) * 100
        bear_percentage = (bear_count / total) * 100

        center_x = 90.0
        center_y = 90.0
        radius = 65.0
        current_angle = 0.0
        svg_paths = []

        # Red arc for BEAR
        if bear_count > 0:
            sweep_angle = 360.0 * (bear_count / total)
            start_angle = current_angle
            end_angle = current_angle + sweep_angle
            if sweep_angle >= 359.99:
                path1 = describe_arc(center_x, center_y, radius, start_angle, start_angle + 180.0)
                path2 = describe_arc(center_x, center_y, radius, start_angle + 180.0, start_angle + 360.0)
                svg_paths.append(f'<path d="{path1}" fill="#E74C3C" stroke="#FFFFFF" stroke-width="2" />')
                svg_paths.append(f'<path d="{path2}" fill="#E74C3C" stroke="#FFFFFF" stroke-width="2" />')
            else:
                path = describe_arc(center_x, center_y, radius, start_angle, end_angle)
                svg_paths.append(f'<path d="{path}" fill="#E74C3C" stroke="#FFFFFF" stroke-width="2" />')
            current_angle = end_angle

        # Green arc for BULL
        if bull_count > 0:
            sweep_angle = 360.0 * (bull_count / total)
            start_angle = current_angle
            end_angle = current_angle + sweep_angle
            if sweep_angle >= 359.99:
                path1 = describe_arc(center_x, center_y, radius, start_angle, start_angle + 180.0)
                path2 = describe_arc(center_x, center_y, radius, start_angle + 180.0, start_angle + 360.0)
                svg_paths.append(f'<path d="{path1}" fill="#27AE60" stroke="#FFFFFF" stroke-width="2" />')
                svg_paths.append(f'<path d="{path2}" fill="#27AE60" stroke="#FFFFFF" stroke-width="2" />')
            else:
                path = describe_arc(center_x, center_y, radius, start_angle, end_angle)
                svg_paths.append(f'<path d="{path}" fill="#27AE60" stroke="#FFFFFF" stroke-width="2" />')

        svg = f'''
        <div style="display:flex; flex-direction:column; align-items:center; margin:0.5rem 0;">
          <svg width="180" height="180" viewBox="0 0 180 180" role="img" aria-label="{title} pie chart">
            {''.join(svg_paths)}
            <text x="90" y="92" text-anchor="middle" font-size="11" font-weight="700" fill="#111111">{title}</text>
          </svg>
          <div style="text-align:center; font-size:0.75rem; color:#444444; margin-top:0.35rem;">
            <span style="color:#27AE60; font-weight:bold;">BULL: {bull_count}</span> | <span style="color:#E74C3C; font-weight:bold;">BEAR: {bear_count}</span>
          </div>
        </div>
        '''
        return svg

    timeframe_columns = [
        ('DAILY_CURRENT_TREND', 'DAILY'),
        ('WEEKLY_CURRENT_TREND', 'WEEKLY'),
        ('MONTHLY_CURRENT_TREND', 'MONTHLY'),
    ]

    pie_charts_html = '<div style="display:flex; justify-content:center; gap:1.5rem; margin:1rem 0; flex-wrap:wrap;">'
    
    for col_name, display_name in timeframe_columns:
        trend_column = None
        for column in df.columns:
            normalized = str(column).strip().upper().replace(" ", "_")
            if normalized == col_name:
                trend_column = column
                break

        if trend_column is None:
            continue

        trend_values = df[trend_column].dropna()
        bull_count = int((trend_values.str.upper() == 'BULL').sum())
        bear_count = int((trend_values.str.upper() == 'BEAR').sum())

        pie_charts_html += create_pie_svg(bull_count, bear_count, display_name)

    pie_charts_html += '</div>'
    components.html(pie_charts_html, height=360, scrolling=False)


def get_bull_minus_bear_score_from_xlsx(xlsx_path: str | None) -> int:
    if not xlsx_path:
        return -10**9

    try:
        df = pd.read_excel(xlsx_path)
    except Exception:
        return -10**9

    bull_pct_column = None
    for column in df.columns:
        normalized = str(column).strip().upper().replace(" ", "_")
        if normalized == "BULL_PCT":
            bull_pct_column = column
            break

    if bull_pct_column is None:
        return -10**9

    numeric_values = pd.to_numeric(df[bull_pct_column], errors="coerce").dropna().round(2)
    if numeric_values.empty:
        return -10**9

    green_count = int((numeric_values == 100.0).sum())
    red_count = int((numeric_values == 0.0).sum())
    return green_count - red_count


def get_latest_sector_xlsx(base_dir: str, sector_name: str) -> str | None:
    def build_sector_variants(name: str) -> set[str]:
        space_name = name.replace("_", " ")
        underscore_name = name.replace(" ", "_")
        return {
            name,
            space_name,
            underscore_name,
            space_name.title(),
            underscore_name.title(),
            space_name.upper(),
            underscore_name.upper(),
            space_name.lower(),
            underscore_name.lower(),
        }

    xlsx_matches = []
    for sector_variant in build_sector_variants(sector_name):
        xlsx_matches.extend(
            glob.glob(
                os.path.join(
                    base_dir,
                    f"CURRENT_TREND_SUMMARY_ALL_STOCKS_{sector_variant}_*.xlsx",
                )
            )
        )
    xlsx_matches = list(set(xlsx_matches))
    if not xlsx_matches:
        return None
    return max(xlsx_matches, key=os.path.getmtime)


def discover_industry_tokens(base_dir: str) -> list[str]:
    tokens: set[str] = set()
    xlsx_pattern = re.compile(
        r"^CURRENT_TREND_SUMMARY_ALL_STOCKS_INDUSTRIES_(.+)_(\d{2}_\d{2}_\d{4}|\d{4}-\d{2}-\d{2})\.xlsx$"
    )
    png_pattern = re.compile(
        r"^CURRENT_TREND_SUMMARY_TABLE_ALL_STOCKS_INDUSTRIES_(.+)_(\d{2}_\d{2}_\d{4}|\d{4}-\d{2}-\d{2})\.png$"
    )

    for path in glob.glob(os.path.join(base_dir, "CURRENT_TREND_SUMMARY_ALL_STOCKS_INDUSTRIES_*.xlsx")):
        match = xlsx_pattern.match(os.path.basename(path))
        if match:
            tokens.add(match.group(1))

    for path in glob.glob(os.path.join(base_dir, "CURRENT_TREND_SUMMARY_TABLE_ALL_STOCKS_INDUSTRIES_*.png")):
        match = png_pattern.match(os.path.basename(path))
        if match:
            tokens.add(match.group(1))

    return sorted(tokens)


def industry_label_from_token(token: str) -> str:
    return token.replace("_", " ").title()


def get_latest_industry_xlsx(base_dir: str, industry_token: str) -> str | None:
    matches = glob.glob(
        os.path.join(base_dir, f"CURRENT_TREND_SUMMARY_ALL_STOCKS_INDUSTRIES_{industry_token}_*.xlsx")
    )
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)


def get_latest_industry_png(base_dir: str, industry_token: str) -> str | None:
    matches = glob.glob(
        os.path.join(base_dir, f"CURRENT_TREND_SUMMARY_TABLE_ALL_STOCKS_INDUSTRIES_{industry_token}_*.png")
    )
    valid_matches = [path for path in matches if is_valid_png(path)]
    if not valid_matches:
        return None
    return max(valid_matches, key=os.path.getmtime)


DATA_DIR = resolve_data_dir()

####################################################################################################################################################################

# Tabs
tab0, tab1, tab_sector_analysis, tab_spy_vix, tab_spy_analysis, tab_ytd, tab_fed_funds_spy, tab_mercury, tab2, tab3, tab3b, tab_sector_summary, tab_industry_summary, tab8, tab9, tab10, tab11 = st.tabs([
                                                          "Mindset", "Seasonality", "Sector Analysis", "SPY/VIX Analysis", "SPY Analysis", "YTD Analysis", "Fed Funds Rate - SPY", "Mercury Retrograde Analysis", "Tail Candles (D-W-M)", "Close Above/Below Tickers", "Close Above/Below Summary", "Close Above/Below Sector Summary", "Close Above/Below Industry Summary",
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
    st.header("Seasonality")

    base_dir = DATA_DIR
    season_tab1, season_tab2, season_tab3, season_tab4 = st.tabs([
        "SPY",
        "QQQ",
        "IWM",
        "VIX",
    ])

    with season_tab1:
        pattern = os.path.join(base_dir, "spy_seasonality_*.png")
        latest_file = latest_valid_png(pattern)
        if latest_file:
            st.image(latest_file, width=1500)
        else:
            st.warning("SPY seasonality image not found.")

    with season_tab2:
        pattern = os.path.join(base_dir, "qqq_seasonality_*.png")
        latest_file = latest_valid_png(pattern)
        if latest_file:
            st.image(latest_file, width=1500)
        else:
            st.warning("QQQ seasonality image not found.")

    with season_tab3:
        pattern = os.path.join(base_dir, "iwm_seasonality_*.png")
        latest_file = latest_valid_png(pattern)
        if latest_file:
            st.image(latest_file, width=1500)
        else:
            st.warning("IWM seasonality image not found.")

    with season_tab4:
        pattern = os.path.join(base_dir, "VIX_seasonality_*.png")
        latest_file = latest_valid_png(pattern)
        if latest_file:
            st.image(latest_file, width=1500)
        else:
            st.warning("VIX seasonality image not found.")

###############################################################################################################################################################

# Sector Analysis
with tab_sector_analysis:
    st.header("Sector Analysis")

    base_dir = DATA_DIR
    sector_chart_width = 1200
    yearly_chart_width = 1600

    def latest_sector_chart(*filename_patterns: str) -> str | None:
        matches: list[str] = []
        for filename_pattern in filename_patterns:
            matches.extend(glob.glob(os.path.join(base_dir, filename_pattern)))
        unique_matches = list(set(matches))
        valid_matches = [path for path in unique_matches if is_valid_png(path)]
        if not valid_matches:
            return None
        return max(valid_matches, key=os.path.getmtime)

    sub_tab_yearly, sub_tab_ytd, sub_tab_qtd = st.tabs(["Yearly Table", "Year-to-Date", "Quarter-to-Date"])

    with sub_tab_yearly:
        latest_file = latest_sector_chart(
            "sector_etf_yearly_gain_table_*.png",
            "sector_etf_yearly_gain_table.png",
        )
        if latest_file:
            st.image(latest_file, width=yearly_chart_width)
        else:
            st.warning("Yearly gain table image not found.")

    with sub_tab_ytd:
        latest_file = latest_sector_chart(
            "etf_ytd_bar_chart_*.png",
            "etf_ytd_bar_chart.png",
        )
        if latest_file:
            st.image(latest_file, width=sector_chart_width)
        else:
            st.warning("YTD bar chart image not found.")

    with sub_tab_qtd:
        latest_file = latest_sector_chart(
            "etf_qtd_bar_chart_*.png",
            "etf_qtd_bar_chart.png",
        )
        if latest_file:
            st.image(latest_file, width=sector_chart_width)
        else:
            st.warning("QTD bar chart image not found.")

###############################################################################################################################################################

# Tail Candles (Daily/Weekly/Monthly)
with tab2:
    st.header("Tail Candles (D-W-M)")
    st.write("Daily Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    base_dir = DATA_DIR

    def show_latest_png(file_pattern: str, not_found_message: str, width: int = 1500, exclude_substring: str | None = None) -> None:
        matches = glob.glob(os.path.join(base_dir, file_pattern))
        if exclude_substring:
            matches = [path for path in matches if exclude_substring not in os.path.basename(path)]

        if matches:
            latest_file = max(matches, key=os.path.getmtime)
            st.image(latest_file, width=width)
        else:
            st.warning(not_found_message)

    def show_wick_table(file_pattern: str, signal: str, heading: str, not_found_message: str) -> None:
        matches = glob.glob(os.path.join(base_dir, file_pattern))
        if matches:
            latest_file = max(matches, key=os.path.getmtime)
            try:
                df = pd.read_excel(latest_file)
                filtered = df[df["Candle Signal"] == signal]
                st.subheader(f"{heading} — Count: {len(filtered)}")
                if not filtered.empty:
                    st.dataframe(filtered.reset_index(drop=True))
                else:
                    st.info(f"No rows found where Candle Signal is '{signal}'.")
            except Exception as e:
                st.error(f"⚠️ Failed to load XLSX file: {e}")
        else:
            st.warning(not_found_message)

    (
        tc_tab1, tc_tab2, tc_tab3, tc_tab4,
        tc_tab5, tc_tab6, tc_tab7, tc_tab8,
        tc_tab9, tc_tab10, tc_tab11, tc_tab12,
    ) = st.tabs([
        "Daily Count",
        "Daily Count (Separate)",
        "Daily Bullish Wick",
        "Daily Bearish Wick",
        "Weekly Count",
        "Weekly Count (Separate)",
        "Weekly Bullish Wick",
        "Weekly Bearish Wick",
        "Monthly Count",
        "Monthly Count (Separate)",
        "Monthly Bullish Wick",
        "Monthly Bearish Wick",
    ])

    with tc_tab1:
        show_latest_png(
            "daily_tail_candle_count_*.png",
            "Daily Tail Candle Count image not found.",
            exclude_substring="daily_tail_candle_count_separate_",
        )

    with tc_tab2:
        show_latest_png(
            "daily_tail_candle_count_separate_*.png",
            "Daily Tail Candle Count (Separate) image not found.",
        )

    with tc_tab3:
        show_wick_table(
            "daily_summary_data_*.xlsx",
            "Bullish Wick",
            "Daily Bullish Wick Candles",
            "Daily Summary Data file not found.",
        )

    with tc_tab4:
        show_wick_table(
            "daily_summary_data_*.xlsx",
            "Bearish Wick",
            "Daily Bearish Wick Candles",
            "Daily Summary Data file not found.",
        )

    with tc_tab5:
        show_latest_png(
            "weekly_tail_candle_count_*.png",
            "Weekly Tail Candle Count image not found.",
            exclude_substring="weekly_tail_candle_count_separate_",
        )

    with tc_tab6:
        show_latest_png(
            "weekly_tail_candle_count_separate_*.png",
            "Weekly Tail Candle Count (Separate) image not found.",
        )

    with tc_tab7:
        show_wick_table(
            "weekly_summary_data_*.xlsx",
            "Bullish Wick",
            "Weekly Bullish Wick Candles",
            "Weekly Summary Data file not found.",
        )

    with tc_tab8:
        show_wick_table(
            "weekly_summary_data_*.xlsx",
            "Bearish Wick",
            "Weekly Bearish Wick Candles",
            "Weekly Summary Data file not found.",
        )

    with tc_tab9:
        show_latest_png(
            "monthly_tail_candle_count_*.png",
            "Monthly Tail Candle Count image not found.",
            exclude_substring="monthly_tail_candle_count_separate_",
        )

    with tc_tab10:
        show_latest_png(
            "monthly_tail_candle_count_separate_*.png",
            "Monthly Tail Candle Count (Separate) image not found.",
        )

    with tc_tab11:
        show_wick_table(
            "monthly_summary_data_*.xlsx",
            "Bullish Wick",
            "Monthly Bullish Wick Candles",
            "Monthly Summary Data file not found.",
        )

    with tc_tab12:
        show_wick_table(
            "monthly_summary_data_*.xlsx",
            "Bearish Wick",
            "Monthly Bearish Wick Candles",
            "Monthly Summary Data file not found.",
        )

###############################################################################################################################################################

# Close Above/Below Summary
with tab3:
    st.header("Close Above/Below Tickers")
    st.write("Daily Close Above Candles minus Daily Close Below Candles. Helps to identify the institutional distribution in stocks and overall trend.")

    base_dir = DATA_DIR
    cab_tab0, cab_tab1, cab_tab2, cab_tab3, cab_tab4, cab_tab5, cab_tab6, cab_tab7, cab_tab8 = st.tabs([
        "Daily",
        "Weekly",
        "Monthly",
        "Daily Close Trend",
        "Weekly Close Trend",
        "Monthly Close Trend",
        "Daily Close Trend - All Stocks",
        "Weekly Close Trend - All Stocks",
        "Monthly Close Trend - All Stocks",
    ])

    with cab_tab0:
        st.subheader("Daily Close Above/Below")
        pattern = os.path.join(base_dir, "daily_close_above_below_count_*.png")
        matching_files = glob.glob(pattern)
        if matching_files:
            latest_file = max(matching_files, key=os.path.getmtime)
            st.image(latest_file, width=1500)
        else:
            st.warning("Daily Close Above Below Count image not found.")

    with cab_tab1:
        st.subheader("Weekly Close Above/Below")
        pattern = os.path.join(base_dir, "weekly_close_above_below_count_*.png")
        matching_files = glob.glob(pattern)
        if matching_files:
            latest_file = max(matching_files, key=os.path.getmtime)
            st.image(latest_file, width=1500)
        else:
            st.warning("Weekly Close Above Below Count image not found.")

    with cab_tab2:
        st.subheader("Monthly Close Above/Below")
        pattern = os.path.join(base_dir, "monthly_close_above_below_count_*.png")
        matching_files = glob.glob(pattern)
        if matching_files:
            latest_file = max(matching_files, key=os.path.getmtime)
            st.image(latest_file, width=1500)
        else:
            st.warning("Monthly Close Above Below Count image not found.")

    with cab_tab3:
        matches = [
            p for p in glob.glob(os.path.join(base_dir, "BULL_Percentage_Trend_Daily_*.png"))
            if "_ALL_STOCKS_" not in os.path.basename(p)
        ]
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=850)
        else:
            st.warning("Daily Close Trend image not found.")

    with cab_tab4:
        matches = [
            p for p in glob.glob(os.path.join(base_dir, "BULL_Percentage_Trend_Weekly_*.png"))
            if "_ALL_STOCKS_" not in os.path.basename(p)
        ]
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=850)
        else:
            st.warning("Weekly Close Trend image not found.")

    with cab_tab5:
        matches = [
            p for p in glob.glob(os.path.join(base_dir, "BULL_Percentage_Trend_Monthly_*.png"))
            if "_ALL_STOCKS_" not in os.path.basename(p)
        ]
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=850)
        else:
            st.warning("Monthly Close Trend image not found.")

    with cab_tab6:
        matches = glob.glob(os.path.join(base_dir, "BULL_Percentage_Trend_Daily_ALL_STOCKS_*.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=850)
        else:
            st.warning("Daily Close Trend - All Stocks image not found.")

    with cab_tab7:
        matches = glob.glob(os.path.join(base_dir, "BULL_Percentage_Trend_Weekly_ALL_STOCKS_*.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=850)
        else:
            st.warning("Weekly Close Trend - All Stocks image not found.")

    with cab_tab8:
        matches = glob.glob(os.path.join(base_dir, "BULL_Percentage_Trend_Monthly_ALL_STOCKS_*.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=850)
        else:
            st.warning("Monthly Close Trend - All Stocks image not found.")

###############################################################################################################################################################

# Close Above/Below Summary
with tab3b:
    st.header("Close Above/Below Summary")
    st.write("Current trend summary tables and percentage trend analysis for ETFs/indices and the all-stocks universe.")

    base_dir = DATA_DIR
    sector_name_tokens = [
        "MAG7",
        "SEMICONDUCTORS",
        "SOFTWARE",
        "ALL_OTHER_TECHNOLOGY",
        "ALL OTHER TECHNOLOGY",
        "BASIC MATERIAL",
        "BASIC_MATERIAL",
        "COMMUNICATION",
        "ENERGY",
        "HEALTHCARE",
        "INDUSTRIAL",
        "CONSUMER_DISCRETIONARY",
        "CONSUMER_DEFENSIVE",
        "FINANCIAL",
        "UTILITY",
    ]
    cab_summary_tab1, cab_summary_tab2 = st.tabs([
        "CURRENT_TREND_SUMMARY",
        "CURRENT_TREND_SUMMARY_ALL_STOCKS",
    ])

    with cab_summary_tab1:
        pattern = os.path.join(base_dir, "CURRENT_TREND_SUMMARY_*.xlsx")
        matching_files = [
            p for p in glob.glob(pattern)
            if "CURRENT_TREND_SUMMARY_ALL_STOCKS_" not in os.path.basename(p)
        ]
        if matching_files:
            latest_file = max(matching_files, key=os.path.getmtime)
            try:
                df = pd.read_excel(latest_file)
                st.subheader("Trend Distribution by Timeframe")
                render_trend_pie_charts(df)
                st.subheader("BULL Percentage Distribution")
                render_bull_pct_donut(df)
                st.subheader("Detailed Summary")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"⚠️ Failed to load CURRENT_TREND_SUMMARY XLSX file: {e}")
        else:
            st.warning("CURRENT_TREND_SUMMARY XLSX file not found.")

        matches = [
            p for p in glob.glob(os.path.join(base_dir, "CURRENT_TREND_SUMMARY_TABLE_*.png"))
            if "CURRENT_TREND_SUMMARY_TABLE_ALL_STOCKS_" not in os.path.basename(p)
        ]
        valid_matches = [path for path in matches if is_valid_png(path)]
        if valid_matches:
            st.image(max(valid_matches, key=os.path.getmtime), width=1500)
        else:
            st.warning("Close Above/Below Summary image not found.")

    with cab_summary_tab2:
        matches = [
            path
            for path in glob.glob(os.path.join(base_dir, "CURRENT_TREND_SUMMARY_ALL_STOCKS_*.xlsx"))
            if re.match(
                r"^CURRENT_TREND_SUMMARY_ALL_STOCKS_(\d{2}_\d{2}_\d{4}|\d{4}-\d{2}-\d{2})\.xlsx$",
                os.path.basename(path),
            )
        ]
        if matches:
            latest_file = max(matches, key=os.path.getmtime)
            try:
                df = pd.read_excel(latest_file)
                st.subheader("Trend Distribution by Timeframe")
                render_trend_pie_charts(df)
                st.subheader("BULL Percentage Distribution")
                render_bull_pct_donut(df)
                st.subheader("Detailed Summary")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"⚠️ Failed to load CURRENT_TREND_SUMMARY_ALL_STOCKS XLSX file: {e}")
        else:
            st.warning("CURRENT_TREND_SUMMARY_ALL_STOCKS XLSX file not found.")

        matches = [
            path
            for path in glob.glob(os.path.join(base_dir, "CURRENT_TREND_SUMMARY_TABLE_ALL_STOCKS_*.png"))
            if re.match(
                r"^CURRENT_TREND_SUMMARY_TABLE_ALL_STOCKS_(\d{2}_\d{2}_\d{4}|\d{4}-\d{2}-\d{2})\.png$",
                os.path.basename(path),
            )
        ]
        valid_matches = [path for path in matches if is_valid_png(path)]
        if valid_matches:
            st.image(max(valid_matches, key=os.path.getmtime), width=1500)
        else:
            st.warning("Close Above/Below Summary - All Stocks image not found.")

###############################################################################################################################################################

# Close Above/Below Sector Summary
with tab_sector_summary:
    st.header("Close Above/Below Sector Summary")
    st.write("Sector-specific trend summaries with detailed tables.")

    base_dir = DATA_DIR
    
    # Define sectors and their names
    sectors = ['MAG7', 'Semiconductors', 'Software', 'All_Other_Technology', 'Basic Material', 'Communication', 'Energy', 'Healthcare', 'Industrial', 'Consumer_Discretionary', 'Consumer_Defensive', 'Financial', 'Utility']

    sector_entries = []
    for sector_name in sectors:
        latest_xlsx = get_latest_sector_xlsx(base_dir, sector_name)
        score = get_bull_minus_bear_score_from_xlsx(latest_xlsx)
        sector_entries.append(
            {
                "name": sector_name,
                "xlsx": latest_xlsx,
                "score": score,
            }
        )

    sector_entries = sorted(
        sector_entries,
        key=lambda item: (item["score"], item["name"]),
        reverse=True,
    )

    sorted_sectors = [entry["name"] for entry in sector_entries]
    inner_tabs = ["BULL_PCT_per_SECTOR"] + sorted_sectors
    sector_tabs = st.tabs(inner_tabs)
    
    def build_sector_variants(name: str) -> set[str]:
        space_name = name.replace("_", " ")
        underscore_name = name.replace(" ", "_")
        variants = {
            name,
            space_name,
            underscore_name,
            space_name.title(),
            underscore_name.title(),
            space_name.upper(),
            underscore_name.upper(),
            space_name.lower(),
            underscore_name.lower(),
        }
        return variants

    with sector_tabs[0]:
        st.subheader("BULL_PCT per Sector")
        donut_columns = st.columns(4)
        for index, entry in enumerate(sector_entries):
            with donut_columns[index % 4]:
                sector_name = entry["name"]
                st.markdown(
                    f'<div style="text-align:center; font-size:1.2rem; font-weight:700; margin-bottom:0.5rem;">{sector_name}</div>',
                    unsafe_allow_html=True,
                )
                latest_xlsx = entry["xlsx"]
                if latest_xlsx:
                    try:
                        df = pd.read_excel(latest_xlsx)
                        render_bull_pct_donut(df)
                    except Exception:
                        st.warning(f"{sector_name} data unreadable.")
                else:
                    st.warning(f"{sector_name} XLSX not found.")

    for sector_tab, sector_name in zip(sector_tabs[1:], sorted_sectors):
        with sector_tab:
            # Display PNG first
            png_matches = []
            for sector_variant in build_sector_variants(sector_name):
                png_matches.extend(
                    glob.glob(
                        os.path.join(
                            base_dir,
                            f"CURRENT_TREND_SUMMARY_TABLE_ALL_STOCKS_{sector_variant}_*.png",
                        )
                    )
                )
            png_matches = list(set(png_matches))
            
            if png_matches:
                latest_png = max(png_matches, key=os.path.getmtime)
                st.image(latest_png, width=1500)
            else:
                st.warning(f"{sector_name} summary PNG not found.")
            
            # Display XLSX as table
            xlsx_matches = []
            for sector_variant in build_sector_variants(sector_name):
                xlsx_matches.extend(
                    glob.glob(
                        os.path.join(
                            base_dir,
                            f"CURRENT_TREND_SUMMARY_ALL_STOCKS_{sector_variant}_*.xlsx",
                        )
                    )
                )
            xlsx_matches = list(set(xlsx_matches))
            
            if xlsx_matches:
                latest_xlsx = max(xlsx_matches, key=os.path.getmtime)
                try:
                    df = pd.read_excel(latest_xlsx)
                    st.markdown("---")
                    st.subheader("Trend Distribution")
                    render_trend_pie_charts(df)
                    st.markdown("---")
                    st.subheader("Detailed Table")
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Failed to load {sector_name} XLSX file: {e}")
            else:
                st.warning(f"{sector_name} summary XLSX not found.")

###############################################################################################################################################################

# Close Above/Below Industry Summary
with tab_industry_summary:
    st.header("Close Above/Below Industry Summary")
    st.write("Industry-specific trend summaries with detailed tables.")

    base_dir = DATA_DIR
    industry_tokens = discover_industry_tokens(base_dir)

    if not industry_tokens:
        st.warning("No industry summary files found yet.")
    else:
        industry_entries = []
        for token in industry_tokens:
            label = industry_label_from_token(token)
            latest_xlsx = get_latest_industry_xlsx(base_dir, token)
            score = get_bull_minus_bear_score_from_xlsx(latest_xlsx)
            industry_entries.append(
                {
                    "token": token,
                    "label": label,
                    "xlsx": latest_xlsx,
                    "score": score,
                }
            )

        industry_entries = sorted(
            industry_entries,
            key=lambda item: (item["score"], item["label"]),
            reverse=True,
        )

        industry_labels = [entry["label"] for entry in industry_entries]
        inner_tabs = ["BULL_PCT_per_INDUSTRY"] + industry_labels
        industry_tabs = st.tabs(inner_tabs)

        with industry_tabs[0]:
            st.subheader("BULL_PCT per Industry")
            donut_columns = st.columns(4)
            for index, entry in enumerate(industry_entries):
                with donut_columns[index % 4]:
                    label = entry["label"]
                    st.markdown(
                        f'<div style="text-align:center; font-size:1.2rem; font-weight:700; margin-bottom:0.5rem;">{label}</div>',
                        unsafe_allow_html=True,
                    )
                    latest_xlsx = entry["xlsx"]
                    if latest_xlsx:
                        try:
                            df = pd.read_excel(latest_xlsx)
                            render_bull_pct_donut(df)
                        except Exception:
                            st.warning(f"{label} data unreadable.")
                    else:
                        st.warning(f"{label} XLSX not found.")

        for industry_tab, entry in zip(industry_tabs[1:], industry_entries):
            with industry_tab:
                token = entry["token"]
                label = entry["label"]

                latest_png = get_latest_industry_png(base_dir, token)
                if latest_png:
                    st.image(latest_png, width=1500)
                else:
                    st.warning(f"{label} summary PNG not found.")

                latest_xlsx = get_latest_industry_xlsx(base_dir, token)
                if latest_xlsx:
                    try:
                        df = pd.read_excel(latest_xlsx)
                        st.markdown("---")
                        st.subheader("Trend Distribution")
                        render_trend_pie_charts(df)
                        st.markdown("---")
                        st.subheader("Detailed Table")
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Failed to load {label} XLSX file: {e}")
                else:
                    st.warning(f"{label} summary XLSX not found.")

###############################################################################################################################################################

# Upcoming Earnings
with tab8:
    st.header("Upcoming Earnings")
    
    base_dir = DATA_DIR

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
    
    base_dir = DATA_DIR

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
        ma_tab_labels = [f"Page {extract_page_number(p)}" for p in latest_run_pages]
        ma_tabs = st.tabs(ma_tab_labels)
        for tab, page_path in zip(ma_tabs, latest_run_pages):
            with tab:
                st.image(page_path, use_container_width=True)
    else:
        st.warning("20/50ma crossover graph images not found.")

###############################################################################################################################################################

# NAAIM Data
with tab10:
    st.header("NAAIM Data")
    st.write("Above 90 seems to be an area where you should start to see a stock market pullback/selloff. Below 40 seems to be an area where you should start to see a stock market rally.")
    
    base_dir = DATA_DIR

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
    st.write("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    st.write("A 1$ move in the SPY creates about a 20% option move gain on 1 week out expiration at the money options.")
    st.write("Its a quick move that i dont hold overnight. I need to be quick with a stop loss and make sure all indicators are in my favor.")

#######################################################################################################################################################################

# SPY/VIX Analysis
with tab_spy_vix:
    st.header("SPY/VIX Analysis")

    base_dir = DATA_DIR

    (
        svix_tab1, svix_tab2, svix_tab3, svix_tab4, svix_tab5, svix_tab6
    ) = st.tabs([
        "VIX Daily Returns & % Positive Rate",
        "SPY Daily Returns & % Positive Rate",
        "VIX Avg Price & STD Dev Bands",
        "SPY Candles with UVXY+SPY Positive Dates",
        "SPY Candles with VIX+SPY Positive Dates",
        "SPY Combined Positive Signals",
    ])

    with svix_tab1:
        vix_weekday_matches = glob.glob(os.path.join(base_dir, "vix_weekday_*_graph.png"))
        if vix_weekday_matches:
            latest_vix_weekday = max(vix_weekday_matches, key=os.path.getmtime)
            st.image(latest_vix_weekday, width=800)
        else:
            st.warning("VIX Weekday Returns & Hit Rate image not found.")

    with svix_tab2:
        spy_weekday_matches = glob.glob(os.path.join(base_dir, "spy_weekday_*_graph.png"))
        if spy_weekday_matches:
            latest_spy_weekday = max(spy_weekday_matches, key=os.path.getmtime)
            st.image(latest_spy_weekday, width=800)
        else:
            st.warning("SPY Daily Returns & % Positive Rate image not found.")

    with svix_tab3:
        matches = glob.glob(os.path.join(base_dir, "vix_analysis_*_graph.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=1200)
        else:
            st.warning("VIX Avg Price & STD Dev Bands image not found.")

    with svix_tab4:
        matches = glob.glob(os.path.join(base_dir, "spy_uvxy_positive_*_graph.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=1200)
        else:
            st.warning("SPY Candles with UVXY+SPY Positive Dates image not found.")

    with svix_tab5:
        matches = glob.glob(os.path.join(base_dir, "spy_vix_positive_*_graph.png"))
        if matches:
            st.image(max(matches, key=os.path.getmtime), width=1200)
        else:
            st.warning("SPY Candles with VIX+SPY Positive Dates image not found.")

    with svix_tab6:
        matches = glob.glob(os.path.join(base_dir, "spy_combined_positive_signals_*.xlsx"))
        if matches:
            latest_file = max(matches, key=os.path.getmtime)
            try:
                combined_df = pd.read_excel(latest_file)
                st.dataframe(combined_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"⚠️ Failed to load combined signal XLSX file: {e}")
        else:
            st.warning("SPY combined positive signals file not found.")

#######################################################################################################################################################################

# SPY Analysis
with tab_spy_analysis:
    st.header("SPY Analysis")

    base_dir = DATA_DIR

    day_tab1, day_tab2, day_tab3, day_tab4, day_tab5 = st.tabs([
        "Daily SPY Gain Chart",
        "SPY Daily Positive Count Ghart",
        "Monthly SPY Gain Chart",
        "Yearly SPY Gain Chart",
        "SPY Last 10 Weeks",
    ])

    with day_tab1:
        gain_chart_path = os.path.join(base_dir, "Daily_SPY_Gain_Chart.png")
        if os.path.exists(gain_chart_path):
            st.image(gain_chart_path, use_container_width=True)
        else:
            st.warning("Daily SPY Gain Chart image not found.")

    with day_tab2:
        positive_count_path = os.path.join(base_dir, "SPY_Daily_Positive_Count_Ghart.png")
        if os.path.exists(positive_count_path):
            st.image(positive_count_path, use_container_width=True)
        else:
            st.warning("SPY Daily Positive Count Ghart image not found.")

    with day_tab3:
        monthly_gain_path = os.path.join(base_dir, "MONTHLY_SPY_Gain_Chart.png")
        if os.path.exists(monthly_gain_path):
            st.image(monthly_gain_path, width=700)
        else:
            st.warning("Monthly SPY Gain Chart image not found.")

    with day_tab4:
        yearly_gain_path = os.path.join(base_dir, "YEARLY_SPY_Gain_Chart.png")
        if os.path.exists(yearly_gain_path):
            st.image(yearly_gain_path, width=700)
        else:
            st.warning("Yearly SPY Gain Chart image not found.")

    with day_tab5:
        spy_10wk_matches = glob.glob(os.path.join(base_dir, "spy_last_10_weeks_*_graph.png"))
        if spy_10wk_matches:
            latest_spy_10wk = max(spy_10wk_matches, key=os.path.getmtime)
            st.image(latest_spy_10wk, width=800)
        else:
            st.warning("SPY Last 10 Weeks image not found.")

#######################################################################################################################################################################

# YTD Analysis
with tab_ytd:
    st.header("YTD Analysis")

    base_dir = DATA_DIR
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
    ytd_sub_sector, ytd_sub_all = st.tabs(["Sector ETFs", "All Stocks"])

    with ytd_sub_sector:
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

                # --- %_FROM_ATH chart ---
                ath_col = find_matching_column(sector_df, ["%_FROM_ATH", "PCT_FROM_ATH", "% From ATH", "pct_from_ath"])
                ticker_col = find_matching_column(sector_df, ["Ticker", "TICKER", "Symbol", "SYMBOL"])
                if ath_col and ticker_col:
                    ath_df = sector_df[[ticker_col, ath_col]].dropna().copy()
                    ath_df[ath_col] = pd.to_numeric(ath_df[ath_col], errors="coerce")
                    ath_df = ath_df.dropna(subset=[ath_col])
                    ath_df = ath_df.sort_values(by=ath_col, ascending=True)  # worst on left
                    colors = ["#e74c3c" if v <= -20 else "#2ecc71" for v in ath_df[ath_col]]

                    import matplotlib.pyplot as plt
                    import matplotlib.ticker as mticker
                    fig, ax = plt.subplots(figsize=(max(10, len(ath_df) * 0.7), 6))
                    ax.bar(ath_df[ticker_col], ath_df[ath_col], color=colors, edgecolor="black", linewidth=0.5)
                    ax.set_ylim(-100, 0)
                    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
                    ax.axhline(-20, color="#e74c3c", linestyle="--", linewidth=1, label="-20% threshold")
                    ax.set_title("Sector ETFs — % From ATH", fontsize=14, fontweight="bold")
                    ax.set_xlabel("Ticker")
                    ax.set_ylabel("% From ATH")
                    ax.legend(fontsize=9)
                    ax.tick_params(axis="x", rotation=45)
                    fig.patch.set_facecolor("#0e1117")
                    ax.set_facecolor("#0e1117")
                    ax.title.set_color("white")
                    ax.xaxis.label.set_color("white")
                    ax.yaxis.label.set_color("white")
                    ax.tick_params(colors="white")
                    for spine in ax.spines.values():
                        spine.set_edgecolor("#444")
                    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("No `%_FROM_ATH` or `Ticker` column found in Sector ETF file for chart.")

            except Exception as e:
                st.error(f"⚠️ Failed to load sector ETF XLSX file: {e}")
        else:
            st.warning("Sector ETF YTD analysis file not found.")

    with ytd_sub_all:
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

    base_dir = DATA_DIR
    fed_page_matches = glob.glob(os.path.join(base_dir, "fed_rates_spy_page_*_graph.png"))

    if fed_page_matches:
        def extract_fed_page_number(path: str) -> int:
            name = os.path.basename(path)
            try:
                return int(name.split("_page_")[1].split("_")[0])
            except Exception:
                return -1

        ordered_pages = sorted(fed_page_matches, key=extract_fed_page_number, reverse=True)
        fed_tab_labels = [f"Page {extract_fed_page_number(p)}" for p in ordered_pages]
        fed_tabs = st.tabs(fed_tab_labels)
        for tab, page_path in zip(fed_tabs, ordered_pages):
            with tab:
                st.image(page_path, use_container_width=True)
    else:
        st.warning("Fed Funds Rate - SPY graph images not found.")

#######################################################################################################################################################################

# Mercury Retrograde Analysis
with tab_mercury:
    st.header("Mercury Retrograde Analysis")

    base_dir = DATA_DIR

    def extract_mercury_page_number(path: str) -> int:
        name = os.path.basename(path)
        try:
            return int(name.split("_page_")[1].split("_")[0])
        except Exception:
            return -1

    summary_matches = glob.glob(os.path.join(base_dir, "mercury_retrograde_summary_*_graph.png"))
    page_matches = glob.glob(os.path.join(base_dir, "mercury_retrograde_spy_page_*_graph.png"))
    ordered_pages = sorted(page_matches, key=extract_mercury_page_number, reverse=True)

    merc_tab_labels = ["Summary Stats"] + [f"Page {extract_mercury_page_number(p)}" for p in ordered_pages]
    merc_tab_items = [None] + ordered_pages  # None placeholder for summary tab
    merc_tabs = st.tabs(merc_tab_labels)

    with merc_tabs[0]:
        if summary_matches:
            latest_summary = max(summary_matches, key=os.path.getmtime)
            st.image(latest_summary, use_container_width=True)
        else:
            st.warning("Mercury retrograde summary image not found.")

    for tab, page_path in zip(merc_tabs[1:], ordered_pages):
        with tab:
            st.image(page_path, use_container_width=True)

    
             


#######################################################################################################################################################################




