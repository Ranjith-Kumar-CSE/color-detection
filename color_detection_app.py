import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image

# Function to calculate Euclidean distance between two RGB colors
def get_color_name(rgb, color_df):
    try:
        r, g, b = rgb[:3]  # Handle RGB or RGBA by taking first 3 values
        distances = np.sqrt(
            (color_df['R'] - r) ** 2 +
            (color_df['G'] - g) ** 2 +
            (color_df['B'] - b) ** 2
        )
        closest = distances.idxmin()
        return color_df.loc[closest, 'color_name'], (color_df.loc[closest, 'R'],
                                                    color_df.loc[closest, 'G'],
                                                    color_df.loc[closest, 'B'])
    except Exception as e:
        st.error(f"Error matching color: {str(e)}")
        return "Unknown", (0, 0, 0)

# Streamlit app configuration
st.set_page_config(page_title="Color Detection App", layout="centered")
st.title("🎨 Color Detection App")
st.markdown("Upload an image, pick a point with sliders, and discover the color's name and RGB values!")

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
uploaded_file = st.file_uploader("Choose an image (PNG/JPEG)...", type=["png", "jpg", "jpeg"], key="image_uploader")

if uploaded_file is not None:
    try:
        # Read and resize image for performance
        image = Image.open(uploaded_file)
        # Resize while maintaining aspect ratio, max width/height 800px
        image.thumbnail((800, 800))
        img_array = np.array(image)
        
        # Validate image channels
        if img_array.ndim != 3 or img_array.shape[2] not in [3, 4]:
            st.error("Unsupported image format. Please upload an RGB or RGBA image.")
            st.stop()
        
        # Display image
        st.image(image, caption="Select a point on the image using sliders", use_container_width=True)
        
        # Store click coordinates in session state
        if 'click_coords' not in st.session_state:
            st.session_state.click_coords = None
        
        # Sliders for selecting coordinates with dynamic max values
        st.markdown("**Pick a point on the image:**")
        col1, col2 = st.columns(2)
        with col1:
            x = st.slider("X-coordinate", 0, img_array.shape[1] - 1, 0, key="x_slider")
        with col2:
            y = st.slider("Y-coordinate", 0, img_array.shape[0] - 1, 0, key="y_slider")
        
        if st.button("Detect Color", key="detect_button"):
            st.session_state.click_coords = (x, y)
        
        if st.session_state.click_coords:
            x, y = st.session_state.click_coords
            if 0 <= y < img_array.shape[0] and 0 <= x < img_array.shape[1]:
                # Get RGB value at the clicked point
                rgb = img_array[y, x]
                color_name, closest_rgb = get_color_name(rgb, color_df)
                
                # Display results in a styled container
                with st.container():
                    st.markdown("### Color Details")
                    st.write(f"**Color Name:** {color_name}")
                    st.write(f"**RGB Values:** {tuple(rgb[:3])}")
                    st.write(f"**Closest RGB Match:** {closest_rgb}")
                    
                    # Display a colored rectangle
                    color_box = np.zeros((100, 100, 3), dtype=np.uint8)
                    color_box[:] = rgb[:3]  # Use only RGB, ignore alpha if present
                    st.image(color_box, caption="Detected Color", use_container_width=False, width=100)
            else:
                st.error("Selected coordinates are out of image bounds. Please adjust the sliders.")
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
else:
    st.info("Please upload an image to start detecting colors.")
