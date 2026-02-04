import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os


# ১. ইনোভেশন ফাংশন: টাইফুন ক্লাসিফিকেশন (Rule-based AI)
def classify_typhoon(pressure):
    if pressure < 930:
        return "Super Typhoon (Cat 5)"
    elif 930 <= pressure < 960:
        return "Severe Typhoon (Cat 3-4)"
    elif 960 <= pressure < 980:
        return "Typhoon (Cat 1-2)"
    elif 980 <= pressure < 995:
        return "Tropical Storm"
    else:
        return "Tropical Depression"


# ২. ইনোভেশন ফাংশন: ইমপ্যাক্ট জোন (Radius) ক্যালকুলেশন
def calculate_impact_area(msl_data, threshold=1000):
    # কতটি গ্রিড পয়েন্টে বায়ুচাপ threshold এর নিচে আছে তা গণনা
    affected_points = np.sum(msl_data < threshold)
    return affected_points * 25  # আনুমানিক এলাকা (প্রতি গ্রিড ২৫ বর্গ কিমি ধরে)


# ডেটা লোড
file_path = 'mean_sea_level_pressure.nc'
ds = nc.Dataset(file_path)
msl = ds.variables['msl'][:] / 100
lon, lat = ds.variables['longitude'][:], ds.variables['latitude'][:]

output_dir = 'Innovation_IMGs'
os.makedirs(output_dir, exist_ok=True)

for i in range(len(msl)):
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([110, 150, 15, 45])
    ax.add_feature(cfeature.COASTLINE)

    # কেন্দ্র শনাক্তকরণ (Teacher's Method)
    msl_frame = msl[i, :, :]
    min_val = np.min(msl_frame)
    min_idx = np.unravel_index(np.argmin(msl_frame), msl_frame.shape)

    # --- INNOVATION SECTION ---
    category = classify_typhoon(min_val)
    impact_area = calculate_impact_area(msl_frame)

    # ডাইনামিক অ্যানোটেশন [cite: 250-254]
    info_text = (f"Status: {category}\n"
                 f"Central Pressure: {int(min_val)} hPa\n"
                 f"Est. Impact Area: {int(impact_area)} sq km")

    # ম্যাপে প্লট করা
    plt.contourf(lon, lat, msl_frame, cmap='RdYlBu_r', alpha=0.6)
    plt.scatter(lon[min_idx[1]], lat[min_idx[0]], color='black', marker='x', s=100)

    # টেক্সট বক্স যোগ করা (Innovation Chapter-এর জন্য ভিজ্যুয়াল প্রুফ)
    plt.text(112, 17, info_text, bbox=dict(facecolor='white', alpha=0.8), transform=ccrs.PlateCarree())
    plt.title(f"Typhoon Doksuri Intelligent Analysis - Frame {i}")

    plt.savefig(f"{output_dir}/{i}.jpg")
    plt.close()
    print(f"Innovative Analysis Frame {i} done.")