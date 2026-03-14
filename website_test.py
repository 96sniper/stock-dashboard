import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.transforms as mtransforms
from matplotlib.patches import Rectangle


def compute_zone_metrics(df: pd.DataFrame, range_start: pd.Timestamp, range_end: pd.Timestamp) -> pd.DataFrame:
    plot_df = df.dropna(subset=["Open", "High", "Low", "Close", "MA_20", "MA_50"]).copy()
    plot_df = plot_df[(plot_df["Date"] >= range_start) & (plot_df["Date"] <= range_end)].copy()
    if plot_df.empty:
        return pd.DataFrame(columns=["ZONE_TYPE", "LENGTH_DAYS", "MAX_PCT", "MIN_PCT"])

    ma_diff = plot_df["MA_20"] - plot_df["MA_50"]
    bullish_cross = (ma_diff > 0) & (ma_diff.shift(1) <= 0)
    bearish_cross = (ma_diff < 0) & (ma_diff.shift(1) >= 0)

    bullish_dates = plot_df.loc[bullish_cross.fillna(False), "Date"].sort_values()
    bearish_dates = plot_df.loc[bearish_cross.fillna(False), "Date"].sort_values()
    cross_events = [(dt, "green") for dt in bullish_dates] + [(dt, "red") for dt in bearish_dates]
    cross_events.sort(key=lambda item: item[0])

    start_date = plot_df["Date"].iloc[0]
    end_date = plot_df["Date"].iloc[-1]
    initial_color = "green" if ma_diff.iloc[0] >= 0 else "red"

    segment_start = start_date
    current_color = initial_color
    zone_segments: list[tuple[pd.Timestamp, pd.Timestamp, str]] = []

    for cross_date, cross_color in cross_events:
        if cross_date > segment_start:
            zone_segments.append((segment_start, cross_date, current_color))
        segment_start = cross_date
        current_color = cross_color

    if end_date > segment_start:
        zone_segments.append((segment_start, end_date, current_color))

    rows = []
    for zone_start, zone_end, zone_color in zone_segments:
        if zone_end <= zone_start:
            continue

        if zone_end == end_date:
            zone_df = plot_df[(plot_df["Date"] >= zone_start) & (plot_df["Date"] <= zone_end)]
        else:
            zone_df = plot_df[(plot_df["Date"] >= zone_start) & (plot_df["Date"] < zone_end)]

        if zone_df.empty:
            continue

        start_close = float(zone_df.iloc[0]["Close"])
        highest_price = float(zone_df["High"].max())
        lowest_price = float(zone_df["Low"].min())

        rows.append(
            {
                "ZONE_TYPE": "BULLISH" if zone_color == "green" else "BEARISH",
                "LENGTH_DAYS": int(len(zone_df)),
                "MAX_PCT": ((highest_price / start_close) - 1) * 100,
                "MIN_PCT": ((lowest_price / start_close) - 1) * 100,
            }
        )

    return pd.DataFrame(rows)


def summarize_zone_metrics(metrics_df: pd.DataFrame) -> dict:
    if metrics_df.empty:
        return {
            "bull_count": 0,
            "bear_count": 0,
            "bull_length": np.nan,
            "bear_length": np.nan,
            "bull_max": np.nan,
            "bull_min": np.nan,
            "bear_max": np.nan,
            "bear_min": np.nan,
        }

    bull = metrics_df[metrics_df["ZONE_TYPE"] == "BULLISH"]
    bear = metrics_df[metrics_df["ZONE_TYPE"] == "BEARISH"]

    return {
        "bull_count": int(len(bull)),
        "bear_count": int(len(bear)),
        "bull_length": float(bull["LENGTH_DAYS"].mean()) if not bull.empty else np.nan,
        "bull_max_length": float(bull["LENGTH_DAYS"].max()) if not bull.empty else np.nan,
        "bear_length": float(bear["LENGTH_DAYS"].mean()) if not bear.empty else np.nan,
        "bear_max_length": float(bear["LENGTH_DAYS"].max()) if not bear.empty else np.nan,
        "bull_max": float(bull["MAX_PCT"].mean()) if not bull.empty else np.nan,
        "bull_min": float(bull["MIN_PCT"].mean()) if not bull.empty else np.nan,
        "bull_highest_max": float(bull["MAX_PCT"].max()) if not bull.empty else np.nan,
        "bull_lowest_min": float(bull["MIN_PCT"].min()) if not bull.empty else np.nan,
        "bear_max": float(bear["MAX_PCT"].mean()) if not bear.empty else np.nan,
        "bear_min": float(bear["MIN_PCT"].mean()) if not bear.empty else np.nan,
        "bear_highest_max": float(bear["MAX_PCT"].max()) if not bear.empty else np.nan,
        "bear_lowest_min": float(bear["MIN_PCT"].min()) if not bear.empty else np.nan,
    }


