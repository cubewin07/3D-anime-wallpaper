#!/usr/bin/env python3
"""
scripts/stage_studio_showcase.py
Professional 4K Static & 60 FPS Seamless Live Wallpaper Pipeline
Featuring Raiden Shogun & Hu Tao with custom EEVEE-Next NPR cel-shading,
3-point anime lighting, studio cyclorama, and micro-motion loops.
"""

import os
import math
import bpy

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_BLEND = os.path.join(PROJECT_ROOT, "scenes", "master_composition.blend")
STILL_OUTPUT_4K = os.path.join(PROJECT_ROOT, "renders", "stills", "studio_showcase_4k.png")
LOOP_OUTPUT_MP4 = os.path.join(PROJECT_ROOT, "renders", "loops", "studio_showcase_loop_60fps.mp4")

def clean_scene(scene):
    """Cleans previous objects except master collection setup."""
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam, do_unlink=True)
    for lgt in list(bpy.data.lights):
        bpy.data.lights.remove(lgt, do_unlink=True)

def setup_environment(scene):
    """Configures cinematic studio world and lighting rig."""
    # 1. World Background (Deep night indigo anime gradient)
    world = bpy.data.worlds.new("Anime_World")
    scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    
    node_out = wnodes.new('ShaderNodeOutputWorld')
    node_bg = wnodes.new('ShaderNodeBackground')
    node_bg.inputs['Color'].default_value = (0.012, 0.010, 0.022, 1.0) # Deep midnight navy
    node_bg.inputs['Strength'].default_value = 0.6
    wlinks.new(node_bg.outputs['Background'], node_out.inputs['Surface'])
    
    # 2. Seamless Curved Studio Cyclorama (Sweep floor into backdrop)
    bpy.ops.mesh.primitive_plane_add(size=16.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.active_object
    ground.name = "Studio_Cyclorama"
    
    # Add seamless curve material with atmospheric vignette
    mat_cyc = bpy.data.materials.new(name="MAT_Cyclorama")
    mat_cyc.use_nodes = True
    cnodes = mat_cyc.node_tree.nodes
    clinks = mat_cyc.node_tree.links
    cnodes.clear()
    
    c_out = cnodes.new('ShaderNodeOutputMaterial')
    c_emit = cnodes.new('ShaderNodeEmission')
    c_grad = cnodes.new('ShaderNodeTexGradient')
    c_grad.gradient_type = 'QUADRATIC_SPHERE'
    c_coord = cnodes.new('ShaderNodeTexCoord')
    c_map = cnodes.new('ShaderNodeMapping')
    c_map.inputs['Location'].default_value = (0.0, 0.3, 0.0)
    c_map.inputs['Scale'].default_value = (0.28, 0.28, 0.28)
    
    c_ramp = cnodes.new('ShaderNodeValToRGB')
    c_ramp.color_ramp.elements[0].position = 0.0
    c_ramp.color_ramp.elements[0].color = (0.12, 0.08, 0.20, 1.0) # Radiant anime twilight center
    c_ramp.color_ramp.elements[1].position = 0.75
    c_ramp.color_ramp.elements[1].color = (0.015, 0.010, 0.030, 1.0) # Deep midnight borders
    
    clinks.new(c_coord.outputs['Object'], c_map.inputs['Vector'])
    clinks.new(c_map.outputs['Vector'], c_grad.inputs['Vector'])
    clinks.new(c_grad.outputs['Fac'], c_ramp.inputs['Fac'])
    clinks.new(c_ramp.outputs['Color'], c_emit.inputs['Color'])
    c_emit.inputs['Strength'].default_value = 1.0
    clinks.new(c_emit.outputs['Emission'], c_out.inputs['Surface'])
    ground.data.materials.append(mat_cyc)
    ground.location = (0.0, 1.5, 0.0)
    ground.scale = (1.5, 1.5, 1.0)
    ground.rotation_euler = (math.radians(90.0), 0.0, 0.0)

    # 4. Three-Point Anime Lighting Rig
    # Key Light (Warm golden-peach sunlight)
    key_data = bpy.data.lights.new(name="LGT_Key", type='SUN')
    key_data.energy = 3.8
    key_data.color = (1.0, 0.95, 0.90)
    key_obj = bpy.data.objects.new(name="LGT_Key", object_data=key_data)
    scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(38.0), math.radians(18.0), math.radians(-32.0))

    # Fill Light (Cool ambient soft lilac)
    fill_data = bpy.data.lights.new(name="LGT_Fill", type='SUN')
    fill_data.energy = 1.4
    fill_data.color = (0.75, 0.78, 0.95)
    fill_obj = bpy.data.objects.new(name="LGT_Fill", object_data=fill_data)
    scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(-35.0), math.radians(-25.0), math.radians(125.0))

    # Rim Backlight (Vibrant violet/gold silhouette halo)
    rim_data = bpy.data.lights.new(name="LGT_Rim", type='SUN')
    rim_data.energy = 6.5
    rim_data.color = (0.95, 0.85, 1.0)
    rim_obj = bpy.data.objects.new(name="LGT_Rim", object_data=rim_data)
    scene.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (math.radians(-65.0), 0.0, math.radians(180.0))

