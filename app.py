# Import libraries
import gradio as gr
from ultralytics import YOLO
from PIL import Image
import tempfile
import os
import glob  # Helps find YOLO output files

# Load the YOLO Model
model = YOLO('best.pt')  # Path to trained model

# Load Sample Images (Pre-labeled examples)
sample_images = {
    "Example 1": "image_1.jpg",
    "Example 2": "image_2.jpg",
    "Example 3": "image_3.jpg",
    "Example 4": "image_4.jpg",
    "Example 5": "image_5.jpg",
    "Example 6": "image_6.jpg",
    "Example 7": "image_17.jpg",
    "Example 8": "image_8.jpg",
    "Example 9": "image_9.jpg",
    "Example 10": "image_10.jpg",
}

# Prepare Gradio Examples
examples = [[Image.open(path)] for path in sample_images.values()]

# Define Prediction Function
# Define Prediction Function
def detect_fod(img):
    with tempfile.TemporaryDirectory() as temp_dir:  # Create a temporary directory
        input_path = os.path.join(temp_dir, "input.jpg")  # Save uploaded image as a temp file
        img.save(input_path)  # Save the PIL Image to the temp path

        # Run object detection & save output in temp_dir
        model.predict(source=input_path, save=True, project=temp_dir, name="detect")

        # 🔍 Find the output image (use correct path)
        detect_folder = os.path.join(temp_dir, "detect")
        detected_images = glob.glob(f"{detect_folder}/*.jpg")  # Search for YOLO outputs

        if detected_images:  # If YOLO saved output, return the first detected image
            return Image.open(detected_images[0])

        return "Detection failed. No output image generated."

# Create Gradio Interface
gr.Interface(
    fn=detect_fod,
    inputs=gr.Image(type="pil", label="Upload Image for FoD Detection"),
    outputs=gr.Image(type="pil", label="Detected Objects"),
    examples=examples,  # Includes preloaded sample images
    title="✈️ Foreign Object Debris (FoD) Detection",
    description="Upload an image or select a sample image to detect foreign objects.",
    # allow_flagging="never"
).launch(debug=True)