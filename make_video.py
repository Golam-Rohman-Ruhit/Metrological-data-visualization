import cv2
import os
import re


def create_video_from_images(image_folder, video_name, fps=5):
    # 1. Folder check kora
    if not os.path.exists(image_folder):
        print(f"Error: Folder '{image_folder}' pawa jacche na!")
        return

    # 2. Image gula khuje ber kora (.jpg ba .png)
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".png")]

    # 3. Image gula ke number onujayi sort kora (Frame 1, Frame 2... Frame 10...)
    # Sort na korle video elomelohobe (jemon 1 er por 10 chole ashbe)
    try:
        images.sort(key=lambda f: int(re.sub('\D', '', f)))
    except:
        print("Warning: Filename e number nai, normal sort kora hocche.")
        images.sort()

    if not images:
        print(f"Error: '{image_folder}' folder e kono image nai.")
        return

    print(f"Mot {len(images)} ti image pawa geche. Video banano shuru hocche...")

    # 4. First image theke height ar width neya
    frame_path = os.path.join(image_folder, images[0])
    frame = cv2.imread(frame_path)
    height, width, layers = frame.shape

    # 5. Video Writer setup kora (MP4 format)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

    # 6. Loop chalaye video write kora
    for image in images:
        img_path = os.path.join(image_folder, image)
        frame = cv2.imread(img_path)
        video.write(frame)

    # 7. Release memory
    cv2.destroyAllWindows()
    video.release()
    print(f"Success! Video save hoyeche: {video_name}")


# ==========================================
# Settings (Tomar File Structure Onujayi)
# ==========================================

# Tomar screenshot onujayi image gula ei folder e thakar kotha:
input_folder = 'Innovation_IMGs'

# Output video er nam:
output_video_name = 'Typhoon_Doksuri_Animation.mp4'

# FPS (Speed):
# 5 mane protite second e 5 ta frame dekhabe. Slow chaile 2 dao, fast chaile 10 dao.
frames_per_second = 5

# Function call
if __name__ == "__main__":
    create_video_from_images(input_folder, output_video_name, frames_per_second)