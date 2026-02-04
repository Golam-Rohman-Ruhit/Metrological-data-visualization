import numpy as np
import h5py
import xarray as xr
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import matplotlib.dates as mdates
from datetime import timedelta

warnings.filterwarnings('ignore')  # Ignore irrelevant warnings

# ---------------------- 1. Read NC file data ----------------------
with h5py.File("nanjing_2021_t2m.nc", "r") as f:
    print("Datasets in file: ", list(f.keys()))
    # Read core variables and convert to Celsius directly
    t2m = f["t2m"][:] - 273.15               # Temperature data (K to °C)
    lat = f["latitude"][:]                   # Latitude
    lon = f["longitude"][:]                  # Longitude
    time_stamp = f["valid_time"][:]          # Original Unix timestamp (seconds)

# ---------------------- 2. Key fix: Convert Unix timestamp to datetime (Beijing Time) ----------------------
# Step 1: Convert Unix seconds to UTC datetime
time_utc = pd.to_datetime(time_stamp, unit='s')
# Step 2: Convert to Beijing Time (UTC+8, local time of Nanjing)
time_cn = time_utc + timedelta(hours=8)

# ---------------------- 3. Convert to xarray Dataset (unified data structure) ----------------------
ds = xr.Dataset(
    data_vars={
        "t2m": (["valid_time", "latitude", "longitude"], t2m)
    },
    coords={
        "latitude": lat,
        "longitude": lon,
        "valid_time": time_cn  # Use converted Beijing Time
    }
)

# ---------------------- 4. Filter t2m data at specified indices ----------------------
# Longitude index 2, Latitude index 4 (Note: index starts from 0)
t2m_series = ds["t2m"].isel(
    longitude=2,   # Longitude dimension index 2
    latitude=4     # Latitude dimension index 4
)

# Extract converted time axis and temperature values
time_axis = ds["valid_time"].values  # Formatted datetime time axis
t2m_values = t2m_series.values       # Temperature values in °C

# ---------------------- 5. Plot line chart ----------------------
# Set font to support special characters (no need for Chinese font now)
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(12, 6))  # Set figure size

# Plot line chart (x-axis is datetime format)
plt.plot(
    time_axis,        # X-axis: formatted time
    t2m_values,       # Y-axis: t2m values (°C)
    color="#2E86AB",  # Custom color
    linewidth=1.2,    # Line width
    alpha=0.8         # Transparency
)

# ---------------------- 6. Chart beautification (focus on optimizing x-axis ticks) ----------------------
# Set title and axis labels (clearly mark unit as °C)
plt.title(
    f"Nanjing 2021 T2M Time Series",
    fontsize=14,
    fontweight="bold",
    pad=20
)
plt.xlabel("Time (Beijing Time)", fontsize=12, labelpad=10)
plt.ylabel("2m Air Temperature (°C)", fontsize=12, labelpad=10)  # Unified to Celsius

# Core: Set x-axis ticks to 1 per month, formatted as "Jan 2021"
ax = plt.gca()
# Show 1 major tick per month
ax.xaxis.set_major_locator(mdates.MonthLocator())
# Format ticks as "Jan 2021" style
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
# Rotate tick labels to avoid overlap
plt.xticks(ha="right")
# Add grid lines
plt.grid(True, linestyle="--", alpha=0.5)
# Auto-adjust layout
plt.tight_layout()

# ---------------------- 7. Save image ----------------------
plt.savefig(
    "nanjing_t2m_time_series.png",
    dpi=300,        # High resolution
    bbox_inches="tight"  # Save all elements completely
)

# Display chart
plt.show()

# ---------------------- 8. Print key verification information ----------------------
print(f"\nData dimension: {t2m_series.shape}")
print(f"Time range (Beijing Time): {time_axis[0]} to {time_axis[-1]}")
print(f"T2M value range (°C): {np.min(t2m_values):.2f} to {np.max(t2m_values):.2f}")