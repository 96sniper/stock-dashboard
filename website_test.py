import streamlit as st
import streamlit.components.v1 as components
import base64
import pandas as pd
import os
from datetime import date, timedelta
import glob
import re
from PIL import Image

# Set to Wide Mode
st.set_page_config(layout="wide")

def show_chart(image_path: str, width: int | None = None, container=None,
               max_width: int = 1100, max_height: int = 520) -> None:
    """Fit charts within 1,100 x 520 pixels without changing PNGs or table sizing."""
    target = st if container is None else container
    try:
        with Image.open(image_path) as image:
            image_width, image_height = image.size
        width_limit = min(max_width, width) if width is not None else max_width
        scale = min(1, width_limit / image_width, max_height / image_height)
        display_width = max(1, int(image_width * scale))
        target.image(image_path, width=display_width)
    except (OSError, ValueError) as error:
        target.error(f"Unable to display chart {os.path.basename(image_path)}: {error}")

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


def render_daily_close_strength_donut(df: pd.DataFrame) -> None:
    ticker_column = find_matching_column(df, ["TICKER"])
    strength_column = find_matching_column(df, ["D_CLOSE_STRENGTH"])
    if ticker_column is None or strength_column is None:
        st.warning("Daily close strength graphic requires TICKER and D_CLOSE_STRENGTH columns.")
        return

    chart_df = df[[ticker_column, strength_column]].copy()
    chart_df[strength_column] = pd.to_numeric(chart_df[strength_column], errors="coerce")
    valid_rows = (
        chart_df[ticker_column].notna()
        & chart_df[ticker_column].astype(str).str.strip().ne("")
        & chart_df[strength_column].between(0, 100)
    )
    excluded_count = int((~valid_rows).sum())
    chart_df = chart_df.loc[valid_rows].drop_duplicates(subset=[ticker_column])
    if chart_df.empty:
        st.warning("No tickers with valid daily close strength values (0-100) to chart.")
        return

    total = len(chart_df)
    above_count = int((chart_df[strength_column] > 50).sum())
    below_count = total - above_count
    above_pct = above_count / total * 100
    below_pct = below_count / total * 100
    st.markdown("#### Daily Close Strength - % of Tickers")
    components.html(
        f"""
        <div style="font-family:Arial,sans-serif; text-align:center; color:#111111;">
          <svg width="220" height="220" viewBox="0 0 180 180" role="img"
               aria-label="Daily close strength: {above_pct:.1f}% above 50%, {below_pct:.1f}% at or below 50%">
            <circle cx="90" cy="90" r="64" fill="none" stroke="#E74C3C" stroke-width="26" />
            <circle cx="90" cy="90" r="64" fill="none" stroke="#2ECC71" stroke-width="26"
                    pathLength="100" stroke-dasharray="{above_pct:.6f} {100 - above_pct:.6f}"
                    transform="rotate(-90 90 90)" />
            <text x="90" y="85" text-anchor="middle" font-size="11" font-weight="700">D_CLOSE</text>
            <text x="90" y="102" text-anchor="middle" font-size="11">{total} tickers</text>
          </svg>
          <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:12px 28px; font-size:14px;">
            <span><span style="color:#2ECC71;">&#9679;</span>
              Above 50%: <b>{above_pct:.1f}%</b> ({above_count} tickers)</span>
            <span><span style="color:#E74C3C;">&#9679;</span>
              50% or below: <b>{below_pct:.1f}%</b> ({below_count} tickers)</span>
          </div>
        </div>
        """,
        height=290,
        scrolling=False,
    )
    st.caption(
        "Percentages use unique tickers with valid D_CLOSE_STRENGTH values (0-100). "
        "Exactly 50% is included in the 50% or below group."
    )
    if excluded_count:
        st.caption(f"Excluded {excluded_count} rows with missing tickers or missing/invalid daily close strength.")


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
tab_trend_summary, tab1, tab_spy_vix, tab_spy_analysis, tab_ytd, tab_candle_strength, tab_beta, tab_fed_funds_spy, tab2, tab3, tab8, tab_market_cap, tab9, tab_drawdown, tab_52_week, tab_crypto, tab11 = st.tabs([
                                                          "Trend Summary", "Seasonality", "SPY/VIX Analysis", "Index Analysis", "YTD Analysis", "Candle Strength", "Price and Volume Stats", "Fed Funds Rate - SPY", "Tail Candles (D-W-M)", "Close Above/Below",
                                                          "Upcoming Earnings", "Market Cap",                                                           "Moving Average Studies", "Drawdown", "52-Week Highs/Lows",                                                          "Crypto", "Notes"])

###############################################################################################################################################################

