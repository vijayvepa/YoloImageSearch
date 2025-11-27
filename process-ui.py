import traceback
import streamlit as st

# import sys
from pathlib import Path
import time
from src.inference import YOLOv11Inference
from src.utils import get_unique_classes, save_metadata, load_metadata
import tempfile
from typing import Optional
import zipfile
import shutil
import os

# add src to path
# sys.path.append(str(Path(__file__).parent))


def init_session_state():
    """
    ## Store Session Defaults in Streamlit Session State
    """
    session_defaults = {
        "image_dir": "path",
        "metadata": None,
        "unique_classes": [],
        "count_options": {},
        "search_parameters": {
            "search_mode": "Any of the selected classes (OR)",
            "selected_classes": [],
            "thresholds": {},
        },
        "search_results": [],
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_uploaded_tempfile(uploaded_file, suffix: str) -> Optional[str]:
    """Save a Streamlit uploaded file to a temporary file and return its path.

    Args:
            uploaded_file: The object returned by `st.file_uploader`.
            suffix: File suffix (including dot), e.g. '.pt' or '.json'.

    Returns:
            The filesystem path to the temporary file, or None if no file provided.
    """
    if uploaded_file is None:
        return None
    # Create a named temporary file and write the uploaded buffer to disk
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_file.write(uploaded_file.getbuffer())
    tmp_file.flush()
    tmp_file.close()
    return tmp_file.name


def start_inference(zip_path: str, model_path: Optional[str]):
    """Extract a ZIP file, process images in the extracted folder, cleanup and
    return (metadata, metadata_path).

    Args:
        zip_path: Path to the uploaded ZIP file on disk.
        model_path: Optional path to a model weights file.

    Returns:
        Tuple (metadata, metadata_path) on success, or (None, None) on failure.
    """
    if not zip_path:
        st.warning("No ZIP file provided to start_inference.")
        return None, None
    if not model_path:
        st.warning(
            "Model weights pyTorch file needed. Download from [Yolo11m.pt](https://huggingface.co/Ultralytics/YOLO11/blob/main/yolo11m.pt)."
        )
        return None, None

    extract_dir = tempfile.mkdtemp()
    metadata = None
    metadata_path = None
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        metadata, metadata_path = api_process_images(extract_dir, model_path=model_path)

    except Exception as e:
        st.error(f"Unable to extract/process ZIP: {e}")
        st.code(traceback.format_exc())
        metadata = None
        metadata_path = None

    finally:
        # Cleanup extracted files and uploaded zip file
        try:
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
        except Exception:
            pass
        try:
            if zip_path and os.path.exists(zip_path):
                os.remove(zip_path)
        except Exception:
            pass

    return metadata, metadata_path


def layout_process_new_images():
    """
    ## Process New Images (Layout)
    """
    with st.expander("Process New Images", expanded=True):
        col1, col2 = st.columns(2)
        # Placeholder for image processing logic
        with col1:
            # Instead of supplying a folder path, the UI now accepts a ZIP
            # containing images. The ZIP will be extracted and processed.
            uploaded_zip = st.file_uploader("Upload Images ZIP", type=["zip"])
            image_dir = None
            if uploaded_zip is not None:
                # Save uploaded zip to a temporary file
                zip_path = save_uploaded_tempfile(uploaded_zip, suffix=".zip")
                image_dir = None
        with col2:
            uploaded_model = st.file_uploader("Upload Model Weights (.pt)", type=["pt"])
            model_path = save_uploaded_tempfile(uploaded_model, suffix=".pt")
        start_inference_button = st.button("Start Inference")
        if start_inference_button:
            if uploaded_zip is not None and zip_path is not None:
                with st.spinner("Processing images..."):
                    metadata, metadata_path = start_inference(zip_path, model_path)

                # If metadata is None, an error was already shown inside start_inference
                if metadata is not None:
                    unique_classes, count_options = get_unique_classes(metadata)

                    st.success(f"Processed {len(metadata)} images,  metadata saved")
                    st.code(f"Metadata Path: {metadata_path}")
                    st.code(f"Unique Classes: {unique_classes}")
                    st.code(f"Count Options: {count_options}")

                    st.session_state.metadata = metadata
                    st.session_state.unique_classes = unique_classes
                    st.session_state.count_options = count_options

            else:
                st.warning("Please upload a ZIP file containing images.")


def api_process_images(image_dir, model_path):
    """
    ## Process New Images (API)
    """
    inference = YOLOv11Inference(model_path)

    # Collect image paths using the inference helper so extensions stay in sync
    image_paths = inference.list_image_paths(image_dir)

    total = len(image_paths)
    if total == 0:
        st.warning("No images found in the provided directory.")
        return [], None

    progress_bar = st.progress(0)
    status_text = st.empty()

    metadata = []
    for idx, img_path in enumerate(image_paths, start=1):
        try:
            md = inference.process_image(img_path)
            metadata.append(md)
        except Exception as e:
            # show the error but continue processing remaining images
            st.error(f"Error processing {img_path}: {e}")
            continue

        pct = int((idx / total) * 100)
        progress_bar.progress(pct)
        image_name = Path(img_path).name
        status_text.text(f"Processing {image_name} - {idx}/{total} ({pct}%)")

    # finalize UI
    progress_bar.progress(100)
    status_text.text("Completed")

    metadata_path = save_metadata(metadata, image_dir)
    return metadata, metadata_path


def layout_load_existing_metadata():
    with st.expander("Load Existing Metadata", expanded=True):
        # Placeholder for loading metadata logic
        uploaded_model = st.file_uploader("Upload Metadata File", type=["json"])

        metadata_path = save_uploaded_tempfile(uploaded_model, suffix=".json")
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
                    st.session_state.count_options = count_options
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

def api_search_images(search_parameters,metadata):
		"""
		## Search Images (API)
		"""
		results = []
		for item in metadata:
			matches = False
			class_matches = {}
			for cls in search_parameters["selected_classes"]:
				class_detections = [det for det in item.get("detections", []) if det["class"] == cls]
				class_count = len(class_detections)
				class_matches[cls] = False
				threshold = search_parameters["thresholds"].get(cls, "None")
				if threshold == "None":
					if class_count >= 1:
						class_matches[cls] = True
				else:
					if class_count <= int(threshold):
						class_matches[cls] = True
			if search_parameters["search_mode"] == "Any of the selected classes (OR)":
				if any(class_matches.values()):
					matches = True
			else:  # All of the selected classes (AND)
				if all(class_matches.values()):
					matches = True
			if matches:
				results.append(item)
		st.session_state.search_results = results
		st.code(results)
  
def layout_search_images():
    """
    ## Search Images Layout
    """
    # Header with search icon
    st.header("🔎 Search Images")
    with st.container():
      search_mode = st.radio("Search Mode:", ("Any of the selected classes (OR)", "All of the selected classes (AND)"), key="search_mode", horizontal=True)
      classes_to_search = st.multiselect("Classes to Search:", options=st.session_state.unique_classes, key="selected_classes")
      
      thresholds = {}
      if classes_to_search is not None and len(classes_to_search) > 0:
        st.subheader("Count Thresholds (optional)")
        cols = st.columns(len(classes_to_search))
        for i, cls in enumerate(classes_to_search):
          with cols[i]:
            threshold = st.selectbox(f"Max Count for {cls}", options=["None"] + st.session_state.count_options[cls], key=f"threshold_{cls}")
            thresholds[cls] = threshold
      st.session_state.search_parameters["search_mode"] = search_mode
      st.session_state.search_parameters["selected_classes"] = classes_to_search
      st.session_state.search_parameters["thresholds"] = thresholds
    
    search_button = st.button("Search Images", type="primary")
    if search_button and classes_to_search:
      api_search_images(st.session_state.search_parameters, st.session_state.metadata)# Implement search logic here

init_session_state()
st.set_page_config(page_title="YOLOv11 Image Processing", page_icon="⚙️", layout="wide")
st.title("Computer Vision Powered Image Processing")

# Main Options
main_option = st.radio(
    "Select an option:",
    ("Process New Images", "Load Existing Metadata"),
    key="main_option",
)

if main_option == "Process New Images":
    layout_process_new_images()

elif main_option == "Load Existing Metadata":
    layout_load_existing_metadata()

if st.session_state.metadata is not None:
    layout_search_images()
