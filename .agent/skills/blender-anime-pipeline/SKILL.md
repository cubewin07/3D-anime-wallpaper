---
name: blender-anime-pipeline
description: Professional 3D anime character processing, NPR cel-shading, face normal smoothing, 60fps live loop keyframing, and headless EEVEE-Next rendering in Blender 5.2.
---

# Blender Anime Pipeline Skill

This skill equips agents with end-to-end workflows for importing, standardizing, shading, posing, and rendering 3D anime characters in **Blender 5.2.2 LTS** using **EEVEE-Next**.

---

## 1. Model Importing & Standardization

### 1.1 MMD (`.pmx`, `.pmd`) Models
Using the pre-installed `mmd_tools` addon:
```python
import bpy, addon_utils
addon_utils.enable('mmd_tools')

# Import PMX with clean defaults
bpy.ops.mmd_tools.import_model(
    filepath="path/to/character.pmx",
    scale=0.08,             # Standardize MMD 0.08 scale to real-world meters
    clean_model=True,       # Remove unused vertices and materials
    types={'MESH', 'ARMATURE', 'PHYSICS'}
)
```

### 1.2 VRM (`.vrm`) Models
Using the pre-installed `io_scene_vrm` addon:
```python
import bpy, addon_utils
addon_utils.enable('io_scene_vrm')

# Import VRM
bpy.ops.import_scene.vrm(
    filepath="path/to/character.vrm",
    extract_textures_into_folder=True,
    make_new_texture_folder=True
)
```

### 1.3 Height & Scale Normalization
Always measure and normalize the root armature:
- Canon heights:
  - Female characters: 1.50m – 1.68m
  - Male characters: 1.70m – 1.85m
- Apply scale immediately: `bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)`

---

## 2. NPR Anime Cel-Shading (EEVEE-Next)

Photorealistic shaders (standard Principled BSDF) ruin anime aesthetics. Always build stepped cel-shading node trees:

```
[Diffuse BSDF] ---> [Shader to RGB] ---> [ColorRamp (Stepped)] ---> [Mix Shader / Surface]
                                                |
                                        [Shadow Hue Shift]
```

### 2.1 Master Cel-Shading Node Setup (Python Recipe)
```python
import bpy

def create_anime_cel_material(mat_name, base_color=(0.95, 0.85, 0.8, 1.0), shadow_color=(0.85, 0.65, 0.65, 1.0)):
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # 1. Output
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (600, 0)
    
    # 2. Diffuse BSDF
    node_diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')
    node_diffuse.location = (-400, 0)
    
    # 3. Shader to RGB
    node_s2rgb = nodes.new(type='ShaderNodeShaderToRGB')
    node_s2rgb.location = (-200, 0)
    links.new(node_diffuse.outputs['BSDF'], node_s2rgb.inputs['Shader'])
    
    # 4. Stepped ColorRamp (Light & Shadow)
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.location = (0, 0)
    node_ramp.color_ramp.interpolation = 'CONSTANT'
    # Shadow stop (0.0)
    node_ramp.color_ramp.elements[0].position = 0.0
    node_ramp.color_ramp.elements[0].color = shadow_color
    # Light stop (0.45 threshold)
    node_ramp.color_ramp.elements[1].position = 0.45
    node_ramp.color_ramp.elements[1].color = base_color
    links.new(node_s2rgb.outputs['Color'], node_ramp.inputs['Fac'])
    
    # 5. Connect to Surface
    node_emit = nodes.new(type='ShaderNodeEmission')
    node_emit.location = (300, 0)
    links.new(node_ramp.outputs['Color'], node_emit.inputs['Color'])
    links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
    
    return mat
```

---

## 3. Face Normal Smoothing (Data Transfer)

Anime faces look ugly when 3D polygonal shading causes triangular shadows on the cheeks and nose. To fix this:

1. Spawn an invisible UV Sphere scaled to enclose the character's head.
2. Add a `DATA_TRANSFER` modifier to the face mesh.
3. Transfer **Face Corner Data > Custom Normals** from the proxy sphere.
4. Vertex group: Restrict the transfer strictly to the `Face_Skin` vertex group so hair and neck retain proper depth.

```python
def apply_face_normal_transfer(face_obj, proxy_sphere_obj, vertex_group_name="Face_Skin"):
    mod = face_obj.modifiers.new(name="Anime_Face_Normals", type='DATA_TRANSFER')
    mod.object = proxy_sphere_obj
    mod.use_loop_data = True
    mod.data_types_loops = {'CUSTOM_NORMAL'}
    mod.loop_mapping = 'NEAREST_POLYNOR'
    if vertex_group_name in face_obj.vertex_groups:
        mod.vertex_group = vertex_group_name
```

---

## 4. Inverted Hull Outlines

Clean ink outlines without relying on CPU-heavy post-processing:

1. Add a `SOLIDIFY` modifier to the mesh.
2. Set `Thickness` to negative (e.g., `-0.003` to `-0.005`).
3. Check `Normals > Flip`.
4. Set `Material Index Offset` to point to a pure black emission material with **Backface Culling enabled**.

---

## 5. 60 FPS Seamless Live Wallpaper Looping

### 5.1 Golden Rules of Looping
* **Framerate**: 60 FPS.
* **Length**: 120 frames (2 seconds) or 240 frames (4 seconds).
* **Boundary Condition**: Values at Frame 1 must equal Frame `End + 1`.

### 5.2 Breathing Sine Wave Formula
Animate the `Chest` or `Spine2` bone:
```python
import math

def keyframe_breathing_loop(bone, start_frame=1, end_frame=120):
    for f in range(start_frame, end_frame + 1):
        # Progress 0.0 to 1.0 across loop
        t = (f - start_frame) / (end_frame - start_frame)
        # Sine cycle
        scale_y = 1.0 + 0.02 * math.sin(t * 2 * math.pi)
        bone.scale = (1.0, scale_y, 1.0)
        bone.keyframe_insert(data_path="scale", frame=f)
```

### 5.3 Eye Blink Animation
- Frame 1 to 40: Eyes open (`shape_key.value = 0.0`).
- Frame 45: Eyes half closed (`0.5`).
- Frame 48: Eyes fully closed (`1.0`).
- Frame 51: Eyes half open (`0.5`).
- Frame 55 to 120: Eyes open (`0.0`).

---

## 6. Rendering & Video Encoding

### High-Res Still Render
```bash
/Applications/Blender.app/Contents/MacOS/Blender -b scenes/master_composition.blend \
  -o "//../renders/stills/wallpaper_4k_" -F PNG -f 1
```

### 60 FPS Seamless Video Loop Render
```bash
/Applications/Blender.app/Contents/MacOS/Blender -b scenes/master_composition.blend \
  -s 1 -e 120 -a
```

Encode with `ffmpeg` into hardware-accelerated H.265 (HEVC):
```bash
ffmpeg -y -framerate 60 -i renders/loops/frame_%04d.png \
  -c:v libx265 -tag:v hvc1 -pix_fmt yuv420p -crf 18 \
  renders/loops/anime_wallpaper_live_60fps.mp4
```