with tab_trend_summary:
    summary_groups = [
        ("SPY / QQQ / IWM", "indices_trend_summary"),
        ("Sector ETFs", "sector_etfs_trend_summary"),
        ("Favorites", "favorites_trend_summary"),
        ("Additional ETFs", "additional_ETFS_trend_summary"),
        ("All Stocks", "all_stocks_trend_summary"),
    ]
    for summary_tab, (label, prefix) in zip(st.tabs([label for label, _ in summary_groups]), summary_groups):
        with summary_tab:
            if prefix == "all_stocks_trend_summary":
                csv_matches = glob.glob(os.path.join(DATA_DIR, f"{prefix}_*.csv"))
                if not csv_matches:
                    st.warning("All Stocks trend summary CSV not found. Run the combined analysis script to generate it.")
                    continue
                try:
                    stock_trends = pd.read_csv(max(csv_matches, key=os.path.getmtime), keep_default_na=False)
                    trend_columns = [
                        "8_EMA_ABOVE_BELOW", "8_EMA_SLOPE", "DAILY_CLOSE_STATE",
                        "WEEKLY_CLOSE_STATE", "MONTHLY_CLOSE_STATE",
                    ]
                    stock_trends = stock_trends[["TICKER", "DATE", *trend_columns]]
                    if stock_trends.empty:
                        raise ValueError("The all-stock trend summary contains no ticker rows.")
                    unavailable = stock_trends[trend_columns].eq("Unavailable").any(axis=1)
                    if unavailable.any():
                        st.warning(f"Trend data unavailable for {int(unavailable.sum())} tickers; those rows are marked Unavailable.")
                    st.caption("Short term: 8 EMA Above/Below, 8 EMA Slope, Daily. Longer term: Weekly, Monthly.")
                    st.dataframe(stock_trends, use_container_width=True, hide_index=True)
                except (OSError, ValueError, KeyError, pd.errors.ParserError) as e:
                    st.error(f"Unable to load All Stocks trend summary: {e}")
                continue
            summary_path = latest_valid_png(os.path.join(DATA_DIR, f"{prefix}_*.png"))
            if summary_path:
                st.image(summary_path, use_container_width=True)
            else:
                st.warning(f"{label} trend summary PNG not found. Run the combined analysis script to generate it.")

# Home Page
with tab1:

    base_dir = DATA_DIR
    season_tab1, season_tab2, season_tab3, season_tab4, season_tab_mercury = st.tabs([
        "SPY",
        "QQQ",
        "IWM",
        "VIX",
        "Mercury Retrograde",
    ])

    with season_tab1:
        pattern = os.path.join(base_dir, "spy_seasonality_*.png")
        latest_file = latest_valid_png(pattern)
        if latest_file:
            show_chart(latest_file, width=1500)
        else:
            st.warning("SPY seasonality image not found.")

    with season_tab2:
        pattern = os.path.join(base_dir, "qqq_seasonality_*.png")
        latest_file = latest_valid_png(pattern)
        if latest_file:
            show_chart(latest_file, width=1500)
        else:
            st.warning("QQQ seasonality image not found.")

    with season_tab3:
        pattern = os.path.join(base_dir, "iwm_seasonality_*.png")
        latest_file = latest_valid_png(pattern)
        if latest_file:
            show_chart(latest_file, width=1500)
        else:
            st.warning("IWM seasonality image not found.")

    with season_tab4:
        pattern = os.path.join(base_dir, "VIX_seasonality_*.png")
        latest_file = latest_valid_png(pattern)
        if latest_file:
            show_chart(latest_file, width=1500)
        else:
            st.warning("VIX seasonality image not found.")

    with season_tab_mercury:
        st.subheader("Mercury Retrograde")

        def extract_mercury_page_number(path: str) -> int:
            name = os.path.basename(path)
            try:
                return int(name.split("_page_")[1].split("_")[0])
            except Exception:
                return -1

        summary_matches = glob.glob(os.path.join(base_dir, "mercury_retrograde_summary_*_graph.png"))
        if summary_matches:
            st.image(max(summary_matches, key=os.path.getmtime), use_container_width=True)
        else:
            st.warning("Mercury retrograde summary image not found.")

        period_matches = glob.glob(os.path.join(base_dir, "mercury_retrograde_*.xlsx"))
        if period_matches:
            try:
                st.write("Mercury retrograde periods")
                st.dataframe(
                    pd.read_excel(max(period_matches, key=os.path.getmtime)),
                    use_container_width=True,
                    hide_index=True,
                )
            except Exception as e:
                st.error(f"⚠️ Failed to load Mercury retrograde periods file: {e}")
        else:
            st.warning("Mercury retrograde periods file not found.")

        page_matches = glob.glob(os.path.join(base_dir, "mercury_retrograde_spy_page_*_graph.png"))
        if page_matches:
            for page_path in sorted(page_matches, key=extract_mercury_page_number, reverse=True):
                show_chart(page_path)
        else:
            st.warning("Mercury retrograde SPY page images not found.")

###############################################################################################################################################################

# Tail Candles (Daily/Weekly/Monthly)
with tab2:
    st.write("Bottoming Tail Candles minus Topping Tail Candles. Helps to identify the institutional distribution in stocks.")
    base_dir = DATA_DIR

    def show_latest_png(file_pattern: str, not_found_message: str, width: int = 1500,
                        exclude_substring: str | None = None, container=None) -> None:
        target = st if container is None else container
        matches = glob.glob(os.path.join(base_dir, file_pattern))
        if exclude_substring:
            matches = [path for path in matches if exclude_substring not in os.path.basename(path)]

        if matches:
            latest_file = max(matches, key=os.path.getmtime)
            show_chart(latest_file, width=width, container=target)
        else:
            target.warning(not_found_message)

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

    timeframe_tabs = st.tabs(["Daily", "Weekly", "Monthly"])
    for timeframe, timeframe_tab in zip(("Daily", "Weekly", "Monthly"), timeframe_tabs):
        period = timeframe.lower()
        with timeframe_tab:
            count_tab, bullish_tab, bearish_tab = st.tabs([
                f"{timeframe} Count",
                f"{timeframe} Bullish Wick",
                f"{timeframe} Bearish Wick",
            ])

            with count_tab:
                net_column, separate_column = st.columns(2)
                show_latest_png(
                    f"{period}_tail_candle_count_*.png",
                    f"{timeframe} Tail Candle Count image not found.",
                    exclude_substring=f"{period}_tail_candle_count_separate_",
                    container=net_column,
                )
                show_latest_png(
                    f"{period}_tail_candle_count_separate_*.png",
                    f"{timeframe} Tail Candle Count (Separate) image not found.",
                    container=separate_column,
                )

            with bullish_tab:
                show_wick_table(
                    f"{period}_summary_data_*.xlsx",
                    "Bullish Wick",
                    f"{timeframe} Bullish Wick Candles",
                    f"{timeframe} Summary Data file not found.",
                )

            with bearish_tab:
                show_wick_table(
                    f"{period}_summary_data_*.xlsx",
                    "Bearish Wick",
                    f"{timeframe} Bearish Wick Candles",
                    f"{timeframe} Summary Data file not found.",
                )

