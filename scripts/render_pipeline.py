#!/usr/bin/env python3
"""
scripts/render_pipeline.py
Automated headless render runner for 3D Anime Wallpaper project.

Usage:
  # Render 4K Ultra-HD Still Wallpaper:
  /Applications/Blender.app/Contents/MacOS/Blender -b scenes/master_composition.blend --python scripts/render_pipeline.py -- --still

  # Render 60 FPS Seamless Loop Live Wallpaper:
  /Applications/Blender.app/Contents/MacOS/Blender -b scenes/master_composition.blend --python scripts/render_pipeline.py -- --loop
"""

import sys
import os
import subprocess
import bpy

def render_still(output_path):
    print(f"\n[RENDER] Starting 4K Ultra-HD Still Wallpaper render...")
    scene = bpy.context.scene
    
    # Ensure stills output dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '16'  # 16-bit PNG for clean color gradations
    scene.render.filepath = output_path
    
    bpy.ops.render.render(write_still=True)
    print(f"[RENDER] Successfully rendered wallpaper still to:\n  {output_path}\n")

def render_loop(frames_dir, output_mp4, fps=60):
    print(f"\n[RENDER] Starting 60 FPS Seamless Loop render...")
    scene = bpy.context.scene
    
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)
    
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    scene.render.filepath = os.path.join(frames_dir, "frame_")
    
    print(f"[RENDER] Rendering frames {scene.frame_start} to {scene.frame_end} at {scene.render.resolution_x}x{scene.render.resolution_y}...")
    bpy.ops.render.render(animation=True)
    print(f"[RENDER] Frames completed. Encoding video with ffmpeg...")
    
    ffmpeg_bin = "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(ffmpeg_bin):
        ffmpeg_bin = "ffmpeg"
        
    cmd = [
        ffmpeg_bin, "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-c:v", "libx265",
        "-tag:v", "hvc1",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "slow",
        output_mp4
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[RENDER] Successfully encoded 60 FPS loop to:\n  {output_mp4}\n")
    else:
        print(f"[RENDER ERROR] ffmpeg encoding failed:\n{res.stderr}")

def main():
    # Parse custom arguments passed after '--'
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
    else:
        args = []
        
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if "--still" in args or not args:
        output_path = os.path.join(project_root, "renders", "stills", "wallpaper_4k.png")
        render_still(output_path)
    elif "--loop" in args:
        frames_dir = os.path.join(project_root, "renders", "loops", "frames")
        output_mp4 = os.path.join(project_root, "renders", "loops", "anime_wallpaper_live_60fps.mp4")
        render_loop(frames_dir, output_mp4)
    else:
        print(f"Unknown arguments: {args}. Specify --still or --loop.")

if __name__ == "__main__":
    main()
