import streamlit as st
import sys 
from pathlib import Path
import time

# add src to path
sys.path.append(str(Path(__file__).parent))

def init_session_state():
		"""
		## Store Session Defaults in Streamlit Session State
	"""
		session_defaults = {
			"image_dir": "path"
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
			model_path = st.text_input("Model Weights Directory", "yolollm.pt")
		start_inference = st.button("Start Inference")
		if start_inference:
			if image_dir:
				st.spinner("Processing images...")
				
				try:
					api_process_images(image_dir)
					st.success("Image processing completed successfully!")
				except Exception as e:
					st.error(f"An error occurred: {e}")
				
			else:
				st.warning("Please provide a valid image directory.")
		
def api_process_images(image_dir):
  """
	## Process New Images (API)
  """
  time.sleep(5)
    # Placeholder for image processing logic
  # Further processing logic would go here

def layout_load_existing_metadata():
	with st.expander("Load Existing Metadata", expanded=True):
		# Placeholder for loading metadata logic
		metadata_path = st.file_uploader("Upload Metadata File", type=["json"])
		if metadata_path:
			metadata_path = metadata_path.name
		load_metadata = st.button("Load Metadata")
		if load_metadata:
			if metadata_path:
				st.spinner("Loading metadata...")
				
				try:
					api_load_metadata(metadata_path)
					st.success("Metadata loaded successfully!")
				except Exception as e:
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