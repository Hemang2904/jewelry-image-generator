import streamlit as st
import fal_client
import os
import requests
from PIL import Image
from io import BytesIO
import base64
import time
import concurrent.futures
from typing import List, Dict
import zipfile

# Page configuration
st.set_page_config(
    page_title="Bulk Jewelry Image Generator - Flux 2",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E40AF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-box {
        padding: 1rem;
        background-color: #D1FAE5;
        border-radius: 8px;
        border-left: 4px solid #10B981;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #DBEAFE;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False

def get_image_base64(image_path_or_url):
    """Convert image to base64 for API"""
    if image_path_or_url.startswith('http'):
        response = requests.get(image_path_or_url)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(image_path_or_url)
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def create_variations_prompts(base_prompt: str, num_variations: int, params: Dict) -> List[Dict]:
    """Create varied prompts for jewelry generation"""
    
    materials = params.get('materials', ['gold', 'silver', 'platinum', 'rose gold'])
    gemstones = params.get('gemstones', ['diamond', 'sapphire', 'emerald', 'ruby'])
    styles = params.get('styles', ['modern', 'vintage', 'minimalist', 'ornate'])
    angles = params.get('angles', ['front view', 'side view', '3/4 view', 'top view'])
    backgrounds = params.get('backgrounds', ['white studio background', 'luxury velvet background', 
                                             'marble surface', 'minimalist gray background'])
    lighting = params.get('lighting', ['studio lighting', 'natural daylight', 'dramatic lighting', 
                                       'soft diffused light'])
    
    prompts = []
    
    for i in range(num_variations):
        material = materials[i % len(materials)]
        gemstone = gemstones[i % len(gemstones)]
        style = styles[i % len(styles)]
        angle = angles[i % len(angles)]
        background = backgrounds[i % len(backgrounds)]
        light = lighting[i % len(lighting)]
        
        variation_prompt = f"{base_prompt}, {material} jewelry, {gemstone} stones, {style} style, {angle}, {background}, {light}, professional product photography, high detail, 8K resolution, commercial photography"
        
        prompts.append({
            'prompt': variation_prompt,
            'metadata': {
                'material': material,
                'gemstone': gemstone,
                'style': style,
                'angle': angle,
                'background': background,
                'lighting': light,
                'index': i + 1
            }
        })
    
    return prompts

def generate_single_image(prompt_data: Dict, api_token: str, model_params: Dict) -> Dict:
    """Generate a single image using fal.ai Flux"""
    try:
        os.environ["FAL_KEY"] = api_token
        
        # Choose model based on params
        model_choice = model_params.get('model', 'fal-ai/flux/dev')
        
        # fal.ai Flux model
        result = fal_client.subscribe(
            model_choice,
            arguments={
                "prompt": prompt_data['prompt'],
                "image_size": model_params.get('image_size', '1024x1024'),
                "num_inference_steps": model_params.get('num_inference_steps', 28),
                "guidance_scale": model_params.get('guidance_scale', 3.5),
                "num_images": 1,
                "enable_safety_checker": model_params.get('enable_safety_checker', True),
                "output_format": model_params.get('output_format', 'png')
            }
        )
        
        # Get image URL from result
        if isinstance(result, dict) and 'images' in result:
            image_url = result['images'][0]['url']
        else:
            image_url = result
        
        return {
            'success': True,
            'url': image_url,
            'metadata': prompt_data['metadata']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'metadata': prompt_data['metadata']
        }

def generate_images_parallel(prompts: List[Dict], api_token: str, model_params: Dict, max_workers: int = 5):
    """Generate multiple images in parallel"""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(generate_single_image, prompt, api_token, model_params): prompt 
                   for prompt in prompts}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            yield result

def download_image(url: str, filepath: str):
    """Download image from URL"""
    response = requests.get(url)
    with open(filepath, 'wb') as f:
        f.write(response.content)

def create_zip_file(image_urls: List[str], zip_path: str):
    """Create a zip file with all generated images"""
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for idx, url in enumerate(image_urls):
            try:
                response = requests.get(url)
                img_data = response.content
                zipf.writestr(f'jewelry_image_{idx+1:03d}.png', img_data)
            except Exception as e:
                st.warning(f"Failed to add image {idx+1} to zip: {str(e)}")

# App Header
st.markdown('<div class="main-header">💎 Bulk Jewelry Image Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate 50+ high-quality jewelry variations using Flux 2 AI</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Token - Check Streamlit secrets first, then allow manual input
    api_token = None
    try:
        # Try to load from Streamlit secrets (for deployment)
        api_token = st.secrets["FAL_KEY"]
        st.success("✅ API Token loaded from secrets")
    except (KeyError, FileNotFoundError):
        # Fall back to manual input (for local development)
        api_token = st.text_input(
            "fal.ai API Key",
            type="password",
            help="Get your key from https://fal.ai/dashboard/keys"
        )
        if not api_token:
            st.info("💡 For deployment: Add FAL_KEY to Streamlit secrets")
    
    st.markdown("---")
    
    # Number of images
    num_images = st.slider(
        "Number of Images to Generate",
        min_value=10,
        max_value=100,
        value=50,
        step=5,
        help="More images = longer generation time"
    )
    
    # Model parameters
    st.subheader("🎨 Model Parameters")
    
    model_choice = st.selectbox(
        "Flux Model",
        options=[
            "fal-ai/flux/dev",
            "fal-ai/flux-pro/v1.1", 
            "fal-ai/flux-2-pro",
            "fal-ai/flux/schnell"
        ],
        index=0,
        help="Dev: Best balance. Pro: Highest quality. Schnell: Fastest"
    )
    
    image_size = st.selectbox(
        "Image Size",
        options=["1024x1024", "1024x768", "768x1024", "1280x720", "720x1280"],
        index=0
    )
    
    num_inference_steps = st.slider(
        "Inference Steps",
        min_value=10,
        max_value=50,
        value=28,
        step=2,
        help="More steps = better quality but slower"
    )
    
    guidance_scale = st.slider(
        "Guidance Scale",
        min_value=1.0,
        max_value=10.0,
        value=3.5,
        step=0.5,
        help="How closely to follow the prompt"
    )
    
    st.markdown("---")
    
    # Variation parameters
    st.subheader("🔄 Variation Settings")
    
    use_custom_variations = st.checkbox("Customize Variations", value=False)
    
    if use_custom_variations:
        materials = st.multiselect(
            "Materials",
            options=['gold', 'silver', 'platinum', 'rose gold', 'white gold', 'titanium'],
            default=['gold', 'silver', 'platinum', 'rose gold']
        )
        
        gemstones = st.multiselect(
            "Gemstones",
            options=['diamond', 'sapphire', 'emerald', 'ruby', 'pearl', 'amethyst', 'topaz'],
            default=['diamond', 'sapphire', 'emerald', 'ruby']
        )
        
        styles = st.multiselect(
            "Styles",
            options=['modern', 'vintage', 'minimalist', 'ornate', 'art deco', 'bohemian'],
            default=['modern', 'vintage', 'minimalist', 'ornate']
        )
    else:
        materials = ['gold', 'silver', 'platinum', 'rose gold']
        gemstones = ['diamond', 'sapphire', 'emerald', 'ruby']
        styles = ['modern', 'vintage', 'minimalist', 'ornate']
    
    st.markdown("---")
    
    # Generation settings
    st.subheader("⚡ Generation Settings")
    
    max_workers = st.slider(
        "Parallel Workers",
        min_value=1,
        max_value=10,
        value=5,
        help="Higher = faster but may hit rate limits"
    )

# Main Content Area
tab1, tab2, tab3 = st.tabs(["📝 Input", "🖼️ Gallery", "📊 Statistics"])

with tab1:
    st.header("Input Your Jewelry Design")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Text description input
        st.subheader("Text Description")
        base_prompt = st.text_area(
            "Describe your jewelry design",
            placeholder="Example: elegant ring with intricate band design, center stone setting",
            height=150,
            help="Be specific about the jewelry type, design elements, and desired features"
        )
        
        # Optional: Upload reference image
        st.subheader("Reference Image (Optional)")
        uploaded_file = st.file_uploader(
            "Upload a reference image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an existing jewelry image for style reference"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Reference Image", use_column_width=True)
    
    with col2:
        st.subheader("Quick Templates")
        template = st.selectbox(
            "Choose a template (optional)",
            options=[
                "Custom (use your description)",
                "Engagement Ring - Classic Solitaire",
                "Necklace - Pendant Chain",
                "Bracelet - Tennis Style",
                "Earrings - Stud Design",
                "Wedding Band - Classic",
                "Cocktail Ring - Statement Piece"
            ]
        )
        
        template_prompts = {
            "Engagement Ring - Classic Solitaire": "elegant engagement ring with classic solitaire design, round brilliant cut center stone, delicate prong setting, smooth polished band",
            "Necklace - Pendant Chain": "elegant pendant necklace with delicate chain, centered gemstone pendant, sophisticated clasp design",
            "Bracelet - Tennis Style": "tennis bracelet with continuous line of gemstones, secure clasp, uniform stone setting",
            "Earrings - Stud Design": "classic stud earrings with secure post backing, symmetrical gemstone setting",
            "Wedding Band - Classic": "wedding band with classic design, smooth polished finish, comfortable fit",
            "Cocktail Ring - Statement Piece": "bold cocktail ring with large center stone, ornate setting design, dramatic presence"
        }
        
        if template != "Custom (use your description)":
            base_prompt = template_prompts[template]
            st.info(f"Using template: {template}")
        
        st.markdown("---")
        
        # Cost estimation
        st.subheader("💰 Cost Estimation")
        
        # fal.ai pricing per model
        cost_per_image = {
            "fal-ai/flux/dev": 0.025,
            "fal-ai/flux-pro/v1.1": 0.04,
            "fal-ai/flux-2-pro": 0.03,
            "fal-ai/flux/schnell": 0.01
        }
        
        estimated_cost = num_images * cost_per_image.get(model_choice, 0.025)
        estimated_time = num_images / max_workers * (num_inference_steps / 4)  # rough estimate
        
        st.metric("Estimated Cost", f"${estimated_cost:.2f}")
        st.metric("Estimated Time", f"{estimated_time:.1f} minutes")
    
    # Generate button
    st.markdown("---")
    
    if st.button("🚀 Generate Images", type="primary", use_container_width=True):
        if not api_token:
            st.error("❌ Please enter your Replicate API token in the sidebar!")
        elif not base_prompt:
            st.error("❌ Please provide a jewelry description!")
        else:
            # Reset previous results
            st.session_state.generated_images = []
            st.session_state.generation_complete = False
            
            # Create variation prompts
            variation_params = {
                'materials': materials,
                'gemstones': gemstones,
                'styles': styles,
                'angles': ['front view', 'side view', '3/4 view', 'top view'],
                'backgrounds': ['white studio background', 'luxury velvet background', 
                               'marble surface', 'minimalist gray background'],
                'lighting': ['studio lighting', 'natural daylight', 'dramatic lighting', 
                            'soft diffused light']
            }
            
            prompts = create_variations_prompts(base_prompt, num_images, variation_params)
            
            # Model parameters
            model_params = {
                'model': model_choice,
                'image_size': image_size,
                'num_inference_steps': num_inference_steps,
                'guidance_scale': guidance_scale,
                'output_format': 'png',
                'enable_safety_checker': True
            }
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            error_count = 0
            
            # Generate images
            for idx, result in enumerate(generate_images_parallel(prompts, api_token, model_params, max_workers)):
                if result['success']:
                    st.session_state.generated_images.append(result)
                    success_count += 1
                else:
                    error_count += 1
                
                # Update progress
                progress = (idx + 1) / num_images
                progress_bar.progress(progress)
                status_text.text(f"Generated {success_count} images ({error_count} errors) - {progress*100:.1f}% complete")
            
            st.session_state.generation_complete = True
            
            # Final status
            if success_count > 0:
                st.success(f"✅ Successfully generated {success_count} images!")
                if error_count > 0:
                    st.warning(f"⚠️ {error_count} images failed to generate")
            else:
                st.error("❌ Failed to generate any images. Please check your API token and try again.")

with tab2:
    st.header("Generated Images Gallery")
    
    if st.session_state.generation_complete and st.session_state.generated_images:
        # Download all button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Download All Images (ZIP)", type="primary", use_container_width=True):
                with st.spinner("Creating zip file..."):
                    zip_path = "/home/claude/jewelry_images.zip"
                    image_urls = [img['url'] for img in st.session_state.generated_images]
                    create_zip_file(image_urls, zip_path)
                    
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            label="💾 Download ZIP",
                            data=f,
                            file_name="jewelry_images.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
        
        st.markdown("---")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_material = st.multiselect("Filter by Material", 
                                            options=materials,
                                            default=[])
        with col2:
            filter_gemstone = st.multiselect("Filter by Gemstone",
                                            options=gemstones,
                                            default=[])
        with col3:
            filter_style = st.multiselect("Filter by Style",
                                         options=styles,
                                         default=[])
        
        # Display images in grid
        filtered_images = st.session_state.generated_images
        
        if filter_material:
            filtered_images = [img for img in filtered_images 
                             if img['metadata']['material'] in filter_material]
        if filter_gemstone:
            filtered_images = [img for img in filtered_images 
                             if img['metadata']['gemstone'] in filter_gemstone]
        if filter_style:
            filtered_images = [img for img in filtered_images 
                             if img['metadata']['style'] in filter_style]
        
        st.info(f"Showing {len(filtered_images)} of {len(st.session_state.generated_images)} images")
        
        # Grid layout
        cols_per_row = 4
        for i in range(0, len(filtered_images), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(filtered_images):
                    img_data = filtered_images[i + j]
                    with col:
                        st.image(img_data['url'], use_column_width=True)
                        with st.expander("Details"):
                            st.write(f"**Index:** {img_data['metadata']['index']}")
                            st.write(f"**Material:** {img_data['metadata']['material']}")
                            st.write(f"**Gemstone:** {img_data['metadata']['gemstone']}")
                            st.write(f"**Style:** {img_data['metadata']['style']}")
                            st.write(f"**Angle:** {img_data['metadata']['angle']}")
                            
                            # Individual download
                            response = requests.get(img_data['url'])
                            st.download_button(
                                label="Download",
                                data=response.content,
                                file_name=f"jewelry_{img_data['metadata']['index']:03d}.png",
                                mime="image/png",
                                use_container_width=True
                            )
    else:
        st.info("👆 Generate images from the Input tab to see them here!")

with tab3:
    st.header("Generation Statistics")
    
    if st.session_state.generation_complete and st.session_state.generated_images:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Generated", len(st.session_state.generated_images))
        
        with col2:
            materials_used = set(img['metadata']['material'] for img in st.session_state.generated_images)
            st.metric("Materials Used", len(materials_used))
        
        with col3:
            gemstones_used = set(img['metadata']['gemstone'] for img in st.session_state.generated_images)
            st.metric("Gemstones Used", len(gemstones_used))
        
        with col4:
            styles_used = set(img['metadata']['style'] for img in st.session_state.generated_images)
            st.metric("Styles Used", len(styles_used))
        
        st.markdown("---")
        
        # Breakdown by categories
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Breakdown by Material")
            material_counts = {}
            for img in st.session_state.generated_images:
                mat = img['metadata']['material']
                material_counts[mat] = material_counts.get(mat, 0) + 1
            
            for material, count in sorted(material_counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"**{material.title()}:** {count} images")
        
        with col2:
            st.subheader("Breakdown by Gemstone")
            gemstone_counts = {}
            for img in st.session_state.generated_images:
                gem = img['metadata']['gemstone']
                gemstone_counts[gem] = gemstone_counts.get(gem, 0) + 1
            
            for gemstone, count in sorted(gemstone_counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"**{gemstone.title()}:** {count} images")
    else:
        st.info("👆 Generate images to see statistics!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #64748B; padding: 1rem;'>
        <p>💎 Bulk Jewelry Image Generator powered by Flux 2 AI</p>
        <p style='font-size: 0.9rem;'>Need help? Check the sidebar for configuration options</p>
    </div>
    """, unsafe_allow_html=True)
