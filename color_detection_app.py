import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io

# Function to calculate Euclidean distance between two RGB colors
def get_color_name(rgb, color_df):
    r, g, b = rgb
    distances = np.sqrt(
        (color_df['R'] - r) ** 2 +
        (color_df['G'] - g) ** 2 +
        (color_df['B'] - b) ** 2
    )
    closest = distances.idxmin()
    return color_df.loc[closest, 'color_name'], (color_df.loc[closest, 'R'],
                                                color_df.loc[closest, 'G'],
                                                color_df.loc[closest, 'B'])

# Load color dataset
try:
    color_df = pd.read_csv('colors.csv')
    if not all(col in color_df.columns for col in ['color_name', 'R', 'G', 'B']):
        st.error("Invalid colors.csv format. Ensure it has 'color_name', 'R', 'G', 'B' columns.")
        st.stop()
except FileNotFoundError:
    st.error("colors.csv file not found. Please place it in the same directory as the app.")
    st.stop()

# Streamlit app
st.title("Color Detection App")
st.write("Upload an image, click on it to detect the color, and see the results!")

# Image upload
uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    try:
        # Read and display the image
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Display image with clickable functionality
        st.image(image, caption="Click on the image to detect color", use_column_width=True)
        
        # Store click coordinates in session state
        if 'click_coords' not in st.session_state:
            st.session_state.click_coords = None
        
        # Simulate click detection (Streamlit doesn't natively support image clicks)
        # Using sliders as a workaround for user input
        st.write("Select a point on the image by adjusting the sliders below:")
        x = st.slider("X-coordinate", 0, img_array.shape[1] - 1, 0)
        y = st.slider("Y-coordinate", 0, img_array.shape[0] - 1, 0)
        
        if st.button("Detect Color"):
            st.session_state.click_coords = (x, y)
        
        if st.session_state.click_coords:
            x, y = st.session_state.click_coords
            if 0 <= y < img_array.shape[0] and 0 <= x < img_array.shape[1]:
                # Get RGB value at the clicked point
                rgb = img_array[y, x]
                color_name, closest_rgb = get_color_name(rgb, color_df)
                
                # Display results
                st.write(f"**Color Name:** {color_name}")
                st.write(f"**RGB Values:** {tuple(rgb)}")
                st.write(f"**Closest RGB Match:** {closest_rgb}")
                
                # Display a colored rectangle
                color_box = np.zeros((100, 100, 3), dtype=np.uint8)
                color_box[:] = rgb
                st.image(color_box, caption="Detected Color", use_column_width=False)
            else:
                st.error("Selected coordinates are out of image bounds.")
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
else:
    st.info("Please upload an image to start.")