def apply_anime_cel_shader(char_name, obj, textures_dir, shadow_tint=(0.65, 0.60, 0.72)):
    """Constructs professional stepped NPR cel-shading with channel-packed textures."""
    for slot in obj.material_slots:
        mat = bpy.data.materials.new(name=f"MAT_{char_name}_{slot.name}")
        slot.material = mat
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        node_out = nodes.new('ShaderNodeOutputMaterial')
        node_out.location = (800, 0)
        
        node_tex = nodes.new('ShaderNodeTexImage')
        node_tex.location = (-600, 0)
        
        mat_lower = slot.name.lower()
        is_face = ('face' in mat_lower or 'head' in mat_lower or 'eye' in mat_lower)
        is_hair = ('hair' in mat_lower)
        
        if is_face:
            tex_file = os.path.join(textures_dir, "Face_Diffuse.png")
        elif is_hair:
            tex_file = os.path.join(textures_dir, "Hair_Diffuse.png")
        else:
            tex_file = os.path.join(textures_dir, "Body_Diffuse.png")
            
        if os.path.exists(tex_file):
            img = bpy.data.images.load(tex_file, check_existing=True)
            # Crucial: CHANNEL_PACKED preserves unmasked diffuse RGB
            img.alpha_mode = 'CHANNEL_PACKED'
            node_tex.image = img
            
        if is_face:
            # Pristine Anime Face: unlit emission preserves clean illustrator line art
            node_emit = nodes.new('ShaderNodeEmission')
            node_emit.location = (400, 0)
            links.new(node_tex.outputs['Color'], node_emit.inputs['Color'])
            links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
        else:
            # Hair & Body: Stepped NPR Cel-Shading
            node_diffuse = nodes.new('ShaderNodeBsdfDiffuse')
            node_diffuse.location = (-400, -250)
            
            node_s2rgb = nodes.new('ShaderNodeShaderToRGB')
            node_s2rgb.location = (-200, -250)
            links.new(node_diffuse.outputs['BSDF'], node_s2rgb.inputs['Shader'])
            
            # Stepped 2-tone ColorRamp
            node_ramp = nodes.new('ShaderNodeValToRGB')
            node_ramp.location = (0, -250)
            node_ramp.color_ramp.interpolation = 'CONSTANT'
            # Shadow tone
            node_ramp.color_ramp.elements[0].position = 0.0
            node_ramp.color_ramp.elements[0].color = (*shadow_tint, 1.0)
            # Lit tone
            node_ramp.color_ramp.elements[1].position = 0.38
            node_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
            links.new(node_s2rgb.outputs['Color'], node_ramp.inputs['Fac'])
            
            # Multiply Texture with Cel Tone
            node_mult = nodes.new('ShaderNodeMix')
            node_mult.data_type = 'RGBA'
            node_mult.blend_type = 'MULTIPLY'
            node_mult.location = (200, 0)
            node_mult.inputs['Factor'].default_value = 1.0
            links.new(node_tex.outputs['Color'], node_mult.inputs[6])
            links.new(node_ramp.outputs['Color'], node_mult.inputs[7])
            
            # Subtle Rim Edge Glow
            node_fresnel = nodes.new('ShaderNodeFresnel')
            node_fresnel.location = (0, 200)
            node_fresnel.inputs['IOR'].default_value = 1.35
            
            node_step = nodes.new('ShaderNodeMath')
            node_step.operation = 'GREATER_THAN'
            node_step.inputs[1].default_value = 0.78
            node_step.location = (200, 200)
            links.new(node_fresnel.outputs['Fac'], node_step.inputs[0])
            
            node_rim_mix = nodes.new('ShaderNodeMix')
            node_rim_mix.data_type = 'RGBA'
            node_rim_mix.blend_type = 'ADD'
            node_rim_mix.location = (400, 0)
            links.new(node_step.outputs['Value'], node_rim_mix.inputs['Factor'])
            links.new(node_mult.outputs[2], node_rim_mix.inputs[6])
            node_rim_mix.inputs[7].default_value = (0.85, 0.80, 1.0, 1.0)
            
            node_emit = nodes.new('ShaderNodeEmission')
            node_emit.location = (600, 0)
            links.new(node_rim_mix.outputs[2], node_emit.inputs['Color'])
            links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])