def build_zone_stats_text(summary: dict) -> str:
    if summary["bull_count"] == 0 and summary["bear_count"] == 0:
        return "No zone metrics available for this date range."

    def fmt_num(value: float) -> str:
        return "N/A" if np.isnan(value) else f"{value:.2f}"

    return (
        f"Bullish Zones Count: {summary['bull_count']}\n"
        f"Bearish Zones Count: {summary['bear_count']}\n\n"
        f"Average Length (Bullish): {fmt_num(summary['bull_length'])} trading days\n"
        f"Average Length (Bearish): {fmt_num(summary['bear_length'])} trading days\n\n"
        f"Bullish Zone Averages\n"
        f"  MAX: {fmt_num(summary['bull_max'])}%   MIN: {fmt_num(summary['bull_min'])}%\n\n"
        f"Bearish Zone Averages\n"
        f"  MAX: {fmt_num(summary['bear_max'])}%   MIN: {fmt_num(summary['bear_min'])}%"
    )


def draw_candles_with_ma_crosses(ax: plt.Axes, df: pd.DataFrame, range_start: pd.Timestamp, range_end: pd.Timestamp, page_title: str) -> None:
    plot_df = df.dropna(subset=["Open", "High", "Low", "Close", "MA_20", "MA_50"]).copy()
    plot_df = plot_df[(plot_df["Date"] >= range_start) & (plot_df["Date"] <= range_end)].copy()
    if plot_df.empty:
        ax.set_title(f"{page_title} (No data)")
        return

    x = mdates.date2num(np.array(plot_df["Date"].dt.to_pydatetime()))
    bar_width = 0.6

    ma_diff = plot_df["MA_20"] - plot_df["MA_50"]
    bullish_cross = (ma_diff > 0) & (ma_diff.shift(1) <= 0)
    bearish_cross = (ma_diff < 0) & (ma_diff.shift(1) >= 0)

    bullish_dates = plot_df.loc[bullish_cross.fillna(False), "Date"].sort_values()
    bearish_dates = plot_df.loc[bearish_cross.fillna(False), "Date"].sort_values()

    cross_events = [(dt, "green") for dt in bullish_dates] + [(dt, "red") for dt in bearish_dates]
    cross_events.sort(key=lambda item: item[0])

    start_date = plot_df["Date"].iloc[0]
    end_date = plot_df["Date"].iloc[-1]

    initial_color = "green" if ma_diff.iloc[0] >= 0 else "red"
    segment_start = start_date
    current_color = initial_color
    zone_segments: list[tuple[pd.Timestamp, pd.Timestamp, str]] = []

    for cross_date, cross_color in cross_events:
        if cross_date > segment_start:
            ax.axvspan(segment_start, cross_date, color=current_color, alpha=0.08, zorder=0)
            zone_segments.append((segment_start, cross_date, current_color))
        segment_start = cross_date
        current_color = cross_color

    if end_date > segment_start:
        ax.axvspan(segment_start, end_date, color=current_color, alpha=0.08, zorder=0)
        zone_segments.append((segment_start, end_date, current_color))

    for i, (_, row) in enumerate(plot_df.iterrows()):
        open_price = row["Open"]
        high_price = row["High"]
        low_price = row["Low"]
        close_price = row["Close"]
        color = "green" if close_price >= open_price else "red"

        ax.vlines(x[i], low_price, high_price, color=color, linewidth=0.7, alpha=0.85, zorder=2)

        body_bottom = min(open_price, close_price)
        body_height = abs(close_price - open_price)
        if body_height == 0:
            ax.hlines(close_price, x[i] - bar_width / 2, x[i] + bar_width / 2, color=color, linewidth=1.0)
        else:
            ax.add_patch(
                Rectangle(
                    (x[i] - bar_width / 2, body_bottom),
                    bar_width,
                    body_height,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=0.6,
                    alpha=0.8,
                    zorder=2,
                )
            )

    ax.plot(plot_df["Date"], plot_df["MA_20"], color="blue", linewidth=1.1, label="MA 20", zorder=3)
    ax.plot(plot_df["Date"], plot_df["MA_50"], color="purple", linewidth=1.1, label="MA 50", zorder=3)

    for dt in bullish_dates:
        ax.axvline(dt, color="green", linewidth=1.0, alpha=0.65, zorder=4)
    for dt in bearish_dates:
        ax.axvline(dt, color="red", linewidth=1.0, alpha=0.65, zorder=4)

    ax.set_title(page_title, pad=46)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid(True, alpha=0.25)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    x_data_y_axes = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    for zone_start, zone_end, zone_color in zone_segments:
        if zone_end <= zone_start:
            continue

        if zone_end == end_date:
            zone_df = plot_df[(plot_df["Date"] >= zone_start) & (plot_df["Date"] <= zone_end)]
        else:
            zone_df = plot_df[(plot_df["Date"] >= zone_start) & (plot_df["Date"] < zone_end)]
        if zone_df.empty:
            continue

        start_close = float(zone_df.iloc[0]["Close"])
        highest_price = float(zone_df["High"].max())
        lowest_price = float(zone_df["Low"].min())
        gain_pct = ((highest_price / start_close) - 1) * 100
        loss_pct = ((lowest_price / start_close) - 1) * 100

        mid_x = zone_start + (zone_end - zone_start) / 2
        box_h = 0.035
        box_y = 0.952 if zone_color == "green" else 0.910
        zone_start_num = mdates.date2num(pd.Timestamp(zone_start))
        zone_end_num = mdates.date2num(pd.Timestamp(zone_end))
        box_w = zone_end_num - zone_start_num

        if box_w > 0:
            ax.add_patch(
                Rectangle(
                    (zone_start_num, box_y),
                    box_w,
                    box_h,
                    transform=x_data_y_axes,
                    facecolor="white",
                    edgecolor=zone_color,
                    linewidth=0.8,
                    alpha=0.75,
                    zorder=1,
                )
            )

        ax.text(
            mid_x,
            box_y + box_h / 2,
            f"MAX {gain_pct:+.2f}%\nMIN {loss_pct:+.2f}%",
            transform=x_data_y_axes,
            ha="center",
            va="center",
            fontsize=6.4,
            color="black",
            zorder=5,
        )

    label_y_bull = 1.012
    label_y_bear = 1.043

    for dt in bullish_dates:
        ax.text(
            dt,
            label_y_bull,
            dt.strftime("%m/%d"),
            transform=x_data_y_axes,
            ha="center",
            va="bottom",
            fontsize=8,
            color="green",
            zorder=5,
            clip_on=False,
        )
    for dt in bearish_dates:
        ax.text(
            dt,
            label_y_bear,
            dt.strftime("%m/%d"),
            transform=x_data_y_axes,
            ha="center",
            va="bottom",
            fontsize=8,
            color="red",
            zorder=5,
            clip_on=False,
        )

    ax.legend(loc="upper left", fontsize=9)


