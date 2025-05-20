import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import base64
import streamlit.components.v1 as components

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
st.markdown("Upload an image, click on any point, and discover the color's name and RGB values!")

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
        
        # Convert image to base64 for HTML display
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # JavaScript to capture click coordinates
        click_script = f"""
        <div id="image-container">
            <img id="clickable-image" src="data:image/png;base64,{img_base64}" style="max-width: 100%; height: auto;">
        </div>
        <script>
            const img = document.getElementById('clickable-image');
            img.addEventListener('click', function(e) {{
                const rect = img.getBoundingClientRect();
                const scaleX = img.naturalWidth / rect.width;
                const scaleY = img.naturalHeight / rect.height;
                const x = Math.round((e.clientX - rect.left) * scaleX);
                const y = Math.round((e.clientY - rect.top) * scaleY);
                // Send coordinates to Streamlit
                Streamlit.setComponentValue({{x: x, y: y}});
            }});
        </script>
        """
        
        # Display clickable image using Streamlit component
        coords = components.html(click_script, height=img_array.shape[0] + 50)
        
        # Store click coordinates in session state
        if 'click_coords' not in st.session_state:
            st.session_state.click_coords = None
        
        # Check if coordinates were received
        if coords and isinstance(coords, dict) and 'x' in coords and 'y' in coords:
            st.session_state.click_coords = (coords['x'], coords['y'])
        
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
                    st.write(f"**Clicked Coordinates:** ({x}, {y})")
                    
                    # Display a colored rectangle
                    color_box = np.zeros((100, 100, 3), dtype=np.uint8)
                    color_box[:] = rgb[:3]  # Use only RGB, ignore alpha if present
                    st.image(color_box, caption="Detected Color", use_container_width=False, width=100)
            else:
                st.error("Clicked coordinates are out of image bounds. Please click within the image.")
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
else:
    st.info("Please upload an image to start detecting colors.")

# Display instructions
st.markdown("""
**Instructions:**
1. Upload a PNG or JPEG image.
2. Click on any point in the image to detect the color.
3. View the color name, RGB values, and a color box below.
""")