def import_and_setup_character(fbx_path, tex_dir, char_name, target_height, world_x, rot_z_deg, shadow_tint):
    """Imports FBX, computes precise bounding box, normalizes scale & grounds character."""
    scene = bpy.context.scene
    before_objs = set(scene.objects)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    new_objs = set(scene.objects) - before_objs
    
    root = next((o for o in new_objs if o.parent is None), None)
    if not root:
        print(f"Warning: Root not found for {char_name}")
        return None
        
    root.name = f"Root_{char_name}"
    bpy.context.view_layer.update()
    
    # Calculate true mesh height across all meshes
    mesh_objs = [o for o in new_objs if o.type == 'MESH']
    all_z = [m.matrix_world @ v.co for m in mesh_objs for v in m.data.vertices]
    curr_h = max(v.z for v in all_z) - min(v.z for v in all_z)
    
    scale_factor = target_height / curr_h
    root.scale = (root.scale.x * scale_factor, root.scale.y * scale_factor, root.scale.z * scale_factor)
    root.rotation_euler.z = math.radians(rot_z_deg)
    root.location.x = world_x
    root.location.y = 0.0
    bpy.context.view_layer.update()
    
    # Re-ground feet precisely to Z = 0
    all_z = [m.matrix_world @ v.co for m in mesh_objs for v in m.data.vertices]
    z_min = min(v.z for v in all_z)
    root.location.z -= z_min
    bpy.context.view_layer.update()
    
    # Apply Cel-Shading Materials
    for obj in mesh_objs:
        apply_anime_cel_shader(char_name, obj, tex_dir, shadow_tint=shadow_tint)
        
    print(f"Loaded {char_name}: target_h={target_height}m, final_scale={root.scale}, loc={root.location}")
    return root

def setup_camera(scene):
    """Configures 4K wallpaper portrait camera with 50mm lens."""
    cam_data = bpy.data.cameras.new("Master_Camera")
    cam_data.lens = 50.0 # Clean portrait focal length
    cam_obj = bpy.data.objects.new("Master_Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # Position: Headroom for both characters and full upper body framing
    cam_obj.location = (0.0, -3.35, 1.05)
    cam_obj.rotation_euler = (math.radians(87.5), 0.0, 0.0)
    return cam_obj

def add_floating_particles(scene, count=35):
    """Adds subtle glowing ambient spirit particles."""
    part_mat = bpy.data.materials.new(name="MAT_Spirit_Mote")
    part_mat.use_nodes = True
    pnodes = part_mat.node_tree.nodes
    plinks = part_mat.node_tree.links
    pnodes.clear()
    p_out = pnodes.new('ShaderNodeOutputMaterial')
    p_emit = pnodes.new('ShaderNodeEmission')
    p_emit.inputs['Color'].default_value = (1.0, 0.85, 0.95, 1.0) # Radiant cherry blossom spark
    p_emit.inputs['Strength'].default_value = 5.0
    plinks.new(p_emit.outputs['Emission'], p_out.inputs['Surface'])
    
    import random
    random.seed(42)
    motes = []
    for i in range(count):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.012)
        mote = bpy.context.active_object
        mote.name = f"Spirit_Mote_{i:02d}"
        mote.data.materials.append(part_mat)
        
        # Distribute across framing
        rx = random.uniform(-1.6, 1.6)
        ry = random.uniform(-0.6, 0.8)
        rz = random.uniform(0.3, 2.1)
        mote.location = (rx, ry, rz)
        motes.append((mote, rx, ry, rz, random.uniform(0.1, 0.35)))
    return motes

