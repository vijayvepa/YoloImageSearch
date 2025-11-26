import traceback
import streamlit as st
#import sys 
from pathlib import Path
import time
from src.inference import YOLOv11Inference
from src.utils import get_unique_classes, save_metadata, load_metadata
import tempfile
# add src to path
#sys.path.append(str(Path(__file__).parent))

def init_session_state():
		"""
		## Store Session Defaults in Streamlit Session State
	"""
		session_defaults = {
			"image_dir": "path",
			"metadata": None,
			"unique_classes": [],
			"count_options": {}
		}
		for key, value in session_defaults.items():
			if key not in st.session_state:
				st.session_state[key] = value
  
def layout_process_new_images():
	"""
		## Process New Images (Layout)
	"""
	with st.expander("Process New Images", expanded=True):
		col1,col2 = st.columns(2)
		# Placeholder for image processing logic
		with col1:
			image_dir = st.text_input("Enter Image Directory", placeholder="path/to/images")
		with col2:
			uploaded_model = st.file_uploader("Upload Model Weights (.pt)", type=["pt"])
			model_path = None
			if uploaded_model is not None:
				tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pt")
				tmp_file.write(uploaded_model.getbuffer())
				tmp_file.flush()
				tmp_file.close()
				model_path = tmp_file.name
		start_inference = st.button("Start Inference")
		if start_inference:
			if image_dir:
				st.spinner("Processing images...")
				
				try:
					metadata, metadata_path = api_process_images(image_dir, model_path=model_path)
					unique_classes, count_options = get_unique_classes(metadata)

					st.success(f"Processed {len(metadata)} images,  metadata saved")
					st.code(f"Metadata Path: {metadata_path}")
					st.code(f"Unique Classes: {unique_classes}")
					st.code(f"Count Options: {count_options}")

					st.session_state.metadata = metadata
					st.session_state.unique_classes = unique_classes
					st.session_state.count_options = count_options
				except Exception as e:
					st.error(f"Unable to process images: {str(e)}")
					st.code(traceback.format_exc())
					st.code(e)
				
			else:
				st.warning("Please provide a valid image directory.")
		
def api_process_images(image_dir, model_path="yolollm.pt"):
  """
	## Process New Images (API)
  """
  inference = YOLOv11Inference(model_path)
  metadata = inference.process_directory(image_dir)
  metadata_path = save_metadata(metadata, image_dir)
  return metadata, metadata_path


def layout_load_existing_metadata():
	with st.expander("Load Existing Metadata", expanded=True):
		# Placeholder for loading metadata logic
		metadata_path = st.file_uploader("Upload Metadata File", type=["json"])
		if metadata_path:
			metadata_path = metadata_path.name
		load_metadata_button = st.button("Load Metadata")
		if load_metadata_button:
			if metadata_path:
				st.spinner("Loading metadata...")
				
				try:
					metadata = load_metadata(metadata_path)
					unique_classes, count_options = get_unique_classes(metadata)

					st.success(f"Found {len(metadata)} images,  metadata loaded")
					st.code(f"Metadata Path: {metadata_path}")
					st.code(f"Unique Classes: {unique_classes}")
					st.code(f"Count Options: {count_options}")

					st.session_state.metadata = metadata
					st.session_state.unique_classes = unique_classes
				except Exception as e:
					st.error(f"Error Loading Metadata: {e}")
					st.code(traceback.format_exc())
					st.error(f"Error Loading Metadata: {e}")
				
			else:
				st.warning("Please provide a valid metadata file path.")
			# Further processing logic would go here
def api_load_metadata(metadata_path):
	"""
	## Load Existing Metadata (API)
	"""
	time.sleep(3)

init_session_state()
st.set_page_config(page_title="YOLOv11 Image Processing", page_icon="⚙️", layout="wide")
st.title("Computer Vision Powered Image Processing")

# Main Options
main_option = st.radio("Select an option:", ("Process New Images", "Load Existing Metadata"), key="main_option")

if main_option == "Process New Images":
		layout_process_new_images()
		
elif main_option == "Load Existing Metadata":
		layout_load_existing_metadata()