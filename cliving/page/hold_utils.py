from ultralytics import YOLO
import numpy as np
import os
import json
from PIL import Image

def perform_object_detection(image_path):
    model = YOLO('../cliving/cliving_hold_weight.pt')

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

def save_detection_results(image_id, detections, output_dir='media/bbox'):
    from .models import Hold, FirstImage, Frame
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    bbox_file_path = os.path.join(output_dir, f"{image_id}_bbox.json")
    with open(bbox_file_path, 'w') as bbox_file:
        json.dump(detections, bbox_file)
        
    for detection in detections:
        x1, y1, x2, y2 = detection['box'][0]

        first_image = FirstImage.objects.create(image_id=image_id)
        
        hold = Hold.objects.create(
            x1=x1, y1=y1, x2=x2, y2=y2,
            frame_id=first_image
        )