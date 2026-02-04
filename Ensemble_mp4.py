import cv2
import os
from tqdm import tqdm


def images_to_video(img_dir, output_path, fps=24):
    """
    将图片序列合成为视频
    :param img_dir: 图片目录（如'IMGs'）
    :param output_path: 输出视频路径（如'output.mp4'）
    :param fps: 帧率（默认24帧/秒）
    """
    # 获取图片列表并按数字排序
    img_files = sorted(
        [f for f in os.listdir(img_dir) if f.endswith('.jpg')],
        key=lambda x: int(x.split('.')[0])
    )

    if not img_files:
        raise ValueError(f"No jpg images found in {img_dir}")

    # 读取第一张图片获取尺寸
    first_img = cv2.imread(os.path.join(img_dir, img_files[0]))
    height, width, _ = first_img.shape

    # 创建视频写入器（MP4格式）
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 或使用'avc1'
    video_writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    # 逐帧写入（带进度条）
    for img_file in tqdm(img_files, desc='Creating video'):
        img_path = os.path.join(img_dir, img_file)
        frame = cv2.imread(img_path)
        video_writer.write(frame)

    video_writer.release()
    print(f"Video saved to {output_path}")


# 使用示例
if __name__ == "__main__":
    images_to_video(
        img_dir='IMGs',
        output_path='typhoon_track.mp4',
        fps=10  # 气象数据通常用较低帧率
    )