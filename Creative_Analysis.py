import numpy as np
import h5py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import warnings

warnings.filterwarnings('ignore')

# ১. ডেটা লোড করা [cite: 45]
with h5py.File("nanjing_2021_t2m.nc", "r") as f:
    t2m = f["t2m"][:] - 273.15  # কেলভিন থেকে সেলসিয়াসে রূপান্তর [cite: 46]
    time_stamp = f["valid_time"][:] # [cite: 49]

# ২. সময় রূপান্তর (Beijing Time) [cite: 51, 52]
time_utc = pd.to_datetime(time_stamp, unit='s')
time_cn = time_utc + timedelta(hours=8)

# ৩. নির্দিষ্ট লোকেশন সিলেকশন (Nanjing Index) [cite: 63-65]
# longitude index 2, latitude index 4
t2m_values = t2m[:, 4, 2]

# ৪. সৃজনশীল বিশ্লেষণ (Creative Analysis)
# সর্বোচ্চ এবং সর্বনিম্ন তাপমাত্রা বের করা
max_temp = np.max(t2m_values)
min_temp = np.min(t2m_values)
max_idx = np.argmax(t2m_values)
min_idx = np.argmin(t2m_values)

# ৭ দিনের মুভিং অ্যাভারেজ (Trend analysis)
df = pd.DataFrame({'temp': t2m_values}, index=time_cn)
df['moving_avg'] = df['temp'].rolling(window=24*7).mean()

# ৫. ভিজ্যুয়ালাইজেশন [cite: 72-93]
plt.figure(figsize=(14, 7))
plt.plot(time_cn, t2m_values, color="#B0C4DE", alpha=0.4, label='Hourly Temp')
plt.plot(df.index, df['moving_avg'], color="#E63946", linewidth=2, label='7-Day Moving Avg (Trend)')

# সর্বোচ্চ বিন্দু চিহ্নিত করা
plt.scatter(time_cn[max_idx], max_temp, color='red', s=100, edgecolors='black', zorder=5)
plt.annotate(f'Hottest: {max_temp:.1f}°C\n({time_cn[max_idx].strftime("%b %d")})',
             xy=(time_cn[max_idx], max_temp), xytext=(20, 10),
             textcoords='offset points', arrowprops=dict(arrowstyle='->', color='red'))

# সর্বনিম্ন বিন্দু চিহ্নিত করা
plt.scatter(time_cn[min_idx], min_temp, color='blue', s=100, edgecolors='black', zorder=5)
plt.annotate(f'Coldest: {min_temp:.1f}°C\n({time_cn[min_idx].strftime("%b %d")})',
             xy=(time_cn[min_idx], min_temp), xytext=(20, -30),
             textcoords='offset points', arrowprops=dict(arrowstyle='->', color='blue'))

# গ্রাফ সুন্দর করা [cite: 80-92]
plt.title("Nanjing 2021 Temperature Analysis: Extremes & Trends", fontsize=15, fontweight='bold')
plt.ylabel("Temperature (°C)", fontsize=12)
plt.xlabel("Month", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()

# ইমেজ সেভ করা [cite: 95]
plt.savefig("creative_temperature_analysis.png", dpi=300)
plt.show()

print(f"Hottest Day: {time_cn[max_idx]} with {max_temp:.2f}°C")
print(f"Coldest Day: {time_cn[min_idx]} with {min_temp:.2f}°C")