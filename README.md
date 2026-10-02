# 3D Anime Character Repository & Rendering Pipeline

A production-grade 3D anime character library and wallpaper rendering studio built with **Blender 5.2.2 LTS**, custom **EEVEE-Next NPR (Non-Photorealistic Rendering) cel-shaders**, and automated Python pipelines.

---

## Features
- **3D Anime Character Vault**: Organized directory structure for storing, standardizing, and optimizing anime 3D models (`.pmx`, `.vrm`, `.blend`).
- **Studio-Quality Cel-Shading**: Custom EEVEE-Next NPR shader node groups with stepped light/shadow ramps, anime rim lighting, anisotropic hair rings, and inverted hull outlines.
- **Dual Wallpaper Pipeline**:
  - **Ultra-HD Stills**: 4K/8K illustration-grade renders with cinematic lighting and compositing.
  - **Seamless 60 FPS Video Loops**: 120-frame or 240-frame looping live wallpapers with micro-animations (breathing, hair/cloth wind sway, eye blinks).
- **Automated Tooling**: Scripts for headless scene setup, shader generation, and one-command rendering.

---

## Directory Structure
```
anime/
├── .agent/skills/             # Custom Antigravity agent skills
├── characters/                # Stored anime 3D character models & textures
├── props/                     # Weapons, accessories, scenery elements
├── scenes/                    # Master blend files and lighting setups
├── shaders/                   # Reusable NPR anime shader node trees
├── animations/                # Reusable action loops & poses
├── renders/                   # Stills and video loop outputs
├── scripts/                   # Blender Python automation scripts
└── docs/                      # Model sourcing & optimization documentation
```

---

## Quick Start

### 1. View Installed 3D Anime Add-ons
Both **MMD Tools** (`.pmx`/`.pmd`) and **VRM Add-on** (`.vrm`) are pre-installed in Blender 5.2:
```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --python-expr "import addon_utils; print('MMD:', addon_utils.enable('mmd_tools')); print('VRM:', addon_utils.enable('io_scene_vrm'))"
```

### 2. Sourcing Characters
Refer to [docs/3D_MODEL_SOURCES.md](docs/3D_MODEL_SOURCES.md) for verified free sources (Aplaybox, BowlRoll, VRoid Hub, The Models Resource) and optimization steps in [docs/OPTIMIZATION_GUIDE.md](docs/OPTIMIZATION_GUIDE.md).

### 3. Rendering Wallpapers (Headless)
- **High-Res Still Render**:
  ```bash
  /Applications/Blender.app/Contents/MacOS/Blender -b scenes/master_composition.blend --python scripts/render_pipeline.py -- --still
  ```
- **60 FPS Seamless Loop Video**:
  ```bash
  /Applications/Blender.app/Contents/MacOS/Blender -b scenes/master_composition.blend --python scripts/render_pipeline.py -- --loop
  ```