###############################################################################################################################################################

# Close Above/Below
with tab3:
    base_dir = DATA_DIR
    (
        cab_daily, cab_weekly, cab_monthly, cab_summary_tab1, cab_summary_tab2,
        tab_sector_summary, tab_industry_summary, cab_shaded,
    ) = st.tabs([
        "Daily",
        "Weekly",
        "Monthly",
        "CURRENT_TREND_SUMMARY",
        "CURRENT_TREND_SUMMARY_ALL_STOCKS",
        "Sector Summary",
        "Industry Summary",
        "Shaded Charts",
    ])

    with cab_shaded:
        for timeframe in ("Daily", "Weekly", "Monthly"):
            st.subheader(f"SPY Candles Shaded by {timeframe} Close Above/Below")
            shading_files = glob.glob(os.path.join(base_dir, f"SPY_{timeframe.lower()}_close_above_shading_*.png"))
            if shading_files:
                show_chart(max(shading_files, key=os.path.getmtime), width=1500)
            else:
                st.warning(f"SPY {timeframe.lower()} close above/below shading image not found.")
        st.subheader("SPY Candles Shaded by Combined Daily, Weekly and Monthly Close Above/Below")
        combined_path = latest_valid_png(os.path.join(base_dir, "SPY_combined_dwm_close_above_shading_*.png"))
        if combined_path:
            show_chart(combined_path, width=1500)
            st.caption(
                "Last 4 months. Green: Daily, Weekly and Monthly all Above; red: all Below; mixed states are unshaded. "
                "Developing weekly/monthly candles are reassessed each day against the previous completed candle."
            )
        else:
            st.warning("SPY combined D-W-M shading image not found. Run the combined analysis script to generate it.")

    with cab_daily:
        cab_tab0, cab_tab3 = st.tabs([
            "Daily", "BULL % Trend Over Time",
        ])
    with cab_weekly:
        cab_tab1, cab_tab4 = st.tabs([
            "Weekly", "BULL % Trend Over Time",
        ])
    with cab_monthly:
        cab_tab2, cab_tab5 = st.tabs([
            "Monthly", "BULL % Trend Over Time",
        ])

    with cab_tab0:
        pattern = os.path.join(base_dir, "daily_close_above_below_count_*.png")
        matching_files = glob.glob(pattern)
        if matching_files:
            latest_file = max(matching_files, key=os.path.getmtime)
            show_chart(latest_file, width=1500)
        else:
            st.warning("Daily Close Above Below Count image not found.")

    with cab_tab1:
        pattern = os.path.join(base_dir, "weekly_close_above_below_count_*.png")
        matching_files = glob.glob(pattern)
        if matching_files:
            latest_file = max(matching_files, key=os.path.getmtime)
            show_chart(latest_file, width=1500)
        else:
            st.warning("Weekly Close Above Below Count image not found.")

    with cab_tab2:
        pattern = os.path.join(base_dir, "monthly_close_above_below_count_*.png")
        matching_files = glob.glob(pattern)
        if matching_files:
            latest_file = max(matching_files, key=os.path.getmtime)
            show_chart(latest_file, width=1500)
        else:
            st.warning("Monthly Close Above Below Count image not found.")

    for timeframe, trend_tab in zip(("Daily", "Weekly", "Monthly"), (cab_tab3, cab_tab4, cab_tab5)):
        with trend_tab:
            etf_column, stocks_column = st.columns(2)
            for group, column, all_stocks in (
                ("SECTOR ETFs", etf_column, False), ("ALL STOCKS", stocks_column, True),
            ):
                column.subheader(group.upper())
                matches = [
                    path for path in glob.glob(os.path.join(base_dir, f"BULL_Percentage_Trend_{timeframe}_*.png"))
                    if ("_ALL_STOCKS_" in os.path.basename(path)) == all_stocks
                ]
                if matches:
                    show_chart(max(matches, key=os.path.getmtime), width=850, container=column)
                else:
                    column.warning(f"{timeframe} BULL % Trend - {group.upper()} image not found.")

###############################################################################################################################################################

# Close Above/Below Summary
with tab3:
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
    with cab_summary_tab1:
        st.write("Current trend summary tables and percentage trend analysis for ETFs/indices.")
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
        st.write("Current trend summary tables and percentage trend analysis for the all-stocks universe.")
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
            try:
                st.image(max(valid_matches, key=os.path.getmtime), width=1500)
            except Image.DecompressionBombError:
                st.error("The all-stock summary PNG is too large to display safely. "
                         "Regenerate it with the updated combined script and upload the new PNG. "
                         "The full dataset remains available in the table above.")
        else:
            st.warning("Close Above/Below Summary - All Stocks image not found.")

