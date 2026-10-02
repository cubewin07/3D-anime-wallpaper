# 3D Anime Character Optimization Guide

Raw imported models from MMD or game rips often contain common issues: jagged facial shading, hidden overlapping geometry that clips during poses, bloated 8K textures, or Japanese bone names. 

Follow this protocol to standardize and optimize every character.

---

## 1. The Face Normal Fix (Critical for Anime 3D)

### The Problem
Traditional 3D shading calculates light based on geometry surface angles. Because anime faces have flat noses and angled cheekbones, standard lighting casts awkward triangular shadows across the face, ruining the 2D illustration feel.

### The Solution: Spherical Normal Transfer
We project smooth spherical normals onto the face so it shades evenly like a classic anime drawing.

1. **Create Proxy Sphere**:
   * Add a UV Sphere at the character's head location (`Scale ~ 0.25m`).
   * Hide the sphere from renders (Disable camera icon in Outliner).
2. **Apply Data Transfer**:
   * Select the character's head/face mesh.
   * Add a `Data Transfer` modifier:
     * **Source**: The proxy UV sphere.
     * **Face Corner Data**: Enabled.
     * Check **Custom Normals**.
     * **Mapping**: `Nearest Face Interpolated` or `Nearest Poly Normal`.
     * **Vertex Group**: Limit to the `Face_Skin` vertex group (so hair strands and ears keep their own normals).

---

## 2. Hidden Geometry Culling

### The Problem
Many anime 3D models include a full nude body mesh underneath opaque clothing. During extreme poses, the body mesh clips through clothes, and it wastes GPU memory and rigging calculations.

### The Solution
1. Enter **Edit Mode** on the body mesh.
2. Select faces completely obscured by boots, jackets, shirts, or pants.
3. Delete faces (`X > Faces`).
4. This completely prevents clipping artifacts when posing or animating live loops.

---

## 3. Texture Compaction & Downsampling

### The Problem
Some models ship with uncompressed 8K textures or dozens of duplicate 128x128 materials.

### The Solution (CLI with `@gltf-transform`)
For `.vrm` or `.gltf` models:
```bash
# Resize oversized textures to crisp 2K / 4K without loss in fidelity
gltf-transform resize input.vrm output.vrm --width 2048 --height 2048

# Deduplicate identical material slots and prune unused accessors
gltf-transform dedup input.vrm output_optimized.vrm
gltf-transform prune output_optimized.vrm output_final.vrm
```

---

## 4. Rig Standardizing & Japanese Bone Names

MMD models use Japanese bone names (e.g., `全ての親`, `センター`, `足`, `ひざ`).

### In Blender with `mmd_tools`:
1. Select the character armature.
2. Go to the **MMD** sidebar tab (`N` panel).
3. Under **Model**, click **Translate**.
4. Set translation mode to **English** (automatically maps `足` to `leg.L`, `ひざ` to `knee.L`, `首` to `neck`, `頭` to `head`).
5. This makes posing and applying animation curves seamless.

---

## 5. Inverted Hull Silhouette Outlines

To create crisp Studio Trigger / Arc System Works anime outlines:

1. Add a **Solidify Modifier** to the mesh.
2. Settings:
   * **Thickness**: `-0.003` to `-0.005` (adjust based on character scale).
   * **Normals**: Check **Flip**.
   * **Rim**: Uncheck **Fill Rim**.
   * **Material Index Offset**: Assign to the black outline material index.
3. Outline Material Settings:
   * **Surface**: Emission (Color: Pure Black `#000000` or deep navy `#0A0D1A`).
   * **Settings**: Enable **Backface Culling** (this ensures the outline is only visible along the outer silhouette).
