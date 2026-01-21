"""
Configuration file for Bulk Jewelry Image Generator
Modify these settings to customize your application
"""

# API Configuration
REPLICATE_MODEL = "black-forest-labs/flux-1.1-pro"  # Flux 1.1 Pro model
ALTERNATIVE_MODELS = {
    "flux-pro": "black-forest-labs/flux-pro",
    "flux-dev": "black-forest-labs/flux-dev",
    "flux-schnell": "black-forest-labs/flux-schnell",  # Faster, lower quality
}

# Default Generation Settings
DEFAULT_SETTINGS = {
    "num_images": 50,
    "aspect_ratio": "1:1",
    "output_quality": 95,
    "output_format": "png",
    "safety_tolerance": 2,
    "prompt_upsampling": True,
    "max_workers": 5
}

# Variation Parameters
MATERIALS = [
    'gold',
    'silver', 
    'platinum',
    'rose gold',
    'white gold',
    'titanium',
    'brass',
    'copper'
]

GEMSTONES = [
    'diamond',
    'sapphire',
    'emerald',
    'ruby',
    'pearl',
    'amethyst',
    'topaz',
    'aquamarine',
    'garnet',
    'opal',
    'turquoise',
    'onyx'
]

STYLES = [
    'modern',
    'vintage',
    'minimalist',
    'ornate',
    'art deco',
    'bohemian',
    'classic',
    'contemporary',
    'gothic',
    'romantic'
]

ANGLES = [
    'front view',
    'side view',
    '3/4 view',
    'top view',
    'angled view',
    '45 degree view'
]

BACKGROUNDS = [
    'white studio background',
    'luxury velvet background',
    'marble surface',
    'minimalist gray background',
    'black velvet background',
    'wooden surface',
    'silk fabric background',
    'gradient background'
]

LIGHTING = [
    'studio lighting',
    'natural daylight',
    'dramatic lighting',
    'soft diffused light',
    'golden hour lighting',
    'rim lighting',
    'high key lighting',
    'low key lighting'
]

# Jewelry Templates
TEMPLATES = {
    "Engagement Ring - Classic Solitaire": {
        "prompt": "elegant engagement ring with classic solitaire design, round brilliant cut center stone, delicate prong setting, smooth polished band",
        "category": "ring"
    },
    "Engagement Ring - Halo Design": {
        "prompt": "engagement ring with halo setting, center diamond surrounded by smaller stones, intricate band design, luxurious appearance",
        "category": "ring"
    },
    "Engagement Ring - Three Stone": {
        "prompt": "three stone engagement ring, center stone with two side stones, symbolic design, elegant band",
        "category": "ring"
    },
    "Wedding Band - Classic": {
        "prompt": "wedding band with classic design, smooth polished finish, comfortable fit, timeless style",
        "category": "ring"
    },
    "Wedding Band - Diamond": {
        "prompt": "diamond wedding band with continuous line of stones, channel setting, brilliant sparkle",
        "category": "ring"
    },
    "Necklace - Pendant Chain": {
        "prompt": "elegant pendant necklace with delicate chain, centered gemstone pendant, sophisticated clasp design",
        "category": "necklace"
    },
    "Necklace - Statement Piece": {
        "prompt": "bold statement necklace with multiple gemstones, intricate design, dramatic presence",
        "category": "necklace"
    },
    "Necklace - Choker": {
        "prompt": "elegant choker necklace with tight fit, decorative elements, modern design",
        "category": "necklace"
    },
    "Bracelet - Tennis Style": {
        "prompt": "tennis bracelet with continuous line of gemstones, secure clasp, uniform stone setting",
        "category": "bracelet"
    },
    "Bracelet - Bangle": {
        "prompt": "sleek bangle bracelet with smooth finish, minimalist design, comfortable fit",
        "category": "bracelet"
    },
    "Bracelet - Chain": {
        "prompt": "chain bracelet with decorative links, secure clasp, elegant drape",
        "category": "bracelet"
    },
    "Earrings - Stud Design": {
        "prompt": "classic stud earrings with secure post backing, symmetrical gemstone setting",
        "category": "earrings"
    },
    "Earrings - Drop Style": {
        "prompt": "drop earrings with dangling gemstone, elegant movement, sophisticated design",
        "category": "earrings"
    },
    "Earrings - Hoop": {
        "prompt": "hoop earrings with smooth finish, classic circular design, secure clasp",
        "category": "earrings"
    },
    "Cocktail Ring - Statement Piece": {
        "prompt": "bold cocktail ring with large center stone, ornate setting design, dramatic presence",
        "category": "ring"
    },
    "Eternity Band": {
        "prompt": "eternity band with continuous stones around entire band, symbolic design, brilliant sparkle",
        "category": "ring"
    }
}

# UI Configuration
UI_CONFIG = {
    "page_title": "Bulk Jewelry Image Generator - Flux 2",
    "page_icon": "💎",
    "layout": "wide",
    "theme": {
        "primary_color": "#1E40AF",
        "background_color": "#FFFFFF",
        "secondary_background_color": "#F1F5F9",
        "text_color": "#1E293B"
    }
}

# Cost Estimation (per image in USD)
COST_PER_IMAGE = {
    "flux-pro": 0.01,
    "flux-dev": 0.005,
    "flux-schnell": 0.002
}

# Time Estimation (seconds per image)
TIME_PER_IMAGE = {
    "flux-pro": 10,
    "flux-dev": 8,
    "flux-schnell": 3
}

# Quality Presets
QUALITY_PRESETS = {
    "Maximum Quality": {
        "output_quality": 100,
        "prompt_upsampling": True,
        "model": "flux-pro"
    },
    "Balanced": {
        "output_quality": 95,
        "prompt_upsampling": True,
        "model": "flux-pro"
    },
    "Fast Draft": {
        "output_quality": 85,
        "prompt_upsampling": False,
        "model": "flux-schnell"
    }
}

# Prompt Enhancement
PROMPT_SUFFIXES = {
    "quality": "professional product photography, high detail, 8K resolution, commercial photography, studio quality",
    "style": "photorealistic, high resolution, sharp focus, professional lighting",
    "jewelry_specific": "macro photography, jewelry photography, detailed metalwork, brilliant gemstone clarity"
}

# Export Settings
EXPORT_CONFIG = {
    "zip_compression": 6,  # 0-9, 6 is balanced
    "image_format": "png",
    "include_metadata_json": True,  # Save metadata as JSON file
    "create_contact_sheet": False  # Create overview image with all variations
}

# Rate Limiting
RATE_LIMIT_CONFIG = {
    "max_concurrent_requests": 10,
    "retry_attempts": 3,
    "retry_delay": 5  # seconds
}

# Advanced Features (Future)
ADVANCED_FEATURES = {
    "enable_controlnet": False,  # For precise control using reference images
    "enable_background_removal": False,  # Auto-remove background
    "enable_upscaling": False,  # 4x upscaling
    "enable_batch_csv": False  # Generate from CSV file
}