###############################################################################################################################################################

# Close Above/Below Sector Summary
with tab_sector_summary:
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
    
    base_dir = DATA_DIR

    def latest_earnings_output(suffix: str) -> str | None:
        # Exact match so e.g. "_graph.png" doesn't also pick up "_market_cap_graph.png".
        name_regex = re.compile(r"^earnings_calendar_\d{2}_\d{2}_\d{4}" + re.escape(suffix) + r"$")
        matches = [
            path for path in glob.glob(os.path.join(base_dir, "earnings_calendar_*"))
            if name_regex.match(os.path.basename(path))
        ]
        if suffix.endswith(".png"):
            matches = [path for path in matches if is_valid_png(path)]
        return max(matches, key=os.path.getmtime) if matches else None

    def show_earnings_png(suffix: str, label: str) -> None:
        png_path = latest_earnings_output(suffix)
        if png_path:
            show_chart(png_path)
        else:
            st.warning(f"{label} image not found.")

    def show_csv(csv_path: str | None, label: str) -> None:
        if not csv_path:
            st.warning(f"{label} file not found.")
            return
        try:
            st.dataframe(pd.read_csv(csv_path), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"⚠️ Failed to load {label} CSV file: {e}")

    (
        earnings_calendar_tab,
        earnings_market_cap_tab,
        earnings_full_data_tab,
    ) = st.tabs([
        "Earnings Calendar",
        "Market Cap",
        "Full Data",
    ])

    with earnings_calendar_tab:
        calendar_column, week_column = st.columns([3, 2])
        with calendar_column:
            show_earnings_png("_graph.png", "Earnings calendar graph")
        with week_column:
            weekly_png = latest_earnings_output("_this_week.png")
            if weekly_png:
                st.image(weekly_png, use_container_width=True)
            else:
                st.warning("Earnings This Week image not found. Run the combined analysis script to generate it.")

    with earnings_full_data_tab:
        show_csv(latest_earnings_output(".csv"), "Earnings calendar")

    with earnings_market_cap_tab:
        show_earnings_png("_market_cap_graph.png", "Earnings market cap graph")

###############################################################################################################################################################

# Market Cap
with tab_market_cap:

    sector_market_cap_tab, industry_market_cap_tab, top_stock_market_cap_tab = st.tabs([
        "Sector Market Cap %",
        "Industry Market Cap %",
        "Top 20 Stocks",
    ])

    with sector_market_cap_tab:
        show_earnings_png("_sector_market_cap_graph.png", "Sector market cap graph")

    with industry_market_cap_tab:
        st.caption("Chart shows industries above 1% of total market cap; the table lists all industries.")
        show_earnings_png("_industry_market_cap_graph.png", "Industry market cap graph")
        show_csv(latest_earnings_output("_industry_market_cap.csv"), "Industry market cap")

    with top_stock_market_cap_tab:
        st.caption("The 20 largest tracked stocks, shown as a share of total tracked market cap.")
        show_earnings_png("_top_stock_market_cap_graph.png", "Top 20 stocks market cap graph")

###############################################################################################################################################################

# Moving Average Studies
with tab9:
    tab_20_50_crossover, tab_8ema_study = st.tabs(["20/50 Crossover", "8_EMA Study"])

with tab_20_50_crossover:
    base_dir = DATA_DIR
    crossover_recent_tab, crossover_historical_tab = st.tabs(["Recent", "Historical"])

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
        with crossover_recent_tab:
            recent_columns = st.columns(2)
            for column, page_path in zip(recent_columns, latest_run_pages[:2]):
                column.subheader(f"Page {extract_page_number(page_path)}")
                show_chart(page_path, container=column)
            st.write("SPY daily candlestick pages with MA 20/50 crossover zones and summary stats.")
            st.write("Green Zones show where the 20MA flips above the 50MA. Red Zones show where the 20MA flips below the 50MA.")
            st.write("This chart shows that when a 20/50ma crossover, the odds of price action to a certain direction increases.")
            st.write("This should help me in my short term trading by knowing what price should do.")
            st.write("The price action following a 20/50ma crossover is not guaranteed but the odds increase for a certain direction.")
            st.write("The zones were calculated by looking for the maximum price gain or decline within the zone. This simply gives an idea to what direction price should be heading short term.")
        with crossover_historical_tab:
            for page_path in latest_run_pages[2:]:
                st.subheader(f"Page {extract_page_number(page_path)}")
                show_chart(page_path)
            if len(latest_run_pages) <= 2:
                st.info("No historical crossover pages available for this run.")
    else:
        with crossover_recent_tab:
            st.warning("20/50ma crossover graph images not found.")
        with crossover_historical_tab:
            st.info("No historical crossover pages available.")

###############################################################################################################################################################