def plot_candles_with_ma_cross_book(df: pd.DataFrame) -> None:
    plot_df = df.dropna(subset=["Open", "High", "Low", "Close", "MA_20", "MA_50"]).copy()
    if plot_df.empty:
        return

    latest_date = plot_df["Date"].max()
    start_20y = latest_date - pd.DateOffset(years=20)
    chart_page_count = 5

    periods = []
    for idx in range(chart_page_count):
        period_start = start_20y + pd.DateOffset(years=4 * idx)
        period_end = start_20y + pd.DateOffset(years=4 * (idx + 1))
        if idx == chart_page_count - 1:
            period_end = latest_date
        periods.append(
            {
                "type": "chart",
                "start": period_start,
                "end": period_end,
                "label": f"{period_start.year}-{period_end.year}",
            }
        )

    overall_metrics = compute_zone_metrics(plot_df, start_20y, latest_date)
    periods.append(
        {
            "type": "stats",
            "label": "Summary Stats",
            "metrics_df": overall_metrics,
            "start": start_20y,
            "end": latest_date,
        }
    )
    total_pages = len(periods)

    fig, ax = plt.subplots(figsize=(16, 8))
    plt.subplots_adjust(top=0.90)

    page_state = {"idx": 0}

    def render_page(idx: int) -> None:
        idx = idx % len(periods)
        page_state["idx"] = idx
        ax.clear()
        page = periods[idx]

        if page["type"] == "chart":
            range_start = page["start"]
            range_end = page["end"]
            title = (
                f"SPY Daily Candles with MA 20/50 Crossovers | Page {idx + 1}/{total_pages}: {page['label']}"
                f" ({range_start.strftime('%Y-%m-%d')} to {range_end.strftime('%Y-%m-%d')})"
            )
            draw_candles_with_ma_crosses(ax, plot_df, range_start, range_end, title)
        else:
            title = (
                f"SPY MA 20/50 Zone Stats | Page {idx + 1}/{total_pages}: {page['label']}"
                f" ({page['start'].strftime('%Y-%m-%d')} to {page['end'].strftime('%Y-%m-%d')})"
            )
            ax.set_title(title, pad=20)
            ax.axis("off")
            summary = summarize_zone_metrics(page["metrics_df"])

            # Visual 1: Average MAX/MIN (%) by zone type
            range_ax = ax.inset_axes([0.06, 0.54, 0.90, 0.38])
            labels = ["Bullish", "Bearish"]
            x_pos = np.arange(len(labels))
            width = 0.34
            max_vals = [summary["bull_max"], summary["bear_max"]]
            min_vals = [summary["bull_min"], summary["bear_min"]]

            bars_max = range_ax.bar(x_pos - width / 2, max_vals, width, label="AVG MAX %", color="#2e8b57", alpha=0.85)
            bars_min = range_ax.bar(x_pos + width / 2, min_vals, width, label="AVG MIN %", color="#d9534f", alpha=0.85)

            # Wick per scenario: highest MAX down to lowest MIN (full observed range)
            wick_high = [summary["bull_highest_max"], summary["bear_highest_max"]]
            wick_low = [summary["bull_lowest_min"], summary["bear_lowest_min"]]
            for i, x_center in enumerate(x_pos):
                if np.isnan(wick_high[i]) or np.isnan(wick_low[i]):
                    continue
                range_ax.vlines(x_center, wick_low[i], wick_high[i], color="black", linewidth=1.4, zorder=4)
                cap_half = 0.07
                range_ax.hlines(wick_high[i], x_center - cap_half, x_center + cap_half, color="black", linewidth=1.2, zorder=4)
                range_ax.hlines(wick_low[i], x_center - cap_half, x_center + cap_half, color="black", linewidth=1.2, zorder=4)

            range_ax.axhline(0, color="black", linewidth=0.8)
            range_ax.set_xticks(x_pos)
            range_ax.set_xticklabels(labels)
            range_ax.set_ylabel("%")
            range_ax.set_title("Average Zone Range (%)", fontsize=10)
            range_ax.grid(True, axis="y", alpha=0.25)
            range_ax.legend(fontsize=8, loc="upper right")

            for bars in (bars_max, bars_min):
                for bar in bars:
                    height = bar.get_height()
                    if np.isnan(height):
                        continue
                    y_pos = height + (0.25 if height >= 0 else -0.25)
                    va = "bottom" if height >= 0 else "top"
                    range_ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        y_pos,
                        f"{height:.2f}%",
                        ha="center",
                        va=va,
                        fontsize=8,
                    )

            # Visual 2: Average zone length by type
            length_ax = ax.inset_axes([0.06, 0.08, 0.90, 0.34])
            length_vals = [summary["bull_length"], summary["bear_length"]]
            length_colors = ["#2e8b57", "#d9534f"]
            length_x = np.arange(len(labels))
            length_bars = length_ax.bar(length_x, length_vals, color=length_colors, alpha=0.85)
            length_ax.set_xticks(length_x)
            length_ax.set_xticklabels(labels)
            length_ax.set_title("Average Zone Length (Trading Days)", fontsize=10)
            length_ax.set_ylabel("Days")
            length_ax.grid(True, axis="y", alpha=0.25)

            # Max-length wick per scenario: average length up to longest observed length
            max_len_vals = [summary["bull_max_length"], summary["bear_max_length"]]
            for i, x_center in enumerate(length_x):
                if np.isnan(length_vals[i]) or np.isnan(max_len_vals[i]):
                    continue
                if max_len_vals[i] > length_vals[i]:
                    length_ax.vlines(x_center, length_vals[i], max_len_vals[i], color="black", linewidth=1.4, zorder=4)
                    cap_half = 0.08
                    length_ax.hlines(max_len_vals[i], x_center - cap_half, x_center + cap_half, color="black", linewidth=1.2, zorder=4)
                    length_ax.text(
                        x_center,
                        max_len_vals[i] + 1.2,
                        f"max {max_len_vals[i]:.0f}",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                        color="black",
                    )

            for bar in length_bars:
                height = bar.get_height()
                if np.isnan(height):
                    continue
                length_ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 0.7,
                    f"{height:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        fig.canvas.draw_idle()

    def next_page(event=None) -> None:
        render_page(page_state["idx"] + 1)

    def prev_page(event=None) -> None:
        render_page(page_state["idx"] - 1)

    def on_key(event) -> None:
        if event.key in ["right", "d", "n"]:
            next_page(None)
        elif event.key in ["left", "a", "p"]:
            prev_page(None)

    def save_all_pages_as_png(upload_dir: str) -> None:
        tdy = datetime.today().strftime("%Y-%m-%d")
        graph_prefix = f"spy_daily_data_{tdy}"
        old_graph_files = glob.glob(os.path.join(upload_dir, "spy_daily_data_*_page_*_graph.png"))

        for file_path in old_graph_files:
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted: {file_path}")
            except Exception as exc:
                print(f"⚠️ Failed to delete {file_path}: {exc}")

        for idx in range(total_pages):
            render_page(idx)
            page_path = os.path.join(upload_dir, f"{graph_prefix}_page_{idx + 1}_graph.png")
            fig.savefig(page_path, dpi=150, bbox_inches="tight")
            print(f"📊 Saved graph: {page_path}")

    fig._key_cid = fig.canvas.mpl_connect("key_press_event", on_key)
    render_page(0)

    upload_dir = r"C:\Users\jrrub\Stock Script Analysis Charts\stock-dashboard\uploads"
    os.makedirs(upload_dir, exist_ok=True)
    save_all_pages_as_png(upload_dir)
    render_page(page_state["idx"])