def keyframe_seamless_loop(scene, root_raiden, root_hutao, cam_obj, motes, total_frames=120):
    """Sets up 60 FPS, 120-frame (2.0s) seamless live wallpaper loop with full character actions:
    Hu Tao waving her hand with bouncing pigtails & head tilt;
    Raiden Shogun in a poised regal stance with gaze shift, wind-rippling braid, and sleeve flutter.
    """
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.render.fps = 60
    
    # Locate character armatures
    arm_raiden = next((o for o in bpy.data.objects if o.type == 'ARMATURE' and 'shougun' in o.name.lower()), None)
    arm_hutao = next((o for o in bpy.data.objects if o.type == 'ARMATURE' and 'hutao' in o.name.lower()), None)
    
    # Configure XYZ rotation mode on all animated pose bones
    if arm_hutao:
        h_bones = [
            "Bip001 R UpperArm", "Bip001 R Forearm", "Bip001 R Hand",
            "Bip001 Head", "Bip001 Spine1",
            "+HairS L I01", "+HairS L I02", "+HairS L I03", "+HairS L I04", "+HairS L I05",
            "+HairS R I01", "+HairS R I02", "+HairS R I03", "+HairS R I04", "+HairS R I05"
        ]
        for bname in h_bones:
            pb = arm_hutao.pose.bones.get(bname)
            if pb:
                pb.rotation_mode = 'XYZ'
                
    if arm_raiden:
        r_bones = [
            "Bip001 R UpperArm", "Bip001 R Forearm", "Bip001 R Hand",
            "Bip001 L UpperArm", "Bip001 L Forearm", "Bip001 L Hand",
            "Bip001 Head", "Bip001 Spine1",
            "+HairB L B01", "+HairB L B02", "+HairB L B03", "+HairB L B04", "+HairB L B05", "+HairB L B06",
            "+SleeveB R A31", "+SleeveB R A32", "+SleeveB L A21", "+SleeveB L A22"
        ]
        for bname in r_bones:
            pb = arm_raiden.pose.bones.get(bname)
            if pb:
                pb.rotation_mode = 'XYZ'

    raiden_base_z = root_raiden.location.z
    hutao_base_z = root_hutao.location.z
    cam_base_x = cam_obj.location.x
    cam_base_z = cam_obj.location.z
    
    for f in range(1, total_frames + 1):
        scene.frame_set(f)
        phase = (f - 1) / total_frames
        angle = phase * 2.0 * math.pi
        
        # 1. ROOT BREATHING OSCILLATION
        root_raiden.location.z = raiden_base_z + math.sin(angle) * 0.004
        root_raiden.keyframe_insert(data_path="location", frame=f)
        
        root_hutao.location.z = hutao_base_z + math.sin(angle + (2.0 * math.pi / 3.0)) * 0.005
        root_hutao.keyframe_insert(data_path="location", frame=f)
        
        # 2. HU TAO: ENERGETIC ANIME HAND WAVE & GREETING ACTION
        if arm_hutao:
            # Wave frequency: 2 complete waves per 2.0s loop
            wave_angle = angle * 2.0
            
            # Right Upper Arm: Raised up into waving posture
            pb_u = arm_hutao.pose.bones.get("Bip001 R UpperArm")
            if pb_u:
                pb_u.rotation_euler = (
                    math.radians(-42.0 + math.sin(wave_angle) * 2.5),
                    math.radians(-28.0),
                    math.radians(-75.0 + math.cos(wave_angle) * 2.0)
                )
                pb_u.keyframe_insert(data_path="rotation_euler", frame=f)
                
            # Right Forearm: Bends up towards head and rocks side to side
            pb_f = arm_hutao.pose.bones.get("Bip001 R Forearm")
            if pb_f:
                pb_f.rotation_euler = (
                    math.radians(-20.0),
                    math.radians(58.0 + math.sin(wave_angle) * 10.0),
                    math.radians(math.cos(wave_angle) * 5.0)
                )
                pb_f.keyframe_insert(data_path="rotation_euler", frame=f)
                
            # Right Hand: Lively side-to-side hand waving motion
            pb_h = arm_hutao.pose.bones.get("Bip001 R Hand")
            if pb_h:
                pb_h.rotation_euler = (
                    math.radians(12.0 + math.sin(wave_angle) * 6.0),
                    math.radians(math.cos(wave_angle) * 8.0),
                    math.radians(25.0 + math.sin(wave_angle) * 28.0) # Prominent wave rotation!
                )
                pb_h.keyframe_insert(data_path="rotation_euler", frame=f)
                
            # Head: Cheerful tilt and nod
            pb_hd = arm_hutao.pose.bones.get("Bip001 Head")
            if pb_hd:
                pb_hd.rotation_euler = (
                    math.radians(6.0 + math.sin(wave_angle) * 2.5),
                    math.radians(-10.0 + math.cos(angle) * 3.5),
                    math.radians(-8.0 + math.sin(angle) * 3.0)
                )
                pb_hd.keyframe_insert(data_path="rotation_euler", frame=f)
                
            # Pigtails: Dynamic secondary hair bounce & flutter
            for i in range(1, 6):
                lag = i * 0.35
                sway = math.sin(wave_angle - lag) * (0.04 * i)
                p_left = arm_hutao.pose.bones.get(f"+HairS L I0{i}")
                p_right = arm_hutao.pose.bones.get(f"+HairS R I0{i}")
                if p_left:
                    p_left.rotation_euler = (sway, 0.0, sway * 0.5)
                    p_left.keyframe_insert(data_path="rotation_euler", frame=f)
                if p_right:
                    p_right.rotation_euler = (sway, 0.0, -sway * 0.5)
                    p_right.keyframe_insert(data_path="rotation_euler", frame=f)

        # 3. RAIDEN SHOGUN: REGAL ARCHON STANCE, GAZE SHIFT & BRAID WIND WAVE
        if arm_raiden:
            # Right Arm: Lowered naturally along right hip with gentle breathing sway
            pb_ru = arm_raiden.pose.bones.get("Bip001 R UpperArm")
            if pb_ru:
                pb_ru.rotation_euler = (
                    math.radians(-55.0 + math.sin(angle) * 1.5),
                    math.radians(10.0),
                    math.radians(25.0 + math.cos(angle) * 1.0)
                )
                pb_ru.keyframe_insert(data_path="rotation_euler", frame=f)
                
            # Left Arm: Lowered naturally along left hip with gentle breathing sway
            pb_lu = arm_raiden.pose.bones.get("Bip001 L UpperArm")
            if pb_lu:
                pb_lu.rotation_euler = (
                    math.radians(55.0 - math.sin(angle) * 1.5),
                    math.radians(-10.0),
                    math.radians(-25.0 - math.cos(angle) * 1.0)
                )
                pb_lu.keyframe_insert(data_path="rotation_euler", frame=f)
                
            # Head: Elegant regal head turn acknowledging Hu Tao and viewer
            pb_rh = arm_raiden.pose.bones.get("Bip001 Head")
            if pb_rh:
                pb_rh.rotation_euler = (
                    math.radians(3.0 + math.sin(angle) * 1.5),
                    math.radians(math.sin(angle) * 5.0), # Gentle gaze turn
                    math.radians(-3.0)
                )
                pb_rh.keyframe_insert(data_path="rotation_euler", frame=f)
                
            # Long Purple Braid: Cascading harmonic wind ripple across all 6 bones
            for i in range(1, 7):
                lag = i * 0.45
                sway_x = math.sin(angle - lag) * (0.05 * i)
                sway_y = math.cos(angle - lag) * (0.03 * i)
                pb_braid = arm_raiden.pose.bones.get(f"+HairB L B0{i}")
                if pb_braid:
                    pb_braid.rotation_euler = (sway_x, sway_y, 0.0)
                    pb_braid.keyframe_insert(data_path="rotation_euler", frame=f)
                    
            # Kimono Sleeves: Soft atmospheric breeze flutter
            for s_name in ["+SleeveB R A31", "+SleeveB R A32", "+SleeveB L A21", "+SleeveB L A22"]:
                pb_sleeve = arm_raiden.pose.bones.get(s_name)
                if pb_sleeve:
                    pb_sleeve.rotation_euler = (math.sin(angle * 1.5) * 0.03, 0.0, math.cos(angle * 1.5) * 0.02)
                    pb_sleeve.keyframe_insert(data_path="rotation_euler", frame=f)

        # 4. CAMERA CINEMATIC MICRO-FLOAT
        cam_obj.location.x = cam_base_x + math.sin(angle) * 0.010
        cam_obj.location.z = cam_base_z + math.sin(2.0 * angle) * 0.004
        cam_obj.keyframe_insert(data_path="location", frame=f)
        
        # 5. FLOATING SPIRIT PARTICLES
        for mote, ox, oy, oz, speed in motes:
            mote.location.z = oz + math.sin(angle + ox * 3.0) * speed * 0.1
            mote.location.x = ox + math.cos(angle + oy * 2.0) * 0.02
            mote.keyframe_insert(data_path="location", frame=f)

