import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io

# Function to calculate Euclidean distance between two RGB colors
def get_color_name(rgb, color_df):
    # Handle both RGB (3 values) and RGBA (4 values) by taking first 3
    r, g, b = rgb[:3]
    distances = np.sqrt(
        (color_df['R'] - r) ** 2 +
        (color_df['G'] - g) ** 2 +
        (color_df['B'] - b) ** 2
    )
    closest = distances.idxmin()
    return color_df.loc[closest, 'color_name'], (color_df.loc[closest, 'R'],
                                                color_df.loc[closest, 'G'],
                                                color_df.loc[closest, 'B'])

# Streamlit app
st.set_page_config(page_title="Color Detection App", layout="centered")
st.title("Color Detection App")
st.write("Upload an image, select a point, and see the color details!")

# Load color dataset
try:
    color_df = pd.read_csv('colors.csv')
    if not all(col in color_df.columns for col in ['color_name', 'R', 'G', 'B']):
        st.error("Invalid colors.csv format. Ensure it has 'color_name', 'R', 'G', 'B' columns.")
        st.stop()
except FileNotFoundError:
    st.error("colors.csv file not found. Please place it in the same directory as the app.")
    st.stop()
except Exception as e:
    st.error(f"Error loading colors.csv: {str(e)}")
    st.stop()

# Image upload
uploaded_file = st.file_uploader("Choose an image (PNG/JPEG)...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    try:
        # Read and resize image for performance
        image = Image.open(uploaded_file)
        image = image.resize((800, 600))  # Resize to avoid performance issues
        img_array = np.array(image)
        # Convert to BGR for OpenCV if needed, but we'll work with img_array directly
        # img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # Removed since we use PIL's RGB
        
        # Display image
        st.image(image, caption="Select a point on the image using sliders", use_container_width=True)
        
        # Store click coordinates in session state
        if 'click_coords' not in st.session_state:
            st.session_state.click_coords = None
        
        # Sliders for selecting coordinates
        st.write("Use sliders to pick a point on the image:")
        x = st.slider("X-coordinate", 0, img_array.shape[1] - 1, 0, key="x_slider")
        y = st.slider("Y-coordinate", 0, img_array.shape[0] - 1, 0, key="y_slider")
        
        if st.button("Detect Color"):
            st.session_state.click_coords = (x, y)
        
        if st.session_state.click_coords:
            x, y = st.session_state.click_coords
            if 0 <= y < img_array.shape[0] and 0 <= x < img_array.shape[1]:
                # Get RGB value at the clicked point (handles RGBA automatically)
                rgb = img_array[y, x]
                color_name, closest_rgb = get_color_name(rgb, color_df)
                
                # Display results
                st.write(f"**Color Name:** {color_name}")
                st.write(f"**RGB Values:** {tuple(rgb[:3])}")
                st.write(f"**Closest RGB Match:** {closest_rgb}")
                
                # Display a colored rectangle
                color_box = np.zeros((100, 100, 3), dtype=np.uint8)
                color_box[:] = rgb[:3]  # Use only RGB, ignore alpha if present
                st.image(color_box, caption="Detected Color", use_container_width=False, width=100)
            else:
                st.error("Selected coordinates are out of image bounds.")
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
else:
    st.info("Please upload an image to start.")