# Download SPY daily data since 1/1/2000
print("Downloading SPY daily data since 2000...")
end_date_exclusive = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
spy_data = yf.download("SPY", start="2000-01-01", end=end_date_exclusive, interval="1d", progress=False, auto_adjust=False)

# Reset index to make Date a column
spy_data = spy_data.reset_index()

# Flatten multi-level columns (yfinance creates multi-index columns)
spy_data.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in spy_data.columns.values]

# Keep only Date, Open, Close, Volume columns
spy_data = spy_data[['Date', 'Open_SPY', 'High_SPY', 'Low_SPY', 'Close_SPY', 'Volume_SPY']].copy()

# Rename columns for simplicity
spy_data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

# Calculate moving averages
spy_data['MA_20'] = spy_data['Close'].rolling(window=20).mean()
spy_data['MA_50'] = spy_data['Close'].rolling(window=50).mean()

# Add WEEKDAY column (0=Monday, 6=Sunday)
spy_data['WEEKDAY'] = spy_data['Date'].dt.day_name()

# Calculate % change: (previous close - today's close) / previous close * 100
previous_close = spy_data['Close'].shift(1)
pct_change = ((previous_close - spy_data['Close']) / previous_close * 100).round(2)
spy_data['PCT_CHANGE'] = pct_change