def run():
    print("=== Initializing Master Composition Scene ===")
    scene = bpy.context.scene
    clean_scene(scene)
    
    # Configure EEVEE-Next & Color Management
    scene.render.engine = 'BLENDER_EEVEE'
    scene.display_settings.display_device = 'sRGB'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'
    
    # 4K Resolution
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100
    
    # 1. Environment & Lighting
    setup_environment(scene)
    
    # 2. Import Raiden Shogun (1.72m on Left)
    raiden_fbx = os.path.join(PROJECT_ROOT, "characters", "raiden_shogun", "raw", "raiden_shogun.fbx")
    raiden_tex = os.path.join(PROJECT_ROOT, "characters", "raiden_shogun", "textures")
    root_raiden = import_and_setup_character(
        raiden_fbx, raiden_tex, "Raiden", 
        target_height=1.72, world_x=-0.46, rot_z_deg=8.0,
        shadow_tint=(0.60, 0.55, 0.70)
    )
    
    # 3. Import Hu Tao (1.56m on Right)
    hutao_fbx = os.path.join(PROJECT_ROOT, "characters", "hu_tao", "raw", "hu_tao.fbx")
    hutao_tex = os.path.join(PROJECT_ROOT, "characters", "hu_tao", "textures")
    root_hutao = import_and_setup_character(
        hutao_fbx, hutao_tex, "HuTao", 
        target_height=1.56, world_x=0.46, rot_z_deg=-10.0,
        shadow_tint=(0.65, 0.52, 0.55)
    )
    
    # 4. Camera & Composition
    cam_obj = setup_camera(scene)
    
    # 5. Atmospheric Spirit Particles
    motes = add_floating_particles(scene, count=32)
    
    # 6. Keyframe Seamless 60 FPS Loop
    keyframe_seamless_loop(scene, root_raiden, root_hutao, cam_obj, motes, total_frames=120)
    
    # 7. Save Master Composition Blend File
    os.makedirs(os.path.dirname(MASTER_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=MASTER_BLEND)
    print(f"=== Saved Master Scene: {MASTER_BLEND} ===")
    
    # 8. Render 4K Still
    os.makedirs(os.path.dirname(STILL_OUTPUT_4K), exist_ok=True)
    scene.frame_set(1)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = STILL_OUTPUT_4K
    print(f"=== Rendering 4K Wallpaper Still to {STILL_OUTPUT_4K} ===")
    bpy.ops.render.render(write_still=True)
    print(f"=== 4K Still Render Finished Successfully! ===")

    # 9. Render 60 FPS Seamless Live Video Loop
    import subprocess
    frames_dir = os.path.join(PROJECT_ROOT, "renders", "loops", "temp_frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    # 1080p 60 FPS for smooth live wallpaper playback
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.filepath = os.path.join(frames_dir, "frame_")
    
    print(f"=== Rendering 120 frames (60 FPS) to {frames_dir} ===")
    bpy.ops.render.render(animation=True)
    
    # Encode with FFmpeg
    ffmpeg_bin = "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(ffmpeg_bin):
        ffmpeg_bin = "ffmpeg"
        
    cmd = [
        ffmpeg_bin, "-y",
        "-framerate", "60",
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.2",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        LOOP_OUTPUT_MP4
    ]
    print(f"=== Encoding 60 FPS Seamless MP4 with FFmpeg: {' '.join(cmd)} ===")
    subprocess.run(cmd, check=True)
    print(f"=== Live Loop Render Finished Successfully: {LOOP_OUTPUT_MP4} ===")
    
    # Clean temporary frame files
    for f in os.listdir(frames_dir):
        if f.endswith(".png"):
            os.remove(os.path.join(frames_dir, f))
    os.rmdir(frames_dir)

if __name__ == "__main__":
    run()
