import torch
from ultralytics import YOLO
import cv2
import os
import numpy as np


#params => mask in numpy 2D array format
#this  function count the number of pixels in the mask that are greater than 0, 
# which indicates the presence of the detected object in those pixels. 
# The function returns the total count of such pixels.
def count_pixels(mask):
    return int((mask > 0).sum())


#params=> class id of class and pixel count of that class
#this function creates a numpy array of zeros with the same length as the number of classes (len(names)). 
# It then increments the value at the index corresponding to the class_id by the pixel_count.
def pixel_adder(class_id,pixel_count):
    #print('class_id', class_id)
    #print('pixel_count', pixel_count)
    current=np.zeros((len(names)),dtype=int)
    current[class_id]+=pixel_count
    return current


#param=> saved image name in uploaded_images folder
#this function takes an image name as input, constructs the path to the image, and uses the YOLO model to make predictions on the image.
# It initializes an array pixel_count_arr to store the pixel counts for each class to find thr infected area.
def predict(img):
    path=os.path.join('./uploaded_images',img)

    results = model(source=path,conf=0.25)

    #annotated_image = results[0].plot()
    #print('result.masks', (results[0].masks).shape)

    pixel_count_arr=np.zeros((len(names)),dtype=int)

    for result in results:

        infected_area_polgons=result.masks
        #print('infected_area_polgons', infected_area_polgons.shape)
        #print('infected_area_polgons', infected_area_polgons.shape[0])
        for raw_mask_id in range(infected_area_polgons.shape[0]):
            raw_mask_numpy = infected_area_polgons[raw_mask_id].data.cpu().numpy()[0]
            #print('raw_mask_numpy', raw_mask_numpy.shape)
            #print(raw_mask_id)
            #cv2.imshow("Tea Disease Detection", annotated_image)

            class_id=int(result.boxes.cls[raw_mask_id])
            pixel_count_arr+=pixel_adder(class_id,count_pixels(raw_mask_numpy))

            #cv2.imshow(f"Infected Area Mask {names[class_id]}", raw_mask_numpy * 255) # Multiply by 255 to visualize the mask
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

    return pixel_count_arr

#params=> pixel count array of each class
#this function calculates the percentage of infection for each class based on the pixel counts. 
#It first calculates the total number of pixels by summing the pixel counts. If the total is zero, it returns 0 to avoid division by zero.
def claculate_infection_percentage(pixel_count_arr):
    #print(pixel_count_arr)
    total_pixels = pixel_count_arr.sum()
    if total_pixels == 0:
        return 0
    pixel_count_arr[0]=0 #to ignore the healthy area
    pixel_count=pixel_count_arr.sum()
    infection_percentages = (pixel_count / total_pixels) * 100
    return infection_percentages





model = YOLO("best.pt") 
names = model.names #names is a list of class names corresponding to the class IDs used in the model.

#print(predict('Blister_Blight_dt3_00119.jpg'))
print(claculate_infection_percentage(predict('Blister_Blight_dt3_00119.jpg')))
#print(predict('Blister_Blight_dt3_00132.jpg'))