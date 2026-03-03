import torch
from ultralytics import YOLO
import cv2
import os
import numpy as np

class TeaDiseaseIdentifier:
    #params => weight path of the model
    #this function initializes the model and the names of the classes
    def __init__(self,weight_path,imgPath):
        self.model = YOLO(weight_path)
        self.names = self.model.names
        self.imgPath=imgPath;


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
    # It initializes an array pixel_count_arr to store the pixel counts for each class to find thr infected area.
    def predict(self,img):
        path=os.path.join(self.imgPath,img)
        results = self.model(source=path,conf=0.25)
        #annotated_image = results[0].plot()
        #print('result.masks', (results[0].masks).shape)
        pixel_count_arr=np.zeros((len(self.names)),dtype=int)
        for result in results:
            infected_area_polgons=result.masks
            #print('infected_area_polgons', infected_area_polgons.shape)
            #print('infected_area_polgons', infected_area_polgons.shape[0])
            for raw_mask_id in range(infected_area_polgons.shape[0]):
                raw_mask_numpy = infected_area_polgons[raw_mask_id].data.cpu().numpy()[0]
                #print('raw_mask_numpy', raw_mask_numpy.shape)
                #print(raw_mask_id)
                class_id=int(result.boxes.cls[raw_mask_id])
                pixel_count_arr+=self.pixel_adder(class_id,self.count_pixels(raw_mask_numpy))
        return pixel_count_arr
    
    #params=> pixel count array of each class
    #this function calculates the percentage of infection for each class based on the pixel counts. 
    #It first calculates the total number of pixels by summing the pixel counts. If the total is zero, it returns 0 to avoid division by zero.
    def claculate_infection_percentage(self, pixel_count_arr):
        total_pixels = pixel_count_arr.sum()
        if total_pixels == 0:
            return 0
        pixel_count_arr[0]=0 #to ignore the healthy area
        pixel_count=pixel_count_arr.sum()
        infection_percentages = (pixel_count / total_pixels) * 100
        return np.round(infection_percentages,2)

    
    #params=> pixel count array of each class as numpy array
    #this function determines the disease name based on the pixel counts for each class.
    def get_disease_name(self,pixel_count_arr):
        pixel_count_arr[0]=0 #to ignore the healthy area
        disease_index = np.argmax(pixel_count_arr)
        return self.names[disease_index]
    
    #param=> image file name
    #this function combines the previous functions to get both the disease name and the infection percentage for a given image. 
    # It first calls the predict function to get the pixel count array, then uses that array to determine the disease name and calculate the infection percentage. 
    # Finally, it returns both the disease name and the infection percentage as a tuple.
    def get_disease(self, img):
        pixel_count_arr = self.predict(img) # call to get the Yolo result.it returns mask as numpy array
        infection_percentage = self.claculate_infection_percentage(pixel_count_arr)
        disease_name = self.get_disease_name(pixel_count_arr)
        return disease_name, float(infection_percentage)
    
    #params=> infection percentage
    #this function categorizes the severity of the infection based on the percentage of infection.
    def get_severity_level(self,infection_percentage):
        if infection_percentage >= 75:
            return "High"
        elif infection_percentage >= 25:
            return "Medium"
        else:
            return "Low"

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


teaDiseaseIdentifier=TeaDiseaseIdentifier('./tea_disease_identifier_weight.pt','./data/processed/final_dataset/Blister Blight (Exobasidium vexans)')
result=teaDiseaseIdentifier.get_disease('Blister_Blight_dt5_00147.jpg')
print(result)
print(teaDiseaseIdentifier.get_severity_level(result[1]))


