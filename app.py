"""
ProPhoto AI - Professional Headshot Generator
============================================

A Streamlit application that transforms any photo into a professional headshot
using AI-powered background removal and image enhancement.

Features:
- AI background removal using rembg
- Professional background options
- Smart image enhancement (brightness, contrast, sharpness, saturation)
- High-quality output in JPEG and PNG formats
- 100% local processing for privacy

Author: Kondaveeti Anthony Raju
Version: 1.0.0
"""

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import rembg
import io
from typing import Tuple, Optional


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="ProPhoto AI", 
    page_icon="📸", 
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =============================================================================
# STYLING AND CSS
# =============================================================================

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app."""
    st.markdown("""
    <style>
        /* Main app background with gradient */
        .stApp {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        }
        
        /* Header styling */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            color: white;
        }
        
        .main-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .main-header p {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 0;
        }
        
        /* Upload section container */
        .upload-section {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        /* Settings panel styling */
        .settings-panel {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #2a5298;
        }
        
        /* Custom button styling */
        .stButton > button {
            background: linear-gradient(45deg, #1e3c72, #2a5298);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(45deg, #2a5298, #1e3c72);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* Results container */
        .result-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        /* Feature cards grid */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .feature-card {
            background: rgba(255,255,255,0.1);
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            color: white;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Success alert styling */
        .success-alert {
            background: #d1edff;
            border: 1px solid #0066cc;
            color: #004499;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# IMAGE PROCESSING FUNCTIONS
# =============================================================================

def enhance_image(
    image: Image.Image, 
    brightness: float = 1.1, 
    contrast: float = 1.2, 
    sharpness: float = 1.3, 
    saturation: float = 1.0
) -> Image.Image:
    """
    Enhance image quality with adjustable parameters.
    
    Args:
        image (Image.Image): Input PIL Image
        brightness (float): Brightness factor (1.0 = no change)
        contrast (float): Contrast factor (1.0 = no change)
        sharpness (float): Sharpness factor (1.0 = no change)
        saturation (float): Color saturation factor (1.0 = no change)
    
    Returns:
        Image.Image: Enhanced PIL Image
    """
    # Apply brightness enhancement
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)
    
    # Apply contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)
    
    # Apply sharpness enhancement
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(sharpness)
    
    # Apply color saturation enhancement
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(saturation)
    
    # Apply subtle smoothing to reduce noise
    image = image.filter(ImageFilter.SMOOTH_MORE)
    
    return image


def create_professional_background(
    size: Tuple[int, int], 
    bg_type: str, 
    custom_color: Optional[str] = None
) -> Image.Image:
    """
    Create a professional background with specified color/style.
    
    Args:
        size (Tuple[int, int]): Background dimensions (width, height)
        bg_type (str): Type of background ('Clean White', 'Corporate Gray', etc.)
        custom_color (str, optional): Hex color code for custom background
    
    Returns:
        Image.Image: Background image as PIL Image
    """
    # Define predefined professional background colors
    backgrounds = {
        "Clean White": (255, 255, 255),
        "Corporate Gray": (245, 245, 248),
        "LinkedIn Blue": (235, 242, 251),  # Fixed typo from original
        "Executive Black": (45, 45, 48)
    }
    
    # Use custom color if specified, otherwise use predefined
    if bg_type == "Custom" and custom_color:
        # Convert hex color to RGB tuple
        color = tuple(int(custom_color[i:i+2], 16) for i in (1, 3, 5))
    else:
        # Get predefined color or default to white
        color = backgrounds.get(bg_type, (255, 255, 255))
    
    # Create and return solid color background
    return Image.new("RGB", size, color)


def process_photo(
    image: Image.Image, 
    bg_type: str, 
    custom_color: Optional[str] = None, 
    add_enhancement: bool = True, 
    brightness: float = 1.1,
    contrast: float = 1.2, 
    sharpness: float = 1.3, 
    saturation: float = 1.0
) -> Image.Image:
    """
    Main photo processing pipeline that removes background and applies enhancements.
    
    Args:
        image (Image.Image): Input PIL Image
        bg_type (str): Background type to apply
        custom_color (str, optional): Custom background color if bg_type is 'Custom'
        add_enhancement (bool): Whether to apply image enhancements
        brightness (float): Brightness enhancement factor
        contrast (float): Contrast enhancement factor
        sharpness (float): Sharpness enhancement factor
        saturation (float): Saturation enhancement factor
    
    Returns:
        Image.Image: Processed professional headshot
    """
    # Ensure image is in RGBA mode for transparency support
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    # Convert PIL Image to bytes for rembg processing
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Remove background using AI model
    output = rembg.remove(img_byte_arr)
    img_no_bg = Image.open(io.BytesIO(output)).convert("RGBA")
    
    # Apply image enhancements if requested
    if add_enhancement:
        img_enhanced = enhance_image(
            img_no_bg, brightness, contrast, sharpness, saturation
        )
    else:
        img_enhanced = img_no_bg
    
    # Create professional background
    background = create_professional_background(
        img_enhanced.size, bg_type, custom_color
    )
    
    # Composite the enhanced image onto the background
    final_image = background.copy()
    final_image.paste(img_enhanced, (0, 0), img_enhanced)
    
    return final_image


def convert_to_download_format(image: Image.Image, format_type: str) -> bytes:
    """
    Convert processed image to downloadable format.
    
    Args:
        image (Image.Image): Processed PIL Image
        format_type (str): Output format ('JPEG' or 'PNG')
    
    Returns:
        bytes: Image data in specified format
    """
    img_buffer = io.BytesIO()
    
    if format_type == "JPEG":
        # Convert RGBA to RGB for JPEG (no transparency support)
        if image.mode == "RGBA":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1])
            rgb_image.save(img_buffer, format="JPEG", quality=95, optimize=True)
        else:
            image.save(img_buffer, format="JPEG", quality=95, optimize=True)
    else:  # PNG
        image.save(img_buffer, format="PNG", optimize=True)
    
    return img_buffer.getvalue()


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_header():
    """Render the main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>📸 ProPhoto AI</h1>
        <p>Transform any photo into a professional headshot in seconds</p>
    </div>
    """, unsafe_allow_html=True)


def render_feature_cards():
    """Render feature cards when no image is uploaded."""
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <h3>🤖 AI Background Removal</h3>
            <p>Automatically removes any background with precision</p>
        </div>
        <div class="feature-card">
            <h3>🎨 Professional Backgrounds</h3>
            <p>Clean, corporate-ready backgrounds for any industry</p>
        </div>
        <div class="feature-card">
            <h3>✨ Smart Enhancement</h3>
            <p>Optimizes brightness, contrast, and sharpness automatically</p>
        </div>
        <div class="feature-card">
            <h3>📱 Instant Results</h3>
            <p>Professional photos ready in seconds, not hours</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render the application footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: white; padding: 2rem;">
        <p><strong>🔒 100% Private & Secure</strong></p>
        <p>All processing happens locally on your device. No data is stored or transmitted.</p>
        <p style="margin-top: 1rem; opacity: 0.8;">Built with ❤️ using Streamlit & AI</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application function."""
    
    # Apply custom styling
    apply_custom_css()
    
    # Render header
    render_header()
    
    # Initialize session state variables
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    if 'original_image' not in st.session_state:
        st.session_state.original_image = None
    
    # Main upload and processing section
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "📤 Choose your photo",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear photo with good lighting for best results"
        )
        
        if uploaded_file is not None:
            # Load and store original image
            original_image = Image.open(uploaded_file)
            st.session_state.original_image = original_image
            
            # Settings panel
            st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
            st.subheader("🎛️ Customize Your Professional Photo")
            
            # Create two columns for settings
            col1, col2 = st.columns(2)
            
            with col1:
                # Background selection
                bg_type = st.selectbox(
                    "Background Style",
                    ["Clean White", "Corporate Gray", "LinkedIn Blue", "Executive Black", "Custom"],
                    help="Choose a professional background"
                )
                
                # Custom color picker for custom background
                custom_color = None
                if bg_type == "Custom":
                    custom_color = st.color_picker("Pick background color", "#FFFFFF")
            
            with col2:
                # Enhancement toggle
                add_enhancement = st.checkbox("✨ Enhance Image Quality", value=True)
                
                # Enhancement fine-tuning
                if add_enhancement:
                    with st.expander("🔧 Fine-tune Enhancement"):
                        brightness = st.slider("Brightness", 0.7, 1.5, 1.1, 0.1)
                        contrast = st.slider("Contrast", 0.7, 1.5, 1.2, 0.1)
                        sharpness = st.slider("Sharpness", 0.7, 1.5, 1.3, 0.1)
                        saturation = st.slider("Color Saturation", 0.5, 1.5, 1.0, 0.1)
                else:
                    # Default enhancement values when disabled
                    brightness = contrast = sharpness = saturation = 1.0
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Process button
            if st.button("🚀 Create Professional Photo"):
                with st.spinner("✨ Processing your photo..."):
                    try:
                        # Process the photo
                        processed_image = process_photo(
                            original_image, bg_type, custom_color, 
                            add_enhancement, brightness, contrast, sharpness, saturation
                        )
                        
                        # Store processed image in session state
                        st.session_state.processed_image = processed_image
                        
                        # Show success message
                        st.markdown("""
                        <div class="success-alert">
                            ✅ Your professional photo is ready! Scroll down to see the results.
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"❌ Processing failed: {str(e)}")
                        st.info("💡 Try a different image or check your connection")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if (st.session_state.original_image is not None and 
        st.session_state.processed_image is not None):
        
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        
        st.subheader("📸 Your Professional Transformation")
        
        # Before/After comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Before**")
            st.image(st.session_state.original_image, use_container_width=True)
        
        with col2:
            st.markdown("**After - Professional**")
            st.image(st.session_state.processed_image, use_container_width=True)
        
        # Download section
        st.subheader("💾 Download Your Photo")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # JPEG download
            jpg_data = convert_to_download_format(
                st.session_state.processed_image, "JPEG"
            )
            st.download_button(
                label="📥 Download JPEG (Recommended)",
                data=jpg_data,
                file_name="professional_headshot.jpg",
                mime="image/jpeg"
            )
        
        with col4:
            # PNG download
            png_data = convert_to_download_format(
                st.session_state.processed_image, "PNG"
            )
            st.download_button(
                label="📥 Download PNG",
                data=png_data,
                file_name="professional_headshot.png",
                mime="image/png"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show feature cards when no image is uploaded
    if uploaded_file is None:
        render_feature_cards()
    
    # Render footer
    render_footer()


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()