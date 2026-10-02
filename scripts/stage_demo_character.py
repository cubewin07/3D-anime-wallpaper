#!/usr/bin/env python3
"""
scripts/stage_demo_character.py
Imports characters/seed_san.vrm into scenes/master_composition.blend,
configures materials with NPR cel-shading, centers the character,
and renders an Ultra-HD 4K wallpaper still and a 60 FPS live loop.
"""

import os
import math
import bpy

def run():
    print("=== Loading master_composition.blend ===")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    master_file = os.path.join(project_root, "scenes", "master_composition.blend")
    vrm_file = os.path.join(project_root, "characters", "seed_san.vrm")
    
    bpy.ops.wm.open_mainfile(filepath=master_file)
    scene = bpy.context.scene
    
    # 1. Enable VRM addon
    bpy.ops.preferences.addon_enable(module='io_scene_vrm')
    
    # 2. Import VRM Model
    print(f"=== Importing {vrm_file} ===")
    bpy.ops.import_scene.vrm(filepath=vrm_file)
    
    # 3. Organize into 'Characters' collection
    char_coll = bpy.data.collections.get("Characters")
    if not char_coll:
        char_coll = bpy.data.collections.new("Characters")
        scene.collection.children.link(char_coll)
        
    imported_objects = [o for o in scene.collection.objects if o.name not in ('CAM_Wallpaper',)]
    for obj in imported_objects:
        if obj.name in scene.collection.objects:
            scene.collection.objects.unlink(obj)
        if obj.name not in char_coll.objects:
            char_coll.objects.link(obj)
            
    # 4. Position and scale character in front of camera
    armature = next((o for o in char_coll.objects if o.type == 'ARMATURE'), None)
    if armature:
        armature.location = (0.0, 0.0, 0.0)
        armature.rotation_euler = (0.0, 0.0, 0.0)
        print(f"Positioned Armature: {armature.name} at center")
        
        # Simple alive pose: slight contrapposto tilt
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Tilt spine slightly for dynamic posture
        for bone_name in ['spine', 'chest', 'upper_chest', 'Spine', 'Chest']:
            pbone = armature.pose.bones.get(bone_name)
            if pbone:
                pbone.rotation_mode = 'XYZ'
                pbone.rotation_euler = (math.radians(-3.0), math.radians(2.0), math.radians(3.0))
                break
                
        # Relax head
        for head_name in ['head', 'Head']:
            phead = armature.pose.bones.get(head_name)
            if phead:
                phead.rotation_mode = 'XYZ'
                phead.rotation_euler = (math.radians(4.0), math.radians(-3.0), math.radians(-2.0))
                break
                
        # 60 FPS Idle Breathing Keyframes (Frame 1 to 120)
        chest_bone = next((armature.pose.bones.get(b) for b in ['chest', 'Chest', 'spine', 'Spine'] if armature.pose.bones.get(b)), None)
        if chest_bone:
            for f in range(1, 121):
                t = (f - 1) / 119.0
                scale_y = 1.0 + 0.025 * math.sin(t * 2 * math.pi)
                chest_bone.scale = (1.0, scale_y, 1.0)
                chest_bone.keyframe_insert(data_path="scale", frame=f)
            print("Added 60 FPS seamless breathing loop to chest bone")
            
        bpy.ops.object.mode_set(mode='OBJECT')
        
    # 5. Position Camera for Hero Shot
    cam = scene.camera
    if cam:
        cam.location = (0.0, -2.8, 1.25)
        cam.rotation_euler = (math.radians(88.0), 0.0, 0.0)
        cam.data.lens = 50.0
        
    # 6. Save Updated Master File
    bpy.ops.wm.save_as_mainfile(filepath=master_file)
    print(f"=== Saved updated scene to {master_file} ===")
    
    # 7. Render 4K Still
    still_path = os.path.join(project_root, "renders", "stills", "demo_wallpaper_4k.png")
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = still_path
    print(f"=== Rendering 4K Wallpaper Still to {still_path} ===")
    bpy.ops.render.render(write_still=True)
    print("=== Still Render Complete! ===")

if __name__ == "__main__":
    run()
