from ultralytics import YOLO
import cv2

model = YOLO('./best.pt') 

test_image_path = ["./data/processed/final_dataset/Blister Blight (Exobasidium vexans)/Blister_Blight_dt5_00052.jpg",
                   "./data/processed/final_dataset/Helopeltis (Helopeltis theivora)/Helopeltis_dt5_12635.jpg"]


results = model.predict(source=test_image_path, conf=0.25,boxes=False,save=True)


annotated_image = results[0].plot()


cv2.imshow("Tea Disease Detection", annotated_image)


cv2.waitKey(0)
cv2.destroyAllWindows()

print("Prediction finished!")