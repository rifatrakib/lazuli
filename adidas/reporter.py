from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

from adidas.utils import create_directory

sns.set_style("darkgrid", {"axes.facecolor": "#62946050"})


def load_data():
    current_date = datetime.now().date().isoformat()
    location = f"data/dashboard/{current_date}/latest.jl"
    df = pd.read_json(location, lines=True)

    # Convert "sent_at" and "received_at" columns to datetime format
    df["sent_at"] = pd.to_datetime(df["sent_at"])
    df["received_at"] = pd.to_datetime(df["received_at"])

    df["download_time"] = (df["received_at"] - df["sent_at"]).dt.total_seconds()

    # Set "received_at" as the datetime index
    df.set_index("received_at", inplace=True)
    return df


def create_timeseries(df):
    df = df.resample("1S").agg(
        {
            "response_size": "sum",
            "download_time": "mean",
            "sent_at": "count",
        }
    )
    return df


def get_kpis(df):
    total_requests = df["sent_at"].count()
    average_latency = df["download_time"].mean()
    maximum_latency = df["download_time"].max()
    return [
        {"value": f"{total_requests}", "subtext": "Total Requests"},
        {"value": f"{average_latency:.2f}", "subtext": "Average Latency"},
        {"value": f"{maximum_latency:.2f}", "subtext": "Maximum Latency"},
    ]


def plot_kpis(ax, value, subtext):
    rect = FancyBboxPatch(
        (0, 0),
        ax.get_window_extent().width,
        ax.get_window_extent().height,
        boxstyle="round,pad=0.2,rounding_size=0.3",
        linewidth=1,
        facecolor="#629460",
        edgecolor="none",
    )
    ax.text(0.5, 0.6, value, ha="center", va="center", fontsize=48, color="#243119", fontweight="bold")
    ax.text(0.5, 0.4, subtext, ha="center", va="center", fontsize=16, color="#243119")
    ax.add_patch(rect)
    ax.set_axis_off()


def plot_timeseries(ax, ts):
    ax.plot(ts["response_size"], label="Response size")
    ax.set_title("Downloaded response size per second")
    ax.set_ylabel("Downloaded bytes / s")


def save_report(fig):
    location = create_directory("data/report", "png")
    fig.savefig(f"{location}/latest.png")


def create_dashboard():
    df = load_data()
    kpis = get_kpis(df)
    ts = create_timeseries(df)

    fig = plt.figure(layout="constrained", figsize=(12, 8))
    grid = plt.GridSpec(3, 3, figure=fig)

    for i in range(3):
        ax = fig.add_subplot(grid[0, i])
        plot_kpis(ax, **kpis[i])

    ax = fig.add_subplot(grid[1:, :])
    ax.plot(ts["response_size"], color="#243119", lw=3)
    ax.set_title("Total bytes in per second", color="#243119", fontsize=16, fontweight="bold")

    fig.suptitle("Scraper Performance Report", color="#243119", fontsize=36, fontweight="bold")
    save_report(fig)
    plt.show()
