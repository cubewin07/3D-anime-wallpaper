#!/usr/bin/env python3
"""
scripts/setup_workspace.py
Initializes the master composition scene for the 3D Anime Wallpaper project in Blender 5.2.2.
Sets up:
- EEVEE-Next engine with high-quality anime settings
- Standard color management for vibrant 2D cel colors
- 4K resolution (3840x2160) at 60 FPS
- 120-frame seamless loop range
- Cinematic 3-point anime lighting rig (Key, Fill, Rim)
- Front-facing camera rig
- Saves to scenes/master_composition.blend
"""

import os
import math
import bpy

def setup_scene():
    print("=== Initializing 3D Anime Wallpaper Master Scene ===")
    
    # Reset to factory default state
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    scene = bpy.context.scene
    
    # 1. Engine & Quality Settings
    scene.render.engine = 'BLENDER_EEVEE'
    
    # Color Management for Anime
    try:
        scene.view_settings.view_transform = 'Standard'
        scene.view_settings.look = 'Medium High Contrast'
    except Exception as e:
        print(f"Color management note: {e}")
        
    # Resolution: 4K Ultra-HD
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100
    
    # Framerate & Loop Range (60 FPS, 120 frames = 2.0s seamless loop)
    scene.render.fps = 60
    scene.frame_start = 1
    scene.frame_end = 120
    scene.frame_current = 1
    
    # 2. Camera Rig
    cam_data = bpy.data.cameras.new(name="CAM_Wallpaper")
    cam_data.lens = 50  # 50mm cinematic portrait/lineup lens
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    
    cam_obj = bpy.data.objects.new(name="CAM_Wallpaper", object_data=cam_data)
    # Position: Centered on X, back along -Y, eye-level at Z=1.35m
    cam_obj.location = (0.0, -4.2, 1.35)
    cam_obj.rotation_euler = (math.radians(88.0), 0.0, 0.0)
    
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # 3. 3-Point Anime Lighting Rig
    light_collection = bpy.data.collections.new("Lighting_Rig")
    scene.collection.children.link(light_collection)
    
    # Key Light (Warm Sunlight, Front-Left 45 degrees)
    key_data = bpy.data.lights.new(name="LGT_Key", type='SUN')
    key_data.energy = 3.5
    key_data.color = (1.0, 0.95, 0.88)  # Warm sunlight
    key_obj = bpy.data.objects.new(name="LGT_Key", object_data=key_data)
    key_obj.rotation_euler = (math.radians(45.0), math.radians(20.0), math.radians(-35.0))
    light_collection.objects.link(key_obj)
    
    # Fill Light (Cool Sky Shadow Fill, Front-Right)
    fill_data = bpy.data.lights.new(name="LGT_Fill", type='SUN')
    fill_data.energy = 1.2
    fill_data.color = (0.85, 0.90, 1.0)  # Cool sky tint
    fill_obj = bpy.data.objects.new(name="LGT_Fill", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(50.0), math.radians(-25.0), math.radians(45.0))
    light_collection.objects.link(fill_obj)
    
    # Rim Light (Contre-Jour Backlight for Crisp Anime Silhouette Glow)
    rim_data = bpy.data.lights.new(name="LGT_Rim", type='SUN')
    rim_data.energy = 5.0
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new(name="LGT_Rim", object_data=rim_data)
    rim_obj.rotation_euler = (math.radians(-40.0), math.radians(10.0), math.radians(160.0))
    light_collection.objects.link(rim_obj)
    
    # 4. Character Collection Anchor
    char_collection = bpy.data.collections.new("Characters")
    scene.collection.children.link(char_collection)
    
    # 5. Save Master File
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scenes_dir = os.path.join(project_root, "scenes")
    os.makedirs(scenes_dir, exist_ok=True)
    master_file = os.path.join(scenes_dir, "master_composition.blend")
    
    bpy.ops.wm.save_as_mainfile(filepath=master_file)
    print(f"=== Successfully saved master composition to: {master_file} ===")

if __name__ == "__main__":
    setup_scene()
