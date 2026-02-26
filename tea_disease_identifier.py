from ultralytics import YOLO
import cv2
import numpy as np
import os

model = YOLO('./best.pt')

def predict(img):
    path=os.path.join('./uploaded images', img)
    print(f"Processing image: {path}")
    if os.path.exists(path):
        results = model(path)
        return results
    else:
        return None




def calculate_severity(results):
    # result[0] is the current image processing result
    res = results[0]

    if res.masks is None:
        return 0, 0, 0

    # Initialize pixel counts
    total_leaf_pixels = 0
    total_infected_pixels = 0

    # Loop through detections to separate leaf and disease
    for i, mask in enumerate(res.masks.data):
        cls_id = int(res.boxes.cls[i])
        label = res.names[cls_id]

        # Calculate pixel count for this specific mask
        mask_array = mask.cpu().numpy()
        pixel_count = np.sum(mask_array > 0.5)  # Binary threshold

        if label == "leaf":  # Assuming your class name for the leaf is 'leaf'
            total_leaf_pixels += pixel_count
        elif label == "blister_blight":
            total_infected_pixels += pixel_count

    # Calculate percentage
    if total_leaf_pixels > 0:
        severity_percentage = (total_infected_pixels / total_leaf_pixels) * 100
    else:
        severity_percentage = 0

    return total_leaf_pixels, total_infected_pixels, round(severity_percentage, 2)