# 8_EMA Study
with tab_8ema_study:

    base_dir = DATA_DIR

    def show_8ema_csv(file_name: str, label: str) -> None:
        csv_path = os.path.join(base_dir, file_name)
        if not os.path.exists(csv_path):
            st.warning(f"{file_name} not found.")
            return
        try:
            ema_df = pd.read_csv(csv_path)
            if file_name == "TICKERS_FULL_PRICE_DATA.csv":
                dates = pd.to_datetime(ema_df["DATE"], errors="raise")
                if dates.isna().any() or ema_df["TICKER"].isna().any():
                    raise ValueError("Stock price data contains missing dates or tickers.")
                ema_df = ema_df.loc[dates.sort_values(kind="stable").index]
                ema_df = ema_df.drop_duplicates(subset="TICKER", keep="last").sort_values("TICKER")
        except Exception as e:
            st.error(f"⚠️ Failed to load {label} CSV file: {e}")
            return

        st.dataframe(ema_df, use_container_width=True, hide_index=True)

    ema_stocks_tab, ema_full_data_tab = st.tabs(["Stocks", "Full Data"])

    with ema_stocks_tab:
        ema_breadth_path = latest_valid_png(os.path.join(base_dir, "stocks_8_ema_breadth_*_graph.png"))
        if ema_breadth_path:
            show_chart(ema_breadth_path, max_width=1600, max_height=520)
        else:
            st.warning("Stock 8 EMA breadth chart not found. Run the combined analysis script to generate it.")
        ema_daily_path = latest_valid_png(os.path.join(base_dir, "stocks_8_ema_daily_net_*_graph.png"))
        if ema_daily_path:
            show_chart(ema_daily_path)
        else:
            st.warning("Daily stock 8 EMA chart not found. Run the combined analysis script to generate it.")
    with ema_full_data_tab:
        show_8ema_csv("TICKERS_FULL_PRICE_DATA.csv", "stock")

with tab_crypto:
    crypto_summary_path = latest_valid_png(os.path.join(DATA_DIR, "crypto_trend_summary_*.png"))
    if crypto_summary_path:
        st.image(crypto_summary_path, use_container_width=True)
    else:
        st.warning("Crypto trend summary PNG not found. Run the combined analysis script to generate it.")

###############################################################################################################################################################

# Drawdown
with tab_drawdown:
    drawdown_tickers = ["SPY", "QQQ", "SMH", "IWM", "BTC", "UVXY", "GLD"]
    for drawdown_ticker, drawdown_tab in zip(drawdown_tickers, st.tabs(drawdown_tickers)):
        with drawdown_tab:
            if drawdown_ticker == "UVXY":
                st.caption(
                    "Last 10 years: percentage distance from the 200-day simple moving average of adjusted closes. "
                    "Green is above the average; red is below."
                )
            else:
                st.caption("Last 10 years: percentage below the running adjusted-close peak within the chart window. Zero marks a new or recovered peak.")
            drawdown_path = latest_valid_png(
                os.path.join(DATA_DIR, f"{drawdown_ticker.lower()}_drawdown_*.png")
            )
            if drawdown_path:
                show_chart(drawdown_path)
            else:
                st.warning(f"{drawdown_ticker} drawdown chart not found. Run the combined analysis script to generate it.")

