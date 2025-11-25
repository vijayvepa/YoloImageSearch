from ultralytics import YOLO
from pathlib import Path
import torch
from PIL import Image
import numpy as np
from src.config import load_config

class YOLOv11Inference:

		def __init__(self, model_name, device="cuda"):

			self.model = YOLO(model_name)
			self.model.to(device)
			self.device = device

			self.config = load_config()
			self.conf_threshold = self.config["model"]["conf_threshold"]
			self.extensions = self.config["data"]["image_extensions"]

		def process_image(self, image_path):
			results = self.model.predict(source=str(image_path), conf=self.conf_threshold, device=self.device, save=False)
			# process the results
			detections = []
			class_counts = {}
  
			for result in results:
				for box in result.boxes:
					cls = result.names[int(box.cls)]
					conf = float(box.conf)
					bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
					detections.append({
						"class": cls, # car
						"confidence": conf,
						"bbox": bbox,
						"count": 1
					})
					# Update class count
					class_counts[cls] = class_counts.get(cls, 0) + 1

			# Update counts in detections
			for det in detections:
				det['count'] = class_counts[det['class']]
    
			return {
				"image_path": str(image_path),
				"detections": detections,
				"total_objects": len(detections),
				"unique_class": list(class_counts.keys()), #[0,1,2]
				"class_counts": class_counts # {"car": 3, "person": 5}
			}
  
		def process_directory(self, directory):
			metadata = []
			patterns = [f"*{ext}" for ext in self.extensions]
			image_paths = []
			for pattern in patterns:
				image_paths.extend(Path(directory).glob(pattern))
			for img_path in image_paths:
				try:
					metadata.extend(self.process_image(img_path))
				except Exception as e:
					print(f"Error processing {img_path}: {e}")
					continue
			return metadata
  