# Extract Month/Day as a string for grouping (do this before reordering)
spy_data['Month_Day'] = spy_data['Date'].dt.strftime('%m/%d')

# Reorder columns for clarity
spy_data = spy_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'MA_20', 'MA_50', 'WEEKDAY', 'PCT_CHANGE', 'Month_Day']]

# Display first few rows
print(f"\nTotal trading days since 2000: {len(spy_data)}")
print("\nFirst 5 rows:")
print(spy_data.head())
print("\nLast 5 rows:")
print(spy_data.tail())

# Save to CSV
output_path = r'C:\Users\jrrub\Stock Script Analysis Charts\SPY_Daily_Data_2000_Present.csv'
spy_data.to_csv(output_path, index=False)
print(f"\nData saved to: {output_path}")

# Create a dataframe for unique dates of year (MM/DD) with statistics
print("\n" + "="*80)
print("Creating seasonality dataframe for unique dates of year (MM/DD)...")

# Filter out rows with NaN PCT_CHANGE (first row will be NaN)
spy_data_clean = spy_data.dropna(subset=['PCT_CHANGE'])

# Group by Month/Day and calculate statistics
seasonality_df = spy_data_clean.groupby('Month_Day').agg(
    AVG_PCT_CHANGE=('PCT_CHANGE', 'mean'),
    DATE_COUNT=('PCT_CHANGE', 'count'),
    DATE_COUNT_GREATER_THAN_0=('PCT_CHANGE', lambda x: (x > 0).sum())
).reset_index()

