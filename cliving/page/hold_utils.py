from ultralytics import YOLO
import numpy as np
import os
import json
from PIL import Image

def perform_object_detection(image_path):
    model = YOLO('../cliving/cliving_hold_weight.pt')

    image = Image.open(image_path)
    image_np = np.array(image)
    
    width, height = image.size

    results = model(image_np)   

    detected_objects = []
    if len(results) > 0 and len(results[0].boxes) > 0:
        for idx, result in enumerate(results[0].boxes):
            if result.cls == 0 and result.conf.item() >= 0.4:
                detected_objects.append({
                    "object_index": idx,
                    "confidence": result.conf.item(),
                    "box": result.xyxy.tolist()
                })

    return detected_objects, width, height

def save_detection_results(first_image_id, detections, output_dir='media/bbox'):
    from .models import Hold, FirstImage, Frame 
    
    first_image = FirstImage.objects.get(id=first_image_id)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    bbox_file_path = os.path.join(output_dir, f"{first_image.id}_bbox.json")
    with open(bbox_file_path, 'w') as bbox_file:
        json.dump(detections, bbox_file)
        
    frame = Frame.objects.first()
        
    for idx, detection in enumerate(detections):
        box = detection['box'][0]
        x1, y1, x2, y2 = box
        
        hold = Hold.objects.create(
            first_image=first_image,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            frame=frame
        )
        
        # hold.save()
    
    return bbox_file_path