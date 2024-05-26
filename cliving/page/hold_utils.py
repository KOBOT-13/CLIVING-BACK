from ultralytics import YOLO
import numpy as np
from PIL import Image

def perform_object_detection(image_path):
    model = YOLO('cliving-back/cliving/cliving_hold_weight_yolov8.pt')

    image_np = np.array(Image.open(image_path))

    results = model(image_np)

    detected_objects = []
    for idx, result in enumerate(results[0].boxes):
        detected_objects.append({
            "object_index": idx,
            "confidence": result.conf.item(),
            "box": result.xyxy.tolist()
        })

    return detected_objects