# 52-Week Highs/Lows
with tab_52_week:
    highs_lows_chart_tab, highs_lows_dataset_tab = st.tabs(["Chart", "Full Dataset"])
    with highs_lows_chart_tab:
        highs_lows_path = latest_valid_png(os.path.join(DATA_DIR, "stocks_52_week_highs_lows_*_graph.png"))
        if highs_lows_path:
            show_chart(highs_lows_path, max_width=1800, max_height=520)
            st.caption("Last 252 trading sessions (one trading year). Daily net = new 52-week highs minus new 52-week lows (intraday records vs the prior 252 sessions). Green dot = positive, red dot = negative.")
        else:
            st.warning("52-week highs/lows chart not found. Run the combined analysis script to generate it.")
    with highs_lows_dataset_tab:
        highs_lows_csvs = glob.glob(os.path.join(DATA_DIR, "stocks_52_week_highs_lows_*.csv"))
        if highs_lows_csvs:
            try:
                highs_lows_df = pd.read_csv(max(highs_lows_csvs, key=os.path.getmtime))
                st.dataframe(highs_lows_df.iloc[::-1], use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Could not read 52-week highs/lows data: {e}")

# Notes
with tab11:
    notes_mindset_tab, notes_fomo_tab, notes_spy_options_tab = st.tabs(["Mindset", "FOMO", "SPY Options"])

    with notes_mindset_tab:
        st.subheader("Psychology")
        st.write("Psychology is the most important aspect of trading")
        st.write("Psycology alone is the reason I have blown up accounts.")
        st.write(" ")
        st.write("Extreme Patience")
        st.write("      Each day I should be fine not taking a trade. Just patiently watch the market and my data. Then if something lines up I take it.")
        st.write("      Remember that this trading account is my entire future. Smart trades at the right time will compound into a fortune. Dumb trades at the wrong time will compound into a disaster.")
        st.write("      Most days I will be best off by just watching charts and doing nothing.")
        st.write("      The hardest thing is not trading at all. Most of the time staying away is the best decision.")
        st.write("      Being in a trade is one of the toughest places to be in because rational thinking goes away.")
        st.write("      What ive noticed is by being very-very patient, I am able to identify the best possible trade entries and get out quickly. Not being in a position gave me that ability to read markets correctly.")
        st.write(" ")
        st.write("Day Trading only ")
        st.write("      Try to not hold over the weekend - Dont trade Friday unless there is a quick day trade.")
        st.write("      My mind will be too focussed on news and Bitcoin over the weekend if I enter a position on friday.")
        st.write("      Not to mention the 3 days you lose out on theta.")
        st.write(" ")

        st.write(" ")
        st.write("Reality of Trading")
        st.write("      Its not about finding the perfect trade that will double your money. Its about finding opportunities where reward outweighs the risk and taking a shot.")

    with notes_fomo_tab:
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

    with notes_spy_options_tab:
        st.write("A 1$ move in the SPY creates about a 20% option move gain on 1 week out expiration at the money options.")
        st.write("Its a quick move that i dont hold overnight. I need to be quick with a stop loss and make sure all indicators are in my favor.")

#######################################################################################################################################################################

# SPY/VIX Analysis
with tab_spy_vix:

    base_dir = DATA_DIR

    svix_tab1, svix_tab2, svix_tab3, svix_expected_move_tab = st.tabs([
        "VIX Daily Returns & % Positive Rate",
        "SPY Daily Returns & % Positive Rate",
        "VIX Avg Price & STD Dev Bands",
        "SPY Expected Move",
    ])

    with svix_expected_move_tab:
        current_session_tab, next_session_tab = st.tabs(["Current Session", "Next Session"])
        for session_tab, prefix, label in (
            (current_session_tab, "spy_expected_move_d_w", "Current Session"),
            (next_session_tab, "spy_expected_move_next_session", "Next Session"),
        ):
            with session_tab:
                expected_move_path = latest_valid_png(os.path.join(base_dir, f"{prefix}_*.png"))
                if expected_move_path:
                    show_chart(expected_move_path)
                else:
                    st.warning(f"SPY {label} expected-move PNG not found. Run the combined analysis script to generate it.")

    with svix_tab1:
        vix_four_year_col, vix_last_five_col = st.columns(2)
        vix_four_year_col.subheader("Last 4 Years")
        vix_weekday_path = latest_valid_png(
            os.path.join(base_dir, "vix_weekday_*_graph.png"), exclude_substring="_last_five_",
        )
        if vix_weekday_path:
            show_chart(vix_weekday_path, container=vix_four_year_col)
        else:
            vix_four_year_col.warning("VIX Weekday Returns & Hit Rate image not found.")
        vix_last_five_col.subheader("Last 5 Occurrences per Weekday")
        vix_recent_path = latest_valid_png(os.path.join(base_dir, "vix_weekday_last_five_*_graph.png"))
        if vix_recent_path:
            show_chart(vix_recent_path, container=vix_last_five_col)
        else:
            vix_last_five_col.warning("VIX Last 5 weekday image not found.")

    with svix_tab2:
        spy_four_year_col, spy_last_five_col = st.columns(2)
        spy_four_year_col.subheader("Last 4 Years")
        spy_weekday_path = latest_valid_png(
            os.path.join(base_dir, "spy_weekday_*_graph.png"), exclude_substring="_last_five_",
        )
        if spy_weekday_path:
            show_chart(spy_weekday_path, container=spy_four_year_col)
        else:
            spy_four_year_col.warning("SPY Daily Returns & % Positive Rate image not found.")
        spy_last_five_col.subheader("Last 5 Occurrences per Weekday")
        spy_recent_path = latest_valid_png(os.path.join(base_dir, "spy_weekday_last_five_*_graph.png"))
        if spy_recent_path:
            show_chart(spy_recent_path, container=spy_last_five_col)
        else:
            spy_last_five_col.warning("SPY Last 5 weekday image not found.")

    with svix_tab3:
        matches = glob.glob(os.path.join(base_dir, "vix_analysis_*_graph.png"))
        if matches:
            show_chart(max(matches, key=os.path.getmtime), width=1200)
        else:
            st.warning("VIX Avg Price & STD Dev Bands image not found.")

#######################################################################################################################################################################

# Index Analysis
with tab_spy_analysis:

    base_dir = DATA_DIR

    day_tab1, day_tab2, day_tab3, day_tab4, day_tab5, day_tab6, spy_top_month_tab = st.tabs([
        "Daily SPY Gain Chart",
        "SPY Daily Positive Count Ghart",
        "Monthly Gain Chart",
        "Yearly Gain Chart",
        "SPY Last 10 Weeks",
        "Price vs Avg Trend",
        "SPY_Top_Month",
    ])

    with spy_top_month_tab:
        top_month_path = latest_valid_png(os.path.join(base_dir, "spy_top_month_*.png"))
        if top_month_path:
            show_chart(top_month_path)
        else:
            st.warning("SPY top-month chart not found. Run the combined analysis script to generate it.")

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
        for monthly_row in (["SPY", "QQQ", "IWM"], ["BTC", "CL1!"]):
            monthly_cols = st.columns(3)
            for col, ticker in zip(monthly_cols, monthly_row):
                monthly_gain_path = os.path.join(base_dir, f"MONTHLY_{ticker}_Gain_Chart.png")
                if os.path.exists(monthly_gain_path):
                    col.image(monthly_gain_path, use_container_width=True)
                else:
                    col.warning(f"Monthly {ticker} Gain Chart image not found.")

    with day_tab4:
        for yearly_row in (["SPY", "QQQ", "IWM"], ["CL1!"]):
            yearly_cols = st.columns(3)
            for col, ticker in zip(yearly_cols, yearly_row):
                yearly_gain_path = os.path.join(base_dir, f"YEARLY_{ticker}_Gain_Chart.png")
                if os.path.exists(yearly_gain_path):
                    col.image(yearly_gain_path, use_container_width=True)
                else:
                    col.warning(f"Yearly {ticker} Gain Chart image not found.")

    with day_tab5:
        spy_10wk_matches = glob.glob(os.path.join(base_dir, "spy_last_10_weeks_*_graph.png"))
        if spy_10wk_matches:
            latest_spy_10wk = max(spy_10wk_matches, key=os.path.getmtime)
            st.image(latest_spy_10wk, width=800)
        else:
            st.warning("SPY Last 10 Weeks image not found.")

    with day_tab6:
        trend_tickers = ["SPY", "QQQ", "IWM"]
        for ticker, trend_tab in zip(trend_tickers, st.tabs(trend_tickers)):
            with trend_tab:
                trend_chart_path = os.path.join(base_dir, f"{ticker}_Price_vs_Avg_Trend.png")
                if os.path.exists(trend_chart_path):
                    show_chart(trend_chart_path, width=1000)
                else:
                    st.warning(f"{ticker} Price vs Avg Trend image not found.")

#######################################################################################################################################################################

# YTD Analysis
with tab_ytd:

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
    ytd_sub_sector, ytd_sub_all, sub_tab_yearly, sub_tab_ytd, sub_tab_qtd, sub_tab_ytd_lines = st.tabs(
        ["Sector ETFs", "All Stocks", "Yearly Table", "Year-to-Date", "Quarter-to-Date", "YTD Line Charts"]
    )
    with sub_tab_ytd_lines:
        ytd_line_symbols = [
            "HOOD", "SPCX", "ORCL", "TSLA", "META", "MSFT", "NVDA", "GOOGL",
            "AMZN", "QQQ", "SPY", "AAPL", "IWM", "SMH", "NFLX", "AMD", "BTC", "CL1!",
        ]
        for ticker_tab, symbol in zip(st.tabs(ytd_line_symbols), ytd_line_symbols):
            with ticker_tab:
                line_path = latest_valid_png(os.path.join(base_dir, f"{symbol}_ytd_line_chart_*.png"))
                if line_path:
                    show_chart(line_path)
                else:
                    st.warning(f"{symbol} YTD line chart not found. Run the combined analysis script to generate it.")
    with sub_tab_ytd:
        sub_tab_ytd_sector, sub_tab_favorites, sub_tab_groups = st.tabs(
            ["Sector ETFs", "Favorites", "Industry/Group YTD"]
        )

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
        ath_breadth_path = latest_valid_png(os.path.join(base_dir, "stocks_ath_breadth_*_graph.png"))
        if ath_breadth_path:
            show_chart(ath_breadth_path, max_width=1600, max_height=640)
            st.caption(
                "Percentages use stocks with valid % from ATH values in each group. "
                "Recorded highs use up to 20 years of available price history."
            )
        else:
            st.warning("Stock ATH breadth chart not found. Run the combined analysis script to generate it.")
        ath_history_path = latest_valid_png(os.path.join(base_dir, "stocks_ath_history_*_graph.png"))
        if ath_history_path:
            show_chart(ath_history_path)
            st.caption(
                "Last four years: percentage of the current tracked stocks with an available daily close "
                "below -19.99% from their recorded high as of that day. "
                "Available stocks vary by date; highs use up to 20 years of downloaded history."
            )
        else:
            st.warning("Historical stock ATH breadth chart not found. Run the combined analysis script to generate it.")
        if all_stocks_matches:
            latest_all_stocks_file = max(all_stocks_matches, key=os.path.getmtime)
            try:
                all_stocks_df = pd.read_excel(latest_all_stocks_file)
                all_stocks_table_height = min(900, max(360, row_height * (len(all_stocks_df) + 1) + 12))
                st.dataframe(
                    all_stocks_df,
                    use_container_width=True,
                    height=all_stocks_table_height,
                    hide_index=True,
                    row_height=row_height,
                )
            except Exception as e:
                st.error(f"⚠️ Failed to load all-stocks XLSX file: {e}")
        else:
            st.warning("All stocks YTD analysis file not found.")

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

    with sub_tab_yearly:
        latest_file = latest_sector_chart(
            "sector_etf_yearly_gain_table_*.png",
            "sector_etf_yearly_gain_table.png",
        )
        if latest_file:
            show_chart(latest_file, width=yearly_chart_width, max_width=1600, max_height=700)
        else:
            st.warning("Yearly gain table image not found.")

    with sub_tab_ytd_sector:
        latest_file = latest_sector_chart(
            "etf_ytd_bar_chart_*.png",
            "etf_ytd_bar_chart.png",
        )
        if latest_file:
            show_chart(latest_file, width=sector_chart_width)
        else:
            st.warning("YTD bar chart image not found.")

    with sub_tab_qtd:
        latest_file = latest_sector_chart(
            "etf_qtd_bar_chart_*.png",
            "etf_qtd_bar_chart.png",
        )
        if latest_file:
            show_chart(latest_file, width=sector_chart_width)
        else:
            st.warning("QTD bar chart image not found.")

    with sub_tab_favorites:
        latest_file = latest_sector_chart(
            "favorite_trading_tickers_ytd_bar_chart_*.png",
            "favorite_trading_tickers_ytd_bar_chart.png",
        )
        if latest_file:
            show_chart(latest_file, width=sector_chart_width)
        else:
            st.warning("Favorites YTD bar chart image not found.")

    with sub_tab_groups:
        group_ytd_charts = [
            ("MAG7", "mag7_ytd_bar_chart"),
            ("Semiconductors", "semiconductor_stocks_ytd_bar_chart"),
            ("Semi Equipment & Materials", "semiconductor_equipment_materials_ytd_bar_chart"),
            ("Software Infrastructure", "software_infrastructure_ytd_bar_chart"),
            ("Software Application", "software_application_ytd_bar_chart"),
            ("Restaurants", "restaurants_ytd_bar_chart"),
            ("Residential Construction", "residential_construction_ytd_bar_chart"),
            ("Banks Diversified", "banks_diversified_ytd_bar_chart"),
            ("Credit Services", "credit_services_ytd_bar_chart"),
            ("Energy Sector", "energy_sector_ytd_bar_chart"),
            ("Utilities Sector", "utilities_sector_ytd_bar_chart"),
        ]
        for group_tab, (group_label, group_prefix) in zip(
            st.tabs([label for label, _ in group_ytd_charts]), group_ytd_charts
        ):
            with group_tab:
                latest_file = latest_sector_chart(f"{group_prefix}_*.png", f"{group_prefix}.png")
                if latest_file:
                    show_chart(latest_file, width=sector_chart_width)
                else:
                    st.warning(f"{group_label} YTD bar chart image not found.")

#######################################################################################################################################################################

# Candle Strength
with tab_candle_strength:

    base_dir = DATA_DIR
    candle_chart_tab, candle_dataset_tab = st.tabs(["Chart", "Full Dataset"])
    with candle_chart_tab:
        candle_breadth_path = latest_valid_png(os.path.join(base_dir, "candle_strength_breadth_*_graph.png"))
        if candle_breadth_path:
            show_chart(candle_breadth_path, width=1000)
            st.caption(
                "Each bar uses unique tickers with a valid value for that measure. "
                "Green is above 50%; red includes exactly 50% and below."
            )
        else:
            st.warning("Candle strength breadth chart not found. Run the combined analysis script to generate it.")

with candle_dataset_tab:
    etf_matches = glob.glob(os.path.join(base_dir, "ETF_CANDLE_STRENGTH*.xlsx"))

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
    st.subheader("ETF Candle Strength")
    if etf_matches:
        latest_etf_file = max(etf_matches, key=os.path.getmtime)
        try:
            etf_df = pd.read_excel(latest_etf_file)
            etf_table_height = min(900, max(360, row_height * (len(etf_df) + 1) + 12))
            st.dataframe(
                etf_df,
                use_container_width=True,
                height=etf_table_height,
                hide_index=True,
                row_height=row_height,
            )
        except Exception as e:
            st.error(f"⚠️ Failed to load ETF candle strength XLSX file: {e}")
    else:
        st.warning("ETF candle strength file not found.")

#######################################################################################################################################################################

# Price and Volume Stats
with tab_beta:

    beta_tab, volume_stats_tab = st.tabs(["Beta", "Volume Stats"])

    base_dir = DATA_DIR
    beta_matches = glob.glob(os.path.join(base_dir, "AVERAGE_PCT_MOVES_*.xlsx"))

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

    with beta_tab:
        st.subheader("Beta - Average Daily % Moves")
        st.write("Average absolute daily % moves over the past year, sorted from highest to lowest.")

        if beta_matches:
            latest_beta_file = max(beta_matches, key=os.path.getmtime)
            try:
                beta_df = pd.read_excel(latest_beta_file)
                beta_table_height = min(900, max(360, 24 * (len(beta_df) + 1) + 12))
                st.dataframe(
                    beta_df,
                    use_container_width=True,
                    height=beta_table_height,
                    hide_index=True,
                    row_height=24,
                )
            except Exception as e:
                st.error(f"⚠️ Failed to load beta (average % moves) XLSX file: {e}")
        else:
            st.warning("Average % moves XLSX file not found.")

    with volume_stats_tab:
        st.subheader("Volume Stats")
        st.write("Latest daily volume, 20 trading day average volume, today's relative volume (current / 20 day average), and AVG_DAILY_PCT_MOVE (average absolute close-to-close % move over the last 20 trading days).")
        volume_stats_path = os.path.join(base_dir, "STOCKS_VOLUME_STATS.csv")
        show_csv(volume_stats_path if os.path.exists(volume_stats_path) else None, "STOCKS_VOLUME_STATS")

#######################################################################################################################################################################

# Fed Funds Rate - SPY
with tab_fed_funds_spy:

    base_dir = DATA_DIR

    fed_calendar_tab, fed_datasets_tab = st.tabs(["Calendar", "Full Datasets"])
    with fed_calendar_tab:
        fed_calendar_path = latest_valid_png(os.path.join(base_dir, "fed_meeting_calendar_*.png"))
        if fed_calendar_path:
            show_chart(fed_calendar_path, max_width=1800, max_height=720)
        else:
            st.warning("Fed meeting calendar PNG not found. Run the combined analysis script to generate it.")

    with fed_datasets_tab:
        fed_meeting_matches = glob.glob(os.path.join(base_dir, "fed_meeting_dates_*.csv"))
        if fed_meeting_matches:
            latest_fed_meetings = max(fed_meeting_matches, key=os.path.getmtime)
            try:
                fed_meetings_df = pd.read_csv(latest_fed_meetings)
                upcoming_meetings = fed_meetings_df[fed_meetings_df["STATUS"] == "Upcoming"]
                prior_meetings = fed_meetings_df[fed_meetings_df["STATUS"] == "Prior"].iloc[::-1]
                st.write("Upcoming meetings")
                st.dataframe(upcoming_meetings, use_container_width=True, hide_index=True)
                st.write("Prior meetings (most recent first)")
                st.dataframe(prior_meetings, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"⚠️ Failed to load Fed meeting dates CSV file: {e}")
        else:
            st.warning("Fed meeting dates CSV file not found.")
