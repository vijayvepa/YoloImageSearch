from pathlib import Path
import json

def ensure_dir_exists(path):
	"""
	Ensure that a directory exists; if not, create it.
	"""
	dir_path = Path(path)
	processed_path = dir_path.parent.parent / "processed" / dir_path.name
	processed_path.mkdir(parents=True, exist_ok=True)
	return processed_path
  
def save_metadata(metadata, raw_path):
	"""
	Save metadata to a JSON file.
	"""
	processed_path  = ensure_dir_exists(raw_path)
	output_path = processed_path / "metadata.json"
	with open(output_path, 'w') as f:
		json.dump(metadata, f, indent=4)
	return output_path

def load_metadata(metadata_path):
	"""
	Load metadata from a JSON file.
	"""
	with open(metadata_path, 'r') as f:
		metadata = json.load(f)
	return metadata

	"""example json:
[
{
	"class": 0,
	"confidence": 0.85,
	"bbox": [x1, y1, x2, y2],
	"count": 3
},
{
	"class": 1,
	"confidence": 0.92,
	"bbox": [x1, y1, x2, y2],
	"count": 5
}		
]
	"""

def get_unique_classes(metadata):
	"""
	Get a set of unique classes from metadata.
	"""
	unique_classes = set() 
	count_options = {}

	for item in metadata:
		for det in item.get("detections", []):
			cls = det["class"]
			unique_classes.add(cls)
			if cls not in count_options:
				count_options[cls] = set()
			count_options[cls].add(det["count"])
		
	unique_classes = sorted(list(unique_classes))	
	for cls in count_options:
		count_options[cls] = sorted(list(count_options[cls]))
	return unique_classes, count_options