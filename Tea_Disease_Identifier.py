import json

import torch
from ultralytics import YOLO
import cv2
import os
import numpy as np

class TeaDiseaseIdentifier:
    
    #params => weight path of the model, path of the image folder
    #this function initializes the model and the names of the classes
    def __init__(self,weight_path,imgPath):
        self.model = YOLO(weight_path)
        self.names = self.model.names
        self.imgPath=imgPath
        self.lower_green = np.array([25,40,40])
        self.upper_green = np.array([85,255,255])


    #params => mask in numpy 2D array format
    #this  function count the number of pixels in the mask that are greater than 0, 
    # which indicates the presence of the detected object in those pixels. 
    # The function returns the total count of such pixels.
    def count_pixels(self,mask):
        return int((mask > 0).sum())


    #params=> class id of class and pixel count of that class
    #this function creates a numpy array of zeros with the same length as the number of classes (len(names)). 
    # It then increments the value at the index corresponding to the class_id by the pixel_count.
    def pixel_adder(self,class_id,pixel_count):
        current=np.zeros((len(self.names)),dtype=int)
        current[class_id]+=pixel_count
        return current
    

    #param=> name of the image which is saved in the folder
    #this function takes an image name as input, constructs the path to the image, and uses the YOLO model to make predictions on the image.
    # returns an array pixel_count_arr to store the pixel counts for each class to find the infected area, the average confidence of the predictions, the lesion count, and a list of masks for each detected object.
    def predict(self,img):
        masks = []
        lesion_count = 0
        path = os.path.join(self.imgPath, img)
        results = self.model(source=path, conf=0.25)
        pixel_count_arr = np.zeros((len(self.names)), dtype=int)
        for result in results:
            infected_area_polgons = result.masks
            confident_list = result.boxes.conf.tolist()
            for raw_mask_id in range(infected_area_polgons.shape[0]):
                mask = infected_area_polgons[raw_mask_id].xy[0]
                conf = confident_list[raw_mask_id]
                raw_mask_numpy = infected_area_polgons[raw_mask_id].data.cpu().numpy()[0]
                class_id = int(result.boxes.cls[raw_mask_id])
                class_name = self.names[class_id]
                masks.append(self.save_pologon(class_name, conf, mask))
                lesion_count += self.lesion_counter(class_id)
                pixel_count_arr += self.pixel_adder(class_id, self.count_pixels(raw_mask_numpy))
        return pixel_count_arr, round((sum(confident_list) / len(confident_list)) * 100, 2), lesion_count, masks

    #params=>class_id
    #this function checks if the class name corresponding to the given class_id is not 'leaf'. If it is not 'leaf', 
    #  returns 1, indicating that it is a lesion. Otherwise, it returns 0, indicating that it is not a lesion. This function is used to count the number of lesions detected in the image.
    def lesion_counter(self,class_id):
        if self.names[class_id] != 'leaf':
            return 1
        return 0

    #params=> pixel count array of each class
    #this function calculates the percentage of infection for each class based on the pixel counts. 
    #It first calculates the total number of pixels by summing the pixel counts. If the total is zero, it returns 0 to avoid division by zero.
    def calculate_infection_percentage(self, pixel_count_arr):
        total_pixels = pixel_count_arr.sum()
        if total_pixels == 0:
            return 0,0,0
        pixel_count_arr[0]=0 #to ignore the healthy area
        pixel_count=pixel_count_arr.sum()
        infection_percentages = (pixel_count / total_pixels) * 100
        return total_pixels,pixel_count,np.round(infection_percentages,2)

    
    # params=> pixel count array of each class as numpy array
    # this function determines the disease name based on the pixel counts for each class. 
    # It first sets the pixel count for the healthy area (index 0) to zero to ignore it in the calculation.
    #theb it finds the index of the class with the highest pixel count using np.argmax and returns the corresponding class name from the names list. 
    # This function helps to identify the disease based on the area affected in the image.
    # returns the name of the disease corresponding to the class with the highest pixel count, 
    def get_disease_name(self,pixel_count_arr):
        pixel_count_arr[0]=0 #to ignore the healthy area
        disease_index = np.argmax(pixel_count_arr)
        return self.names[disease_index]


    # params=> class id, confidence of the prediction, mask of the detected object
    # this function creates a dictionary containing the class name, confidence, and mask of the detected
    # returns the dictionary with the class name, confidence, and mask of the detected object. This function is used to store the information about each detected object in a structured format.
    def save_pologon(self,class_id,confidence,mask):
        bbox_data={
            "class_id": class_id,
            "confidence": round(confidence, 4),
            "mask":mask
        }
        return bbox_data
    
    #param=> image file name
    #this function combines the previous functions to get both the disease name and the infection percentage for a given image. 
    # It first calls the predict function to get the pixel count array, then uses that array to determine the disease name and calculate the infection percentage. 
    # Finally, it returns both the disease name and the infection percentage as a tuple.
    def get_disease(self, img):
        pixel_count_arr,confident,lesion_count, masks= self.predict(img) # call to get the Yolo result.it returns mask as numpy array
        healthy_leaf_area,affected_area,infection_percentage = self.calculate_infection_percentage(pixel_count_arr)
        disease_name = self.get_disease_name(pixel_count_arr)
        severity_level=self.get_severity_level(infection_percentage)
        color_deviation=self.get_color_deviation(img)
        return {
            "disease_name":disease_name,
            "confident":confident,
            "infection_percentage":float(infection_percentage),
            "severity_level":severity_level,
            "healthy_leaf_area":healthy_leaf_area,
            "affected_area":affected_area,
            "lesion_count":lesion_count,
            "masks":masks,
            "color_deviation":color_deviation
        }
    
    #params=> infection percentage
    #this function categorizes the severity of the infection based on the percentage of infection.
    #returns "High" if the infection percentage is 75% or higher, "Medium" if it is between 25% and 75%, and "Low" if it is below 25%. This function helps to assess the severity of the disease based on the calculated infection percentage.
    def get_severity_level(self,infection_percentage):
        if infection_percentage >= 75:
            return "High"
        elif infection_percentage >= 25:
            return "Medium"
        else:
            return "Low"

    #params=> image file name
    #this function calculates the color deviation of the leaf in the image.
    # It reads the image, converts it to the HSV color space, and creates a mask to identify the healthy green areas of the leaf.
    # returns the color deviation
    def get_color_deviation(self, img):
        path=os.path.join(self.imgPath,img)
        image = cv2.imread(path)
        hsv  = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        #cv2.imshow('hsv', hsv)
        healthy_mask    = cv2.inRange(hsv, self.lower_green, self.upper_green)
        #cv2.imshow('healthy_mask', healthy_mask)
        healthy_pixels  = np.sum(healthy_mask > 0)
        total_pixels    = healthy_mask.size
        color_deviation = round(1 - (healthy_pixels / total_pixels), 3)
        return color_deviation
        

#instruction for get_disease function
#this function returns the disease name and infection percentage for a given image.
#use the get_disease function to get the disease name and infection percentage for a given image.
#when useing the get_disease function, the image name should be the name of the image file in the folder.
#must pass the image name as a string.

#instruction for get_severity_level function
#this function returns the severity level of the infection based on the infection percentage.
#use the get_severity_level function to get the severity level of the infection based on the infection percentage.
#when useing the get_severity_level function, the infection percentage should be the infection percentage returned by the get_disease function. 
#must pass the infection percentage as a float.


# teaDiseaseIdentifier=TeaDiseaseIdentifier('./tea_disease_identifier_weight.pt','./data/processed/final_dataset/Blister Blight (Exobasidium vexans)')
# result=teaDiseaseIdentifier.get_disease('Blister_Blight_dt5_00147.jpg')
# #result.pop('masks')
# #print(result)
# for mask in result['masks']:
#     print(mask['mask'])
#     break


