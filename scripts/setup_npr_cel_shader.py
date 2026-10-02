#!/usr/bin/env python3
"""
scripts/setup_npr_cel_shader.py
Constructs a modular EEVEE-Next Anime NPR (Non-Photorealistic Rendering) Cel-Shading Node Group.
Saves the node group and template materials into shaders/anime_npr_shaders.blend.
"""

import os
import bpy

def build_npr_node_group():
    group_name = "NPR_Anime_Cel_Shader"
    
    # Check if group already exists
    if group_name in bpy.data.node_groups:
        return bpy.data.node_groups[group_name]
    
    ng = bpy.data.node_groups.new(name=group_name, type='ShaderNodeTree')
    nodes = ng.nodes
    links = ng.links
    nodes.clear()
    
    # Node Group Interface (Inputs & Outputs)
    # Blender 4.0+ uses interface sockets
    tree_inputs = ng.interface
    
    tree_inputs.new_socket(name="Base Color", in_out='INPUT', socket_type='NodeSocketColor')
    tree_inputs.items_tree[-1].default_value = (0.95, 0.82, 0.75, 1.0)
    
    tree_inputs.new_socket(name="Shadow Color", in_out='INPUT', socket_type='NodeSocketColor')
    tree_inputs.items_tree[-1].default_value = (0.85, 0.60, 0.60, 1.0)
    
    tree_inputs.new_socket(name="Shadow Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
    tree_inputs.items_tree[-1].default_value = 0.45
    tree_inputs.items_tree[-1].min_value = 0.0
    tree_inputs.items_tree[-1].max_value = 1.0
    
    tree_inputs.new_socket(name="Rim Color", in_out='INPUT', socket_type='NodeSocketColor')
    tree_inputs.items_tree[-1].default_value = (1.0, 0.95, 0.9, 1.0)
    
    tree_inputs.new_socket(name="Rim Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    tree_inputs.items_tree[-1].default_value = 1.5
    
    tree_inputs.new_socket(name="Shader", in_out='OUTPUT', socket_type='NodeSocketShader')
    
    # Nodes Inside Group
    node_in = nodes.new('NodeGroupInput')
    node_in.location = (-600, 0)
    
    node_out = nodes.new('NodeGroupOutput')
    node_out.location = (800, 0)
    
    # 1. Diffuse Light Sampling
    node_diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    node_diffuse.location = (-400, 100)
    
    node_s2rgb = nodes.new('ShaderNodeShaderToRGB')
    node_s2rgb.location = (-200, 100)
    links.new(node_diffuse.outputs['BSDF'], node_s2rgb.inputs['Shader'])
    
    # 2. Stepped Cel Cutoff (Math: Greater Than)
    node_step = nodes.new('ShaderNodeMath')
    node_step.operation = 'GREATER_THAN'
    node_step.location = (50, 100)
    links.new(node_s2rgb.outputs['Color'], node_step.inputs[0])
    links.new(node_in.outputs['Shadow Threshold'], node_step.inputs[1])
    
    # 3. Mix Base Color and Shadow Color
    node_mix_color = nodes.new('ShaderNodeMix')
    node_mix_color.data_type = 'RGBA'
    node_mix_color.location = (250, 100)
    links.new(node_step.outputs['Value'], node_mix_color.inputs['Factor'])
    links.new(node_in.outputs['Shadow Color'], node_mix_color.inputs[6])  # Color A (Shadow)
    links.new(node_in.outputs['Base Color'], node_mix_color.inputs[7])    # Color B (Lit)
    
    # 4. Rim Light via Fresnel / Layer Weight
    node_layer_weight = nodes.new('ShaderNodeLayerWeight')
    node_layer_weight.location = (-200, -200)
    node_layer_weight.inputs['Blend'].default_value = 0.3
    
    node_rim_step = nodes.new('ShaderNodeMath')
    node_rim_step.operation = 'GREATER_THAN'
    node_rim_step.inputs[1].default_value = 0.65
    node_rim_step.location = (50, -200)
    links.new(node_layer_weight.outputs['Fresnel'], node_rim_step.inputs[0])
    
    # 5. Composite Final Color with Rim
    node_add_rim = nodes.new('ShaderNodeMix')
    node_add_rim.data_type = 'RGBA'
    node_add_rim.blend_type = 'ADD'
    node_add_rim.location = (450, 50)
    links.new(node_rim_step.outputs['Value'], node_add_rim.inputs['Factor'])
    links.new(node_mix_color.outputs[2], node_add_rim.inputs[6])          # Base + Shadow
    links.new(node_in.outputs['Rim Color'], node_add_rim.inputs[7])       # Rim Glow
    
    # 6. Surface Output via Emission (Ensures crisp 2D look without muddy indirect bounces)
    node_emit = nodes.new('ShaderNodeEmission')
    node_emit.location = (650, 0)
    links.new(node_add_rim.outputs[2], node_emit.inputs['Color'])
    links.new(node_emit.outputs['Emission'], node_out.inputs['Shader'])
    
    print(f"Created Node Group: {group_name}")
    return ng

def create_sample_materials(ng):
    # Material 1: Anime Skin
    mat_skin = bpy.data.materials.new(name="MAT_Anime_Skin")
    mat_skin.use_nodes = True
    skin_nodes = mat_skin.node_tree.nodes
    skin_links = mat_skin.node_tree.links
    skin_nodes.clear()
    
    skin_group = skin_nodes.new('ShaderNodeGroup')
    skin_group.node_tree = ng
    skin_group.location = (0, 0)
    skin_group.inputs['Base Color'].default_value = (0.97, 0.88, 0.82, 1.0)
    skin_group.inputs['Shadow Color'].default_value = (0.88, 0.68, 0.68, 1.0)
    skin_group.inputs['Shadow Threshold'].default_value = 0.42
    
    skin_out = skin_nodes.new('ShaderNodeOutputMaterial')
    skin_out.location = (300, 0)
    skin_links.new(skin_group.outputs['Shader'], skin_out.inputs['Surface'])
    
    # Material 2: Inverted Hull Black Outline
    mat_outline = bpy.data.materials.new(name="MAT_Anime_Outline")
    mat_outline.use_nodes = True
    # In Blender 5.2/EEVEE, backface culling is configured on material
    try:
        mat_outline.use_backface_culling = True
    except Exception:
        pass
    out_nodes = mat_outline.node_tree.nodes
    out_links = mat_outline.node_tree.links
    out_nodes.clear()
    
    emit_node = out_nodes.new('ShaderNodeEmission')
    emit_node.inputs['Color'].default_value = (0.02, 0.02, 0.04, 1.0)  # Deep dark ink
    emit_node.location = (0, 0)
    
    mat_out = out_nodes.new('ShaderNodeOutputMaterial')
    mat_out.location = (300, 0)
    out_links.new(emit_node.outputs['Emission'], mat_out.inputs['Surface'])
    
    print("Created template materials: MAT_Anime_Skin, MAT_Anime_Outline")

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ng = build_npr_node_group()
    create_sample_materials(ng)
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shaders_dir = os.path.join(project_root, "shaders")
    os.makedirs(shaders_dir, exist_ok=True)
    shader_blend_file = os.path.join(shaders_dir, "anime_npr_shaders.blend")
    
    bpy.ops.wm.save_as_mainfile(filepath=shader_blend_file)
    print(f"=== Saved NPR Cel-Shader library to: {shader_blend_file} ===")

if __name__ == "__main__":
    main()
