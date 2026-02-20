from ultralytics import YOLO
import cv2

model = YOLO('best.pt') 

test_image_path = ["./data/processed/final_dataset/Blister Blight (Exobasidium vexans)/Blister_Blight_dt5_00052.jpg",
                   "./data/processed/final_dataset/Helopeltis (Helopeltis theivora)/Helopeltis_dt5_12635.jpg"]


results = model.predict(source=test_image_path, conf=0.25,boxes=False,save=True)

# 4. Extract the image array with the polygons perfectly drawn on it
annotated_image = results[0].plot()

# 5. Give the image manually to OpenCV to display
cv2.imshow("Tea Disease Detection", annotated_image)

# 6. Because OpenCV is in control now, this will successfully freeze the window!
cv2.waitKey(0)
cv2.destroyAllWindows()

print("Prediction finished!")