# Calculate PCT_POSITIVE
seasonality_df['PCT_POSITIVE'] = (seasonality_df['DATE_COUNT_GREATER_THAN_0'] / seasonality_df['DATE_COUNT'] * 100).round(2)

# Round AVG_PCT_CHANGE to 2 decimals
seasonality_df['AVG_PCT_CHANGE'] = seasonality_df['AVG_PCT_CHANGE'].round(2)

# Reorder columns
seasonality_df = seasonality_df[['Month_Day', 'AVG_PCT_CHANGE', 'PCT_POSITIVE', 'DATE_COUNT', 'DATE_COUNT_GREATER_THAN_0']]

# Rename Month_Day to Date for clarity
seasonality_df = seasonality_df.rename(columns={'Month_Day': 'Date'})

print(f"\nTotal unique dates of year: {len(seasonality_df)}")
print("\nFirst 10 rows:")
print(seasonality_df.head(10))
print("\nLast 10 rows:")
print(seasonality_df.tail(10))

# Save seasonality dataframe to CSV
seasonality_path = r'C:\Users\jrrub\Stock Script Analysis Charts\SPY_Seasonality_Stats.csv'
seasonality_df.to_csv(seasonality_path, index=False)
print(f"\nSeasonality data saved to: {seasonality_path}")

# Plot daily candles and MA 20/50 crossover zones as a 3-page interactive book
plot_candles_with_ma_cross_book(spy_data)
#plt.show()
