import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import netCDF4 as nc
import numpy as np
from PIL import Image
import os
from matplotlib import image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Rectangle
import matplotlib.ticker as ticker
from matplotlib.patches import Circle

from matplotlib.ticker import FuncFormatter
import matplotlib
matplotlib.use('TkAgg')  # 使用Agg后端以避免图形显示问题


# 定义一个函数，将刻度值除以100
def scale_y_tick(x, pos):
    return f"{int(x / 100)}"

def detect_low_pressure_center(msl_data, pressure_threshold):
    min_val = np.min(msl_data)
    min_idx = np.unravel_index(np.argmin(msl_data), msl_data.shape)
    return min_val, min_idx

def resize_image(image_path, size):
    with Image.open(image_path) as img:
        resized_img = img.resize(size, Image.Resampling.LANCZOS)  # 修改这里
        resized_img.save(image_path)

def convert_era5_time_to_datetime(time_array):
    start_date = datetime.datetime(1970, 1, 1)  # Unix时间戳起点
    return [start_date + datetime.timedelta(seconds=int(time)) for time in time_array]

# 设置Matplotlib以支持中文
# mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.sans-serif'] = ['Times New Roman']
mpl.rcParams['axes.unicode_minus'] = False

file_path = 'mean_sea_level_pressure.nc'  # 实际NetCDF文件路径
weather_icon_path = 'panel.png'  # 实际天气图标路径
icon_img = plt.imread(weather_icon_path)

ds = nc.Dataset(file_path)
longitude = ds.variables['longitude'][:]
latitude = ds.variables['latitude'][:]
time = ds.variables['valid_time'][:]
msl = ds.variables['msl'][:]

ds.close()

converted_times = convert_era5_time_to_datetime(time)
pressure_threshold = 99970
mslp_min = np.min(msl)
mslp_max = np.max(msl)

proj = ccrs.PlateCarree()  # 设置地图投影
cmap = mpl.cm.jet  # 使用更鲜艳的颜色图
norm = mpl.colors.Normalize(vmin=mslp_min, vmax=mslp_max)
extent = [100, 150, 0, 50]

image_dir = 'IMGs'
os.makedirs(image_dir, exist_ok=True)

icon_zoom = 0.035  # 调整图标大小
rect_width = 13  # 调整矩形宽度
rect_height = 1.75  # 调整矩形高度
rect_offset = 0.5  # 调整矩形位置

target_size = (1138, 1052)  # 调整目标图片尺寸
# 定义新的颜色和透明度
line_color = (68/255, 65/255, 65/255, 0.84)  # RGBA格式 rgba(68, 65, 65, 0.84)
# 创建ScalarMappable对象用于映射颜色
scalar_map = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
scalar_map.set_array([])
for i, time_i in enumerate(converted_times[:]):
    # 设置画布大小
    fig, ax = plt.subplots(figsize=(16, 12), subplot_kw={'projection': proj})

    ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    # 设置刻度标签颜色为黑色
    ax.tick_params(colors='black', which='both')  # 刻度和刻度标签
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'color': 'black'}  # 经度标签颜色
    gl.ylabel_style = {'color': 'black'}  # 纬度标签颜色

    lon_indices = np.searchsorted(longitude, [extent[0], extent[1]])
    lat_indices = np.searchsorted(latitude, [extent[2], extent[3]])
    msl_data = msl[i, lat_indices[0]:lat_indices[1], lon_indices[0]:lon_indices[1]]
    # 获取颜色数据
    msl_colors = cmap(norm(msl_data))

    # 绘制msl数据，并设置透明度为0.7
    ax.pcolormesh(longitude, latitude, msl_data, cmap=cmap, norm=norm, transform=ccrs.PlateCarree(), alpha=0.7)
    msl_plot = ax.pcolormesh(longitude, latitude, msl_data, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm)


    min_val, (lat_idx, lon_idx) = detect_low_pressure_center(msl_data, pressure_threshold)
    min_lat = latitude[lat_idx]
    min_lon = longitude[lon_idx]

    # 在添加矩形之前获取当前坐标轴的视觉范围
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # 绘制竖直线
    pole_length = 5
    ax.plot([min_lon+0.05, min_lon+0.05], [min_lat, min_lat + pole_length], color=line_color, linewidth=2,
            transform=ccrs.PlateCarree(), zorder=5)

    # 在低压中心绘制一个小白圆点
    circle_radius = 0.2  # 调整圆点半径大小
    white_circle = Circle((min_lon+0.07, min_lat), circle_radius, color='white', transform=ccrs.PlateCarree(), zorder=10)
    ax.add_patch(white_circle)

    # 绘制矩形区域，确保与竖直线紧挨
    flag_rect = Rectangle((min_lon, min_lat + pole_length), rect_width, rect_height,
                          color=line_color, zorder=6, transform=ccrs.PlateCarree())
    ax.add_patch(flag_rect)

    # 添加图标和文本
    icon = OffsetImage(icon_img, zoom=icon_zoom)
    icon_box = AnnotationBbox(icon, (min_lon + rect_width / 12, min_lat + pole_length + rect_height / 2),
                              frameon=False, boxcoords="data", pad=0, zorder=10)
    ax.add_artist(icon_box)
    min_val = int(min_val / 100)
    ax.text(min_lon + 5.5 * rect_width / 10, min_lat + pole_length + rect_height / 2, f'{min_val}hPa Typhoon Dussuri',
            verticalalignment='center', horizontalalignment='center', fontsize=13, weight='bold', color='white',
            transform=ccrs.PlateCarree(), zorder=10)

    # 在添加了图形元素后，重置坐标轴的视觉范围
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # 添加色标并设置刻度和标题颜色为白色
    cbar = plt.colorbar(msl_plot, orientation='vertical', pad=0.02, aspect=50)
    cbar.set_label('Mean Sea Level Pressure(hPa)', color='black')
    cbar.ax.yaxis.set_tick_params(color='black')  # 设置色标刻度标签颜色
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(scale_y_tick))  # 应用自定义刻度格式化

    # 单独设置色标刻度值颜色为白色
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='black')

    title_text = f"Mean Sea Level Pressure at Time: {time_i}"
    ax.set_title(title_text, pad=20, fontsize=25, color='black')

    # 在所有绘图操作后重新设置轴的显示范围
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    # 保存图片和关闭图形
    current_image_path = os.path.join(image_dir, f'{i}.jpg')
    plt.savefig(current_image_path, bbox_inches='tight', transparent=False)
    resize_image(current_image_path, target_size)
    plt.close(fig)
    print(f'{i}.jpg saved')
print(f"All frames have been saved to {image_dir}.")