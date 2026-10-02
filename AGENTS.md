# AGENTS.md — 3D Anime Character Repository & Rendering Pipeline

## 1. Project Purpose & Scope
This repository is a production-grade 3D anime character library and rendering pipeline.
The primary deliverables are:
1. **Curated 3D Anime Character Library**: Storing, standardizing, and optimizing 3D models (`.pmx`, `.vrm`, `.fbx`, `.blend`) of the user's favorite anime characters.
2. **High-Res Static Wallpaper**: Ultra-HD (4K `3840x2160` / 8K) illustration-style renders with custom anime cel-shading and cinematic lighting.
3. **Seamless Looping Live Wallpaper**: 60 FPS video loops (120-frame or 240-frame) featuring micro-animations (breathing, wind sway in hair and cloth, eye blinks, atmospheric particles).

---

## 2. Tech Stack & Environment Specs
- **Blender**: 5.2.2 LTS (Installed at `/Applications/Blender.app/Contents/MacOS/Blender`).
- **Render Engine**: **EEVEE-Next** (Real-time NPR shader responsiveness with Raytracing/Shadow evaluation).
- **Blender Python**: Python 3.13 (`/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13`).
- **Installed Blender Add-ons**:
  - `mmd_tools`: Supports MikuMikuDance (`.pmx`, `.pmd`) models with morphs, physics, and bone translations.
  - `io_scene_vrm` (`VRM_Addon_for_Blender`): Supports VRoid / VRChat (`.vrm`) models with humanoid spring bones and blendshapes.
  - `blender_mcp`: MCP bridge for live viewport control and visual feedback.
  - `node_wrangler` & `rigify`: Core Blender procedural tools.
- **System Tools**:
  - `git-lfs`: Tracks large binary assets (`.blend`, `.pmx`, `.vrm`, `.fbx`, `.tga`).
  - `gltf-transform`: CLI tool for mesh deduplication, texture resizing, and Draco/Meshopt compression.
  - `@pixiv/three-vrm`: VRM avatar validation and structure verification.
  - `ffmpeg`: Video encoding (`/opt/homebrew/bin/ffmpeg`) for 60 FPS H.265 / HEVC MP4 loops.

---

## 3. Directory Layout & Organization

```
blender-project/anime/
├── .agent/
│   └── skills/
│       └── blender-anime-pipeline/   # Antigravity skill with NPR shaders & loop recipes
├── characters/                       # Per-character assets (one folder per character)
│   └── <character_name>/
│       ├── raw/                      # Original downloaded archives / files
│       ├── textures/                 # Optimized textures (PNG / TGA)
│       └── <character_name>.blend    # Standardized, rigged, cel-shaded character asset
├── props/                            # Weapons, accessories, furniture, nature assets
├── scenes/                           # Master composition and environment scenes
│   ├── master_composition.blend      # Main wallpaper staging scene
│   └── lighting_presets/             # Golden hour, night neon, dramatic backlight rigs
├── shaders/                          # Reusable NPR node groups and material templates
├── animations/                       # Reusable action loops (idle breathing, wind sway, blinks)
├── renders/                          # Output directory (ignored by git except .gitkeep)
│   ├── stills/                       # High-res PNG renders
│   └── loops/                        # 60 FPS MP4/WebM seamless video loops
├── scripts/                          # Blender Python automation utilities
│   ├── setup_workspace.py            # Workspace initializer
│   ├── setup_npr_cel_shader.py       # Master anime cel-shader generator
│   └── render_pipeline.py            # Headless still & loop rendering runner
└── docs/                             # Documentation and sourcing guides
    ├── 3D_MODEL_SOURCES.md           # Curated list of verified 3D anime repositories
    └── OPTIMIZATION_GUIDE.md         # Normal transfers, mesh culling, texture packing
```

---

## 4. Modeling, Shading & Rigging Rules

### 4.1 Unit Scale & Orientation
* **Scale**: 1 Blender Unit = 1.0 Meter. Normalize all imported characters to realistic anime proportions (typically 1.50m – 1.85m tall). Always apply scale (`Ctrl+A > Apply Scale`) before rigging or posing.
* **Front View**: Faces must point along the **-Y axis** (Standard Blender Front View = `NumPad 1`).

### 4.2 Cel-Shading (NPR) Standard
* **Do NOT use standard photorealistic Principled BSDF with specular sheen on anime faces.**
* Anime aesthetics require stepped color ramps via `Shader to RGB`:
  * **Base Tone**: Main skin/cloth color.
  * **Shadow Tone**: Slightly saturated, hue-shifted tint (e.g., warm peach shadow for skin, deep violet for dark clothes).
  * **Rim Light**: Sharp silhouette glow (Fresnel + Math Clamp) on the side facing the backlight.
* **Face Normal Smoothing**: To avoid awkward nose/cheek polygon shadow artifacts, apply a **Data Transfer Modifier** on the face mesh, transferring vertex normals from a smooth proxy sphere centered on the head.

### 4.3 Outlines
* Use either:
  1. **Inverted Hull**: Solidify modifier with negative thickness, flipped normals, and a black backface-culled material.
  2. **Grease Pencil Line Art**: Line Art modifier referencing the character collection.

---

## 5. Animation & Looping Protocol (Live Wallpaper)
* **Framerate**: Exactly **60 FPS**.
* **Loop Length**: Exactly **120 frames (2.0s)** or **240 frames (4.0s)**.
* **Seamlessness Rule**: Keyframe at Frame 1 must mathematically match Frame `End + 1`.
  * For cyclical motion (breathing, hair flutter), use sine-wave F-Curve modifiers (`Cycle`) or manually mirror keyframes.
* **Avoid Robot Stiffness**:
  * Utilize *Contrapposto* (weight distributed primarily to one foot, hips angled opposite to shoulders).
  * Always pose micro-expressions using facial blendshapes (slightly lower eyelids, asymmetric mouth, subtle brow lift).

---

## 6. Automation & Execution Guidelines
* Run headless Blender commands using:
  ```bash
  /Applications/Blender.app/Contents/MacOS/Blender -b scenes/master_composition.blend --python scripts/<script_name>.py
  ```
* For UI interaction, ensure the `blender_mcp` addon is active in the user's running Blender session.
* Always commit meaningful changes after each phase. Do not accumulate large batches of uncommitted